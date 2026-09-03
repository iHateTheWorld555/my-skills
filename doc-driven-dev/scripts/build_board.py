#!/usr/bin/env python3
"""把 board.html 及其全部前端依赖打包成一个自包含 HTML。

看板经 VSCode / SSH 端口转发访问时，子路径资源请求可能拿不到（表现为页面卡在
"加载中…"或控制台 404）。内联成单文件后整个页面只需要一次 GET /，不再依赖任何
子路径请求。字体以 base64 data URI 嵌入 CSS，KaTeX 因此可离线渲染。

用法:
    python3 build_board.py            # 生成 assets/board/board.inline.html
"""

import base64
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets/board"
SOURCE = ASSETS / "board.html"
OUTPUT = ASSETS / "board.inline.html"
SCRIPTS = (
    "cytoscape.min.js",
    "marked.min.js",
    "purify.min.js",
    "katex.min.js",
    "katex-auto-render.min.js",
)


def inline_fonts(css):
    """把 CSS 里的 url(fonts/x.woff2) 换成 base64 data URI，其余格式丢弃。"""

    def replace(match):
        name = match.group(1)
        target = ASSETS / "fonts" / Path(name).name
        if not target.is_file():
            return match.group(0)
        data = base64.b64encode(target.read_bytes()).decode("ascii")
        return f"url(data:font/woff2;base64,{data})"

    css = re.sub(r"url\((fonts/[^)]+\.woff2)\)", replace, css)
    # 去掉 woff/ttf 回退：字体已内联 woff2，回退只会触发无用的子路径请求
    css = re.sub(r",\s*url\(fonts/[^)]+\.(?:woff|ttf)\)\s*format\(\"(?:woff|truetype)\"\)", "", css)
    return css


def build():
    html = SOURCE.read_text(encoding="utf-8")
    css = inline_fonts((ASSETS / "katex.min.css").read_text(encoding="utf-8"))
    html = html.replace(
        '<link rel="stylesheet" href="/assets/katex.min.css">',
        "<style>\n" + css + "\n</style>",
    )
    for name in SCRIPTS:
        code = (ASSETS / name).read_text(encoding="utf-8")
        # 去掉 sourceMappingURL：内联后浏览器会去找 .map 文件并报 404
        code = re.sub(r"(?m)^\s*//#\s*sourceMappingURL=.*$", "", code)
        # 脚本内容原样内联；</script> 必须转义，否则会提前闭合标签
        code = code.replace("</script", "<\\/script")
        html = html.replace(
            f'<script src="/assets/{name}"></script>',
            "<script>\n" + code + "\n</script>",
        )
    leftover = re.findall(r'(?:src|href)="/assets/[^"]+"', html)
    if leftover:
        raise SystemExit(f"仍有未内联的资源引用: {leftover}")
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"built {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
