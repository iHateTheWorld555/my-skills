#!/usr/bin/env python3
"""Scan Python source for this skill's forbidden anti-patterns; exit 1 if any."""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Finding:
    path: str
    line: int
    severity: str
    rule: str
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: [{self.severity}] {self.rule}: {self.message}"


SEVERITY_ORDER = {"P0-BLOCKER": 0, "P1-PERF": 1, "P2-MAINTAIN": 2, "P3-STYLE": 3}

CJK = re.compile(r"[一-鿿㐀-䶿]")

CODE_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (
        re.compile(r"^\s*except\s*:\s*$"),
        "P0-BLOCKER",
        "no-bare-except",
        "bare except; catch specific exceptions",
    ),
    (
        re.compile(r"^\s*except\s+(Exception|BaseException)\b.*:\s*(#.*)?$"),
        "P0-BLOCKER",
        "broad-except",
        "broad except; narrow it, or log a reason and re-raise",
    ),
    (
        re.compile(r"^\s*except\b.*:\s*(pass|\.\.\.)\s*$"),
        "P0-BLOCKER",
        "except-pass",
        "except swallows the error; that is debt, not safety",
    ),
    (
        re.compile(r"\b(getattr|setattr|hasattr)\s*\("),
        "P3-STYLE",
        "no-dynamic-attributes",
        "dynamic attribute access; read the field directly and let it fail loudly",
    ),
    (
        re.compile(r"\b\d+\.\d{7,}\b"),
        "P2-MAINTAIN",
        "unexplained-precise-literal",
        "suspiciously precise float literal; name it and note where it came from",
    ),
]

RAW_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (
        re.compile(
            r"""\b(?:logger?|logging)\s*\.\s*\w+\([^)]*?["']\s*\[(Info|Warn|Warning|Error|Debug|step\s*\d+)"""
        ),
        "P3-STYLE",
        "no-log-prefix",
        "manual log prefix; the level field already says it",
    ),
    (
        re.compile(r"""\bprint\([^)]*?["']\s*\[(Info|Warn|Warning|Error|Debug|step\s*\d+)"""),
        "P3-STYLE",
        "no-log-prefix",
        "manual log prefix; the level field already says it",
    ),
]

COMMENT_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (
        re.compile(r"`"),
        "P3-STYLE",
        "no-backticks",
        "comments and docstrings must not contain backticks (`)",
    ),
    (
        re.compile(r"^#\s*(★|☆)"),
        "P3-STYLE",
        "no-process-marker",
        "star marker in comment; process markers are noise",
    ),
    (
        re.compile(r"^#\s*\[?(P[0-4]|FIX|FIXME|HACK|XXX)\]?\b"),
        "P3-STYLE",
        "no-process-marker",
        "priority/fix marker in comment; that belongs in the issue tracker",
    ),
    (
        re.compile(r"(?:={8,}|-{8,}|\*{8,})"),
        "P3-STYLE",
        "no-section-banner",
        "decorative section banner; drop it or split the file",
    ),
    (
        re.compile(r"#\s*TODO\b(?!(?s:.*?)(?:#\d+|[A-Z]{2,}-\d+))"),
        "P3-STYLE",
        "todo-without-ticket",
        "TODO without a ticket reference",
    ),
    (
        re.compile(r"\b(upstream|closed[- ]source)\b"),
        "P3-STYLE",
        "no-provenance-leak",
        "provenance leakage; name the constraint, not the other repo",
    ),
]

# Rule name -> the canonical explanation, kept in sync with the style guide.
RULE_ORDER = ("P0-BLOCKER", "P1-PERF", "P2-MAINTAIN", "P3-STYLE")



@dataclass
class SourceFacts:
    """Everything the checks need, extracted once."""

    source: str
    path: str
    lines: list[str]
    comments: list[tuple[int, str]]
    docstrings: list[tuple[int, str, int]]  # (lineno, text, line_count)
    tree: ast.Module | None
    syntax_error: SyntaxError | None
    import_lines: dict[int, int]  # line -> nesting depth (0 = module level)
    type_checking_lines: dict[int, int]  # line -> nesting depth


def collect(path: str, source: str) -> SourceFacts:
    lines = source.splitlines()
    comments: list[tuple[int, str]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                comments.append((tok.start[0], tok.string))
    except (tokenize.TokenError, IndentationError):
        pass

    tree: ast.Module | None = None
    syntax_error: SyntaxError | None = None
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        syntax_error = exc

    docstrings: list[tuple[int, str, int]] = []
    import_lines: dict[int, int] = {}
    type_checking_lines: dict[int, int] = {}

    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.body:
                    first = node.body[0]
                    if (
                        isinstance(first, ast.Expr)
                        and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)
                    ):
                        text = first.value.value
                        docstrings.append((first.value.lineno, text, len(text.splitlines())))

        # nesting depth of every import / TYPE_CHECKING guard
        def walk(node: ast.AST, depth: int) -> None:
            for child in ast.iter_child_nodes(node):
                child_depth = depth
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    child_depth = depth + 1
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    import_lines[child.lineno] = depth
                if isinstance(child, ast.If):
                    test = child.test
                    name = None
                    if isinstance(test, ast.Name):
                        name = test.id
                    elif isinstance(test, ast.Attribute):
                        name = test.attr
                    if name == "TYPE_CHECKING":
                        type_checking_lines[child.lineno] = depth
                walk(child, child_depth)

        walk(tree, 0)

    return SourceFacts(
        source=source,
        path=path,
        lines=lines,
        comments=comments,
        docstrings=docstrings,
        tree=tree,
        syntax_error=syntax_error,
        import_lines=import_lines,
        type_checking_lines=type_checking_lines,
    )



def check_lines(facts: SourceFacts) -> list[Finding]:
    out: list[Finding] = []
    for lineno, text in enumerate(facts.lines, 1):
        code = strip_strings(text)
        for pattern, severity, rule, message in CODE_RULES:
            if pattern.search(code):
                out.append(Finding(facts.path, lineno, severity, rule, message))
        for pattern, severity, rule, message in RAW_RULES:
            if pattern.search(text):
                out.append(Finding(facts.path, lineno, severity, rule, message))

    for lineno, text in facts.comments:
        for pattern, severity, rule, message in COMMENT_RULES:
            if pattern.search(text):
                out.append(Finding(facts.path, lineno, severity, rule, message))
        if CJK.search(text):
            out.append(Finding(facts.path, lineno, "P3-STYLE", "no-chinese", "Chinese text in a comment"))
    return out


_TRIPLE_D = '"""'
_TRIPLE_S = "'''"
_STRING_RE = re.compile(
    r"(?:[rbfu]{0,2})("
    + _TRIPLE_D
    + r".*?"
    + _TRIPLE_D
    + r"|"
    + _TRIPLE_S
    + r".*?"
    + _TRIPLE_S
    + r'|"[^"\n]*"|\'[^\'\n]*\')',
    re.DOTALL,
)


def strip_strings(line: str) -> str:
    """Blank out string literals so code rules don't fire on their contents."""
    return _STRING_RE.sub(lambda m: '"' * len(m.group(0)), line)


def check_docstrings(facts: SourceFacts) -> list[Finding]:
    out: list[Finding] = []
    for lineno, text, line_count in facts.docstrings:
        if "`" in text:
            out.append(
                Finding(facts.path, lineno, "P3-STYLE", "no-backticks", "docstring contains backticks (`)")
            )
        if CJK.search(text):
            out.append(Finding(facts.path, lineno, "P3-STYLE", "no-chinese", "Chinese text in a docstring"))
        if line_count > 12:
            out.append(
                Finding(
                    facts.path,
                    lineno,
                    "P3-STYLE",
                    "long-docstring",
                    f"docstring is {line_count} lines; keep docstrings to 1-3 lines",
                )
            )
    return out


def check_file_header_comment(facts: SourceFacts) -> list[Finding]:
    """The style guide forbids comments at the top of a file."""
    if facts.tree is None:
        return []
    first_stmt = min(
        (n.lineno for n in facts.tree.body if not isinstance(n, ast.Expr)),
        default=None,
    )
    if first_stmt is None:
        return []
    heading = [c for c in facts.comments if c[0] < first_stmt and not c[1].startswith("#!")]
    if not heading:
        return []
    # one finding per contiguous block, anchored at the first comment
    lines = sorted(c[0] for c in heading)
    return [
        Finding(
            facts.path,
            lines[0],
            "P3-STYLE",
            "no-file-header-comment",
            f"{len(lines)} comment line(s) above the first statement; "
            "the style guide forbids file header comments",
        )
    ]


def check_imports(facts: SourceFacts) -> list[Finding]:
    """Function-local imports, and TYPE_CHECKING used to dodge the linter."""
    out: list[Finding] = []
    for lineno, depth in sorted(facts.import_lines.items()):
        if depth > 0:
            out.append(
                Finding(
                    facts.path,
                    lineno,
                    "P3-STYLE",
                    "lazy-import",
                    "function-local import; move it to the top of the file unless it is a "
                    "heavy optional dependency or a documented circular-dependency break",
                )
            )
    for lineno, depth in sorted(facts.type_checking_lines.items()):
        if depth > 0:
            out.append(
                Finding(
                    facts.path,
                    lineno,
                    "P3-STYLE",
                    "type-checking-in-function",
                    "TYPE_CHECKING guard inside a function; import at module scope",
                )
            )
        else:
            out.append(
                Finding(
                    facts.path,
                    lineno,
                    "P3-STYLE",
                    "type-checking-guard",
                    "TYPE_CHECKING guard: legitimate only for a genuine type-level circular "
                    "import. If the import would work at module scope, put it there",
                )
            )
    return out


DUNDER = re.compile(r"^__\w+__$")


def check_functions(facts: SourceFacts) -> list[Finding]:
    """Single-use private helpers, mutable defaults, parameter deletion, try width."""
    if facts.tree is None:
        return []
    out: list[Finding] = []

    funcs = [n for n in ast.walk(facts.tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(facts.tree) if isinstance(n, ast.ClassDef)]

    # private names at module / class scope (nested functions keep their _)
    for node in facts.tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_") and not DUNDER.match(node.name):
                out.append(
                    Finding(
                        facts.path,
                        node.lineno,
                        "P3-STYLE",
                        "private-name",
                        f"`{node.name}` is module-private by prefix; module-level names "
                        "should be plain. Only nested functions inside a function take _",
                    )
                )
    for cls in classes:
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_") and not DUNDER.match(node.name):
                    out.append(
                        Finding(
                            facts.path,
                            node.lineno,
                            "P3-STYLE",
                            "private-name",
                            f"method `{cls.name}.{node.name}` is private by prefix; "
                            "only nested functions inside a function take _",
                        )
                    )

    # mutable default arguments
    for fn in funcs:
        for default in list(fn.args.defaults) + [d for d in fn.args.kw_defaults if d is not None]:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                out.append(
                    Finding(
                        facts.path,
                        default.lineno,
                        "P0-BLOCKER",
                        "mutable-default",
                        f"mutable default in `{fn.name}`; use a None sentinel or "
                        "field(default_factory=...)",
                    )
                )

    # Any / bare container annotations
    for node in ast.walk(facts.tree):
        if isinstance(node, ast.arg) and node.annotation is not None:
            ann = ann_text(node.annotation)
            if ann in {"Any", "any"}:
                out.append(
                    Finding(
                        facts.path,
                        node.lineno,
                        "P3-STYLE",
                        "no-any-annotation",
                        f"`{node.arg}: {ann}` fakes the type contract; write the real type",
                    )
                )
            elif ann in {"dict", "list", "tuple", "set"}:
                out.append(
                    Finding(
                        facts.path,
                        node.lineno,
                        "P3-STYLE",
                        "bare-container",
                        f"`{node.arg}: {ann}` is a bare container; parameterize it",
                    )
                )
        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
            ann = ann_text(node.annotation)
            if ann in {"Any", "any"}:
                out.append(
                    Finding(
                        facts.path,
                        node.lineno,
                        "P3-STYLE",
                        "no-any-annotation",
                        "`Any` annotation fakes the type contract; write the real type",
                    )
                )

    # single-use private helpers
    defined = {fn.name for fn in funcs if fn.name.startswith("_") and not DUNDER.match(fn.name)}
    if defined:
        references: dict[str, int] = {name: 0 for name in defined}
        for node in ast.walk(facts.tree):
            if isinstance(node, ast.Name) and node.id in references:
                references[node.id] += 1
            elif isinstance(node, ast.Attribute) and node.attr in references:
                references[node.attr] += 1
        # a decorator reference is a real use too
        for node in ast.walk(facts.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for dec in node.decorator_list:
                for sub in ast.walk(dec):
                    if isinstance(sub, ast.Name) and sub.id in references:
                        references[sub.id] += 1
        for fn in funcs:
            if fn.name in references and references[fn.name] <= 1:
                out.append(
                    Finding(
                        facts.path,
                        fn.lineno,
                        "P2-MAINTAIN",
                        "single-use-helper",
                        f"`{fn.name}` has at most one call site; inline it. A short helper "
                        "called once is fragmentation, not clarity",
                    )
                )

    # del <param> on entry
    for fn in funcs:
        params = {
            a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs
        }
        if fn.args.vararg:
            params.add(fn.args.vararg.arg)
        if fn.args.kwarg:
            params.add(fn.args.kwarg.arg)
        for stmt in fn.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue  # leading docstring
            if isinstance(stmt, ast.Delete):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id in params:
                        out.append(
                            Finding(
                                facts.path,
                                stmt.lineno,
                                "P3-STYLE",
                                "del-param",
                                f"`{fn.name}` deletes its own parameter `{target.id}`; "
                                "use it or drop it from the signature",
                            )
                        )
            break  # only inspect the first real statement

    # try blocks that protect too much
    for node in ast.walk(facts.tree):
        if isinstance(node, ast.Try):
            span = (node.end_lineno or node.lineno) - node.lineno + 1
            if span > 15:
                out.append(
                    Finding(
                        facts.path,
                        node.lineno,
                        "P0-BLOCKER",
                        "wide-try-block",
                        f"try block spans {span} lines; narrow the protected region",
                    )
                )

    return out


def ann_text(node: ast.expr) -> str:
    """Render an annotation node as source text, or "" if unparse fails."""
    try:
        return ast.unparse(node)
    except ValueError:
        return ""


def scan_source(path: str, source: str) -> list[Finding]:
    facts = collect(path, source)
    if facts.syntax_error is not None:
        return [
            Finding(
                path,
                facts.syntax_error.lineno or 0,
                "P0-BLOCKER",
                "syntax-error",
                str(facts.syntax_error),
            )
        ]
    out: list[Finding] = []
    out += check_lines(facts)
    out += check_docstrings(facts)
    out += check_file_header_comment(facts)
    out += check_imports(facts)
    out += check_functions(facts)
    return out


HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_diff(patch: str) -> dict[str, list[tuple[int, str]]]:
    """Map path -> added lines as (new_line_number, text)."""
    added: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    lineno = 0

    for raw in patch.splitlines():
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            if target == "/dev/null":
                current = None
                continue
            if target.startswith(("b/", "a/")):
                target = target[2:]
            current = target
            added.setdefault(current, [])
            continue
        match = HUNK.match(raw)
        if match:
            lineno = int(match.group(1))
            continue
        if current is None:
            continue
        if raw.startswith("+"):
            added[current].append((lineno, raw[1:]))
            lineno += 1
        elif raw.startswith(("-", "\\")):
            continue
        else:
            lineno += 1
    return added


def scan_diff(patch: str) -> list[Finding]:
    out: list[Finding] = []
    for path, added_lines in parse_diff(patch).items():
        if not path.endswith(".py"):
            continue
        touched = {n for n, _ in added_lines}
        file = Path(path)
        if file.is_file():
            # full-file analysis, then keep only findings on the added lines
            source = file.read_text(encoding="utf-8")
            facts = collect(path, source)
            if facts.syntax_error is not None:
                continue
            findings = (
                check_lines(facts)
                + check_docstrings(facts)
                + check_file_header_comment(facts)
                + check_imports(facts)
                + check_functions(facts)
            )
            out += [f for f in findings if f.line in touched]
        else:
            # file not on disk (deleted, or reviewing a patch elsewhere):
            # fall back to code rules over the added lines only
            for lineno, text in added_lines:
                code = strip_strings(text)
                for pattern, severity, rule, message in CODE_RULES:
                    if pattern.search(code):
                        out.append(Finding(path, lineno, severity, rule, message))
    return out



def dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple] = set()
    out: list[Finding] = []
    for f in findings:
        key = (f.path, f.line, f.rule, f.message)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("paths", nargs="*", help="Python files or directories to scan")
    parser.add_argument("--diff", metavar="PATCH", help="unified diff file, or - for stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--min-severity",
        default="P3-STYLE",
        choices=RULE_ORDER,
        help="drop findings below this severity (default: report everything)",
    )
    parser.add_argument("--quiet", action="store_true", help="exit code only")
    args = parser.parse_args(argv)

    findings: list[Finding] = []

    if args.diff:
        patch = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
        findings = scan_diff(patch)
    else:
        targets: list[Path] = []
        for p in args.paths:
            path = Path(p)
            if path.is_dir():
                targets.extend(sorted(path.rglob("*.py")))
            else:
                targets.append(path)
        if not targets:
            parser.error("give file paths, a directory, or --diff")
        for path in targets:
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                findings.append(Finding(str(path), 0, "P0-BLOCKER", "unreadable", str(exc)))
                continue
            findings += scan_source(str(path), source)

    findings = dedupe(findings)
    threshold = SEVERITY_ORDER[args.min_severity]
    findings = [f for f in findings if SEVERITY_ORDER.get(f.severity, 99) <= threshold]
    findings.sort(key=lambda f: (f.path, f.line, SEVERITY_ORDER.get(f.severity, 99)))

    if args.quiet:
        return 1 if findings else 0

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False))
        return 1 if findings else 0

    if not findings:
        print("clean: no mechanical anti-patterns found")
        print("This is triage, not a review. Still read the diff and judge intent,")
        print("whether the abstraction earns its keep, and whether the goal was met.")
    else:
        for f in findings:
            print(f.render())
        counts: dict[str, int] = {}
        for f in findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        summary = "  ".join(
            f"{k}:{counts[k]}" for k in RULE_ORDER if k in counts
        )
        print(f"\n{len(findings)} finding(s)  {summary}")
        print("Each finding still needs a judgement call and a concrete fix in the review.")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
