#!/usr/bin/env python3
"""paperq -- on-disk BFS queue for citation-graph literature surveys.

Stdlib only. All state lives in <outdir>/paperq.sqlite so the loop survives
agent restarts, context resets, and parallel sub-agents.

The `gate` subcommand is the loop's stopping authority. Agents must not decide
termination themselves.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources                                                    # noqa: E402

# export.arxiv.org resolves (on some ISP/VPN routes) to a Fastly edge that
# blackholes HTTPS -- plain urlopen then hangs until timeout, which the probe
# reports as arxiv=EMPTY and is easily misread as "no such papers". Pin the
# working edge IP when CITATION_BFS_ARXIV_IP is set. Opt-in so the shared skill
# behaves identically for everyone else.
_ARXIV_IP = os.environ.get("CITATION_BFS_ARXIV_IP")
if _ARXIV_IP:
    import http.client as _http_client
    _orig_connect = _http_client.HTTPSConnection.connect

    def _pinned_connect(self):
        if self.host == "export.arxiv.org":
            self.sock = self._create_connection(
                (_ARXIV_IP, self.port), self.timeout, self.source_address)
            if self._tunnel_host:
                self._tunnel()
            self.sock = self._context.wrap_socket(
                self.sock, server_hostname=self.host)
            return
        return _orig_connect(self)

    _http_client.HTTPSConnection.connect = _pinned_connect

UA = "citation-bfs-survey/1.0 (research use; contact via local agent)"
S2 = "https://api.semanticscholar.org/graph/v1"
ARXIV = "https://export.arxiv.org/api/query"   # MUST be https: http:// 301-redirects to an empty body
GH = "https://api.github.com"

STALE_CLAIM_SEC = 1800


# --------------------------------------------------------------------------- io

def _db(outdir: str) -> sqlite3.Connection:
    os.makedirs(outdir, exist_ok=True)
    con = sqlite3.connect(os.path.join(outdir, "paperq.sqlite"), timeout=60)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=60000")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
        CREATE TABLE IF NOT EXISTS papers(
            id TEXT PRIMARY KEY,          -- arXiv id > doi > s2:<paperId> > gs:<cluster>
            s2id TEXT, arxiv TEXT, doi TEXT, gs_cluster TEXT,
            title TEXT, title_key TEXT, year INT, venue TEXT,
            citations INT, authors TEXT, abstract TEXT,
            status TEXT NOT NULL,         -- frontier|in_progress|done|rejected|candidate
            depth INT NOT NULL DEFAULT 0,
            parent TEXT, discovered_via TEXT,
            summary TEXT, code_url TEXT, code_status TEXT, stars INT,
            relevance TEXT, worker TEXT,
            claimed_at REAL, updated_at REAL
        );
        CREATE TABLE IF NOT EXISTS edges(
            src TEXT, dst TEXT, kind TEXT, UNIQUE(src, dst, kind));
        CREATE TABLE IF NOT EXISTS log(ts REAL, kind TEXT, detail TEXT);
        CREATE INDEX IF NOT EXISTS ix_status ON papers(status, depth);
        CREATE UNIQUE INDEX IF NOT EXISTS ix_titlekey
            ON papers(title_key) WHERE title_key IS NOT NULL;
        """
    )
    return con


def _meta(con, k, default=None):
    r = con.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
    return r["v"] if r else default


def _setmeta(con, k, v):
    con.execute("INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (k, str(v)))


def _log(con, kind, detail):
    con.execute("INSERT INTO log VALUES(?,?,?)", (time.time(), kind, detail))


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------------ http

def _cache_path(outdir, url, body):
    h = hashlib.sha256((url + (body or "")).encode()).hexdigest()[:24]
    d = os.path.join(outdir, ".cache")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, h + ".json")


def fetch(url, outdir, headers=None, body=None, cache=True, tries=6, raw=False,
          follow=False, timeout=60):
    """GET/POST with 429-aware exponential backoff and on-disk caching.

    `follow=True` is required for OpenCitations, which 301s to a versioned path;
    urllib follows redirects by default, so this flag only documents intent and
    keeps the cache key distinct."""
    cp = _cache_path(outdir, url, body)
    if cache and os.path.exists(cp):
        try:
            with open(cp) as f:
                return json.load(f)["d"]
        except Exception:
            pass

    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    if "semanticscholar.org" in url and os.environ.get("S2_API_KEY"):
        hdrs["x-api-key"] = os.environ["S2_API_KEY"]
    if "api.github.com" in url and os.environ.get("GITHUB_TOKEN"):
        hdrs["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

    data = body.encode() if body else None
    delay = 4.0
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs,
                                         method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8", "replace")
            payload = txt if raw else json.loads(txt)
            if isinstance(payload, dict) and payload.get("code") == "429":
                raise urllib.error.HTTPError(url, 429, "rate limited", None, None)
            if cache:
                with open(cp, "w") as f:
                    json.dump({"d": payload, "t": time.time()}, f)
            return payload
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 90)
                continue
            return None
        except Exception as e:                                  # noqa: BLE001
            last = str(e)
            if attempt < tries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 90)
    sys.stderr.write(f"[warn] give up {url[:110]} :: {last}\n")
    return None


# ------------------------------------------------------------------- id helpers

ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")


def norm_arxiv(s):
    return sources.norm_arxiv(s)


def norm_doi(s):
    if not s:
        return None
    s = str(s).strip().lower()
    s = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:", "", s)
    # arXiv DOIs are just a wrapper around the arXiv id -- prefer the id itself
    if s.startswith("10.48550/arxiv."):
        return None
    return s if s.startswith("10.") else None


def key_for(arxiv=None, s2id=None, doi=None, gs_cluster=None):
    """Stable identity, most-specific first. Papers found by different engines
    must collapse onto one row or the survey double-counts."""
    a = norm_arxiv(arxiv)
    if a:
        return a
    d = norm_doi(doi)
    if d:
        return "doi:" + d
    if s2id:
        return "s2:" + s2id
    if gs_cluster:
        return "gs:" + str(gs_cluster)
    return None


# ------------------------------------------------------------------ ingestion

S2_FIELDS = sources.S2_FIELDS


def _title_key(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())[:60] or None


# Speech/TTS topic lexicon. Word-boundary regex: "sing" must not match "using".
DEFAULT_TOPIC_WORDS = (
    r"\b(speech|tts|voice|voices|vocal|vocals|voicing|spoken|speaker|speak|"
    r"acoustic|acoustics|singing|singers|utterance|utterances|phoneme|phonemes|"
    r"prosody|prosodic|dialog|dialogue|text-to-speech|interview|podcast)\w*\b"
)


def _topic_match(rec, words):
    """True if title+abstract mentions any topic term. Regex with word
    boundaries; case-insensitive."""
    text = f"{rec.get('title') or ''} {rec.get('abstract') or ''}".lower()
    if not text.strip():
        # no text to judge -> keep, let a human triage rather than blind-drop
        return True
    return re.search(words, text) is not None


def upsert(con, *, arxiv=None, s2id=None, doi=None, gs_cluster=None, title=None,
           year=None, venue=None, citations=None, abstract=None, authors=None,
           status="candidate", depth=0, parent=None, via=None):
    k = key_for(arxiv, s2id, doi, gs_cluster)
    if not k:
        return None
    now = time.time()
    arxiv, doi = norm_arxiv(arxiv), norm_doi(doi)

    row = con.execute("SELECT * FROM papers WHERE id=?", (k,)).fetchone()
    if not row:
        # Cross-engine dedup: the same paper arrives as an arXiv id from arXiv,
        # a DOI from Crossref and a cluster id from Scholar. Collapse on
        # normalized title so counts and summaries are not split across rows.
        tk = _title_key(title)
        if tk:
            hit = con.execute(
                "SELECT * FROM papers WHERE title_key=?", (tk,)).fetchone()
            if hit:
                row, k = hit, hit["id"]

    if row:
        # Fill gaps only; never downgrade a status that was already earned.
        con.execute(
            """UPDATE papers SET title=COALESCE(title,?), year=COALESCE(year,?),
               venue=COALESCE(venue,?),
               citations=NULLIF(MAX(COALESCE(citations,0),COALESCE(?,0)),0),
               abstract=COALESCE(abstract,?), authors=COALESCE(authors,?),
               s2id=COALESCE(s2id,?), arxiv=COALESCE(arxiv,?),
               doi=COALESCE(doi,?), gs_cluster=COALESCE(gs_cluster,?),
               discovered_via=COALESCE(discovered_via,?), updated_at=?
               WHERE id=?""",
            (title, year, venue, citations, abstract, authors, s2id, arxiv,
             doi, gs_cluster, via, now, k))
        return k

    con.execute(
        """INSERT INTO papers(id,s2id,arxiv,doi,gs_cluster,title,title_key,year,
           venue,citations,authors,abstract,status,depth,parent,discovered_via,
           updated_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (k, s2id, arxiv, doi, gs_cluster, title, _title_key(title), year, venue,
         citations, authors, abstract, status, depth, parent, via, now))
    return k


UPSERT_FIELDS = ("arxiv", "s2id", "doi", "gs_cluster", "title", "year",
                 "venue", "citations", "abstract", "authors")


def only_fields(rec):
    """Source records carry extra keys (source, relation, ext_url) that upsert
    does not accept. Filter rather than spread blindly."""
    return {k: rec.get(k) for k in UPSERT_FIELDS}


def from_s2(d):
    return sources._from_s2(d)


# ------------------------------------------------------------------- commands

def cmd_init(a):
    con = _db(a.outdir)
    _setmeta(con, "topic", a.topic)
    _setmeta(con, "min_year", a.min_year)
    _setmeta(con, "max_depth", a.max_depth)
    _setmeta(con, "target_papers", a.target_papers)
    _setmeta(con, "min_seed_queries", a.min_seed_queries)
    if a.criteria:
        _setmeta(con, "criteria", a.criteria)
    _setmeta(con, "created", datetime.now(timezone.utc).isoformat())
    _setmeta(con, "queries_run", _meta(con, "queries_run", "0"))
    con.commit()
    out({"ok": True, "outdir": os.path.abspath(a.outdir), "topic": a.topic,
         "min_year": a.min_year, "max_depth": a.max_depth,
         "target_papers": a.target_papers,
         "criteria": a.criteria or None,
         "note": ("screening criteria stored -- workers will judge every "
                  "candidate against them (see SKILL.md Screening Protocol)"
                  if a.criteria else
                  "no criteria given: workers will improvise relevance; "
                  "STRONGLY recommend setting them via `criteria`")})


def cmd_seed(a):
    """Query several independent engines per phrase and merge. Different engines
    have structurally different blind spots: arXiv sees only preprints, Crossref
    and DBLP see published venue work, Google Scholar indexes work that never
    reached arXiv at all."""
    con = _db(a.outdir)
    min_year = a.min_year or _meta(con, "min_year")
    engines = [e.strip() for e in a.sources.split(",") if e.strip()]
    unknown = [e for e in engines if e not in sources.DISCOVERY]
    if unknown:
        out({"error": "unknown source(s)", "unknown": unknown,
             "available": sorted(sources.DISCOVERY)}); return

    added, per_engine, per_query = [], {e: 0 for e in engines}, {}
    for q in a.query:
        hits, used = [], []
        for e in engines:
            try:
                r = sources.DISCOVERY[e](fetch, q, a.outdir, a.limit, min_year)
            except Exception as ex:                               # noqa: BLE001
                sys.stderr.write(f"[warn] source {e} failed on '{q}': {ex}\n")
                r = []
            if r:
                used.append(e)
                per_engine[e] += len(r)
                hits += r
        for h in hits:
            k = upsert(con, **only_fields(h), status="frontier", depth=0,
                       via=f"seed:{h.get('source')}:{q}")
            if k:
                # keyword-search hits are unjudged at this point: ring2 until a
                # worker triages them (accept re-tags with the chosen tier)
                con.execute("UPDATE papers SET relevance='[ring2] keyword-search hit (untriaged)' "
                            "WHERE id=? AND relevance IS NULL", (k,))
                added.append(k)
        per_query[q] = {"hits": len(hits), "engines": used}
        _log(con, "seed", f"{q} -> {len(hits)} hits via {','.join(used) or 'none'}")
    _setmeta(con, "queries_run", int(_meta(con, "queries_run", "0")) + len(a.query))
    con.commit()

    n_front = con.execute("SELECT COUNT(*) c FROM papers WHERE status='frontier'").fetchone()["c"]
    dead = [e for e in engines if per_engine[e] == 0]
    out({"ok": True, "papers_touched": len(set(added)), "frontier_size": n_front,
         "per_engine_hits": per_engine, "per_query": per_query,
         "silent_engines": dead,
         "note": ("A silent engine means that channel is down, not that no such "
                  "papers exist -- run `probe` to tell the two apart."
                  if dead else "all requested engines returned results")})


def cmd_add(a):
    """Add user-supplied seed papers. Accepts arXiv ids, DOIs, or S2 ids."""
    con = _db(a.outdir)
    ids = [norm_arxiv(x) or x for x in a.id]
    metas = s2_batch(ids, a.outdir)
    n, unresolved = 0, []
    for i in ids:
        m = metas.get(i)
        if m:
            rec = only_fields(from_s2(m))
        else:
            unresolved.append(i)
            rec = only_fields(dict(arxiv=i if norm_arxiv(i) else None,
                                   doi=i if str(i).startswith("10.") else None,
                                   s2id=None if (norm_arxiv(i) or
                                                 str(i).startswith("10.")) else i))
        k = upsert(con, **rec, status="frontier", depth=0, via="seed:manual")
        if k:
            # seeds are core by definition (the user named them)
            con.execute("UPDATE papers SET relevance='[core] user-provided seed' "
                        "WHERE id=? AND relevance IS NULL", (k,))
            n += 1
    con.commit()
    out({"ok": True, "added": n, "resolved_metadata": len(metas),
         "unresolved": unresolved,
         "note": ("Unresolved ids were queued without metadata; `record` will "
                  "retry hydration." if unresolved else "")})


def s2_batch(ids, outdir):
    """POST /paper/batch -- cheapest way to hydrate many ids at once. Accepts
    bare arXiv ids, `DOI:...`, `s2:...` or raw S2 paperIds."""
    res = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        qids = []
        for x in chunk:
            if x.startswith(("DOI:", "doi:")):
                qids.append("DOI:" + x.split(":", 1)[1])
            elif x.startswith("s2:"):
                qids.append(x[3:])
            elif norm_arxiv(x):
                qids.append("arXiv:" + norm_arxiv(x))
            elif str(x).startswith("10."):
                qids.append("DOI:" + x)
            else:
                qids.append(x)
        d = fetch(f"{S2}/paper/batch?fields={urllib.parse.quote(S2_FIELDS)}", outdir,
                  headers={"Content-Type": "application/json"},
                  body=json.dumps({"ids": qids}))
        if not isinstance(d, list):
            continue
        for orig, item in zip(chunk, d):
            if item:
                res[orig] = item
    return res


def cmd_claim(a):
    """Hand out frontier papers to workers. Reclaims stale claims first."""
    con = _db(a.outdir)
    cut = time.time() - STALE_CLAIM_SEC
    con.execute("""UPDATE papers SET status='frontier', worker=NULL
                   WHERE status='in_progress' AND COALESCE(claimed_at,0) < ?""", (cut,))
    md = int(_meta(con, "max_depth", "2"))
    order = ("COALESCE(citations,0) DESC" if a.order == "cites"
             else "depth ASC, COALESCE(citations,0) DESC")
    rows = con.execute(
        f"""SELECT id,arxiv,s2id,title,year,citations,depth,abstract FROM papers
           WHERE status='frontier' AND depth<=? ORDER BY {order} LIMIT ?""",
        (md, a.n)).fetchall()
    asg = []
    for idx, r in enumerate(rows):
        w = a.worker or f"w{idx+1}"
        con.execute("UPDATE papers SET status='in_progress', worker=?, claimed_at=? WHERE id=?",
                    (w, time.time(), r["id"]))
        asg.append({"paper_id": r["id"], "worker": w, "depth": r["depth"],
                    "title": r["title"], "year": r["year"],
                    "citations": r["citations"],
                    "abstract": (r["abstract"] or "")[:400]})
    con.commit()
    out({"claimed": len(asg), "max_depth": md,
         "criteria": _meta(con, "criteria"),
         "screening_reminder": ("judge every candidate against the stored "
                                "criteria; two-pass (title first, abstract for "
                                "borderline); tag accept --tier core|ring2"),
         "assignments": asg})


def cmd_expand(a):
    """Expand one paper through several independent citation-graph backends,
    pre-filter, and list candidates for triage."""
    con = _db(a.outdir)
    row = con.execute("SELECT * FROM papers WHERE id=?", (a.id,)).fetchone()
    if not row:
        out({"error": "unknown paper", "id": a.id}); return
    min_year = int(_meta(con, "min_year", "2024"))
    pid = (f"arXiv:{row['arxiv']}" if row["arxiv"]
           else f"DOI:{row['doi']}" if row["doi"]
           else row["s2id"] or row["id"].replace("s2:", ""))
    backends = [b.strip() for b in a.backends.split(",") if b.strip()]

    raw, degraded, per_backend = [], [], {}

    if "s2" in backends:
        g, failed = sources.s2_graph(fetch, pid, a.outdir, a.limit)
        raw += g
        degraded += [f"s2:{d}" for d in failed]
        per_backend["s2"] = len(g)

    if "s2rec" in backends:
        r = sources.s2_recommend(fetch, pid, a.outdir, a.rec_limit)
        raw += r
        per_backend["s2rec"] = len(r)
        if not r:
            degraded.append("s2rec")

    if "opencit" in backends and row["doi"]:
        oc = sources.opencit_citedby(fetch, row["doi"], a.outdir, a.limit)
        # DOI-only stubs: hydrate through S2 so they carry titles/years
        if oc:
            hy = s2_batch([f"DOI:{x['doi']}" for x in oc[:60]], a.outdir)
            for v in hy.values():
                rr = from_s2(v); rr["relation"] = "cited_by"; rr["source"] = "opencit"
                raw.append(rr)
        per_backend["opencit"] = len(oc)

    if "gscholar" in backends and row["gs_cluster"]:
        gsc = sources.gscholar_citedby(fetch, row["gs_cluster"], a.outdir,
                                       a.limit, min_year)
        raw += gsc
        per_backend["gscholar"] = len(gsc)
        if not gsc:
            degraded.append("gscholar")

    cands, generic, offtopic = [], 0, 0
    for rec in raw:
        kind = rec.get("relation") or "cited_by"
        yr, cc = rec.get("year") or 0, rec.get("citations") or 0
        # Drop field-defining classics (Attention/BERT/...). They are cited by
        # everything, are not on-topic, and would eat the whole budget.
        if cc >= a.generic_cites and yr and yr < min_year - 2:
            generic += 1
            continue
        # keep recent work, or older work influential enough to be foundational
        if yr and yr < min_year and cc < a.foundational_cites:
            continue
        # Topic lexicon pre-filter: a candidate must mention a topic term in
        # title/abstract, OR be a highly-cited methodological source. Without
        # this, expanding any seed drags in its whole generic-ML neighbourhood
        # (measured: 1 flow-matching seed pulled 1000+ irrelevant papers into
        # deferred, which made the gate's "queue drained" semantics unreachable).
        # --require-words "" disables the filter.
        # --keep-cites > 0 lets high-cited papers bypass; 0 (default) = no
        # bypass, the lexicon applies to every candidate.
        bypass = a.keep_cites > 0 and cc >= a.keep_cites
        if a.require_words and not bypass and not _topic_match(rec, a.require_words):
            offtopic += 1
            continue
        k = key_for(rec.get("arxiv"), rec.get("s2id"), rec.get("doi"),
                    rec.get("gs_cluster"))
        if not k:
            continue
        con.execute("INSERT OR IGNORE INTO edges VALUES(?,?,?)", (a.id, k, kind))
        ex = con.execute("SELECT status FROM papers WHERE id=?", (k,)).fetchone()
        if ex and ex["status"] not in ("candidate", "deferred"):
            continue
        real = upsert(con, **only_fields(rec), status="candidate",
                      depth=row["depth"] + 1, parent=a.id,
                      via=f"{kind}:{rec.get('source','s2')}")
        if real:
            cands.append({"paper_id": real, "title": rec["title"],
                          "year": rec["year"], "citations": rec["citations"],
                          "relation": kind, "found_by": rec.get("source", "s2"),
                          "abstract": (rec.get("abstract") or "")[:350]})
    con.commit()

    # Dedup by id (several backends legitimately return the same paper)
    seen, uniq = set(), []
    for c in cands:
        if c["paper_id"] not in seen:
            seen.add(c["paper_id"]); uniq.append(c)

    # Budget is split PER CHANNEL. Without this, the largest channel (s2
    # cited_by, often 200+ items) starves every other one: measured 30 s2rec
    # recommendations all pushed to deferred by newer cited_by papers, which
    # silently discards the one channel that reaches papers the graph cannot.
    # Budget split PER CHANNEL. Within the cited_by channel, citations dominate:
    # sorting year-first let 2026 zero-citation papers crowd 2023-2025 landmark
    # works (VALL-E 1352 cites, MegaTTS 3) into deferred -- the survey then
    # contained the seed's obscure neighbours but not its field's famous papers.
    fwd = sorted([c for c in uniq if c["relation"] == "cited_by"],
                 key=lambda x: (-(x["citations"] or 0), -(x["year"] or 0)))
    back = sorted([c for c in uniq if c["relation"] == "cites"],
                  key=lambda x: -(x["citations"] or 0))
    rec_c = sorted([c for c in uniq if c["relation"] == "recommended"],
                   key=lambda x: (-(x["year"] or 0), -(x["citations"] or 0)))

    n = a.max_candidates
    quota = {"fwd": max(1, n // 2), "back": max(1, n // 4),
             "rec": max(1, n // 4)} if rec_c else \
            {"fwd": max(1, n - n // 3), "back": max(1, n // 3), "rec": 0}
    keep = fwd[:quota["fwd"]] + back[:quota["back"]] + rec_c[:quota["rec"]]
    # Redistribute unused quota so a thin channel does not waste the budget
    leftover = n - len(keep)
    if leftover > 0:
        pool = fwd[quota["fwd"]:] + rec_c[quota["rec"]:] + back[quota["back"]:]
        keep += pool[:leftover]
    keep_ids = {c["paper_id"] for c in keep}
    # Over-budget candidates are PARKED, not deleted: they stay in the DB as
    # 'deferred' so a later pass can still reach them. Deleting would silently
    # cap recall, which defeats the point of BFS.
    deferred = [c["paper_id"] for c in uniq if c["paper_id"] not in keep_ids]
    if deferred:
        con.executemany("UPDATE papers SET status='deferred' WHERE id=? AND status='candidate'",
                        [(i,) for i in deferred])
        con.commit()

    out({"paper_id": a.id, "title": row["title"], "depth": row["depth"],
         "candidates": len(keep), "per_backend_raw": per_backend,
         "degraded_backends": degraded,
         "generic_classics_skipped": generic,
         "offtopic_filtered": offtopic,
         "deferred_over_budget": len(deferred),
         "topic": _meta(con, "topic"),
         "instruction": ("Judge each candidate against the topic. Call `accept` for "
                         "on-topic ones and `reject` for the rest. Every candidate "
                         "must be triaged before this paper can be recorded."),
         "items": keep})


def gh_stars(query, outdir, explicit_url=None):
    if explicit_url:
        m = re.search(r"github\.com/([^/\s]+)/([^/\s#?)\]]+)", explicit_url)
        if m:
            repo = f"{m.group(1)}/{m.group(2)}".removesuffix(".git")
            d = fetch(f"{GH}/repos/{repo}", outdir)
            if d and "stargazers_count" in d:
                return {"code_url": d["html_url"], "stars": d["stargazers_count"],
                        "code_status": "official", "pushed_at": d.get("pushed_at")}
            return {"code_url": explicit_url, "stars": None, "code_status": "url_unverified"}
    if not query:
        return {"code_url": None, "stars": None, "code_status": "none_found"}
    q = urllib.parse.urlencode({"q": query, "per_page": 3, "sort": "stars"})
    d = fetch(f"{GH}/search/repositories?{q}", outdir)
    items = (d or {}).get("items") or []
    if not items:
        return {"code_url": None, "stars": None, "code_status": "none_found"}
    top = items[0]
    return {"code_url": top["html_url"], "stars": top["stargazers_count"],
            "code_status": "search_guess", "pushed_at": top.get("pushed_at")}


def cmd_record(a):
    """Finish a paper: store summary + code/star info, mark done. Enforces
    that all candidates spawned by this paper were triaged."""
    con = _db(a.outdir)
    row = con.execute("SELECT * FROM papers WHERE id=?", (a.id,)).fetchone()
    if not row:
        out({"error": "unknown paper", "id": a.id}); return
    if len((a.summary or "").strip()) < a.min_summary_chars:
        out({"error": f"summary too short (<{a.min_summary_chars} chars); "
                      "state what the paper actually does", "id": a.id}); return
    untriaged = con.execute(
        """SELECT COUNT(*) c FROM papers WHERE parent=? AND status='candidate'""",
        (a.id,)).fetchone()["c"]
    if untriaged and not a.force:
        out({"error": "untriaged candidates remain; accept/reject them first",
             "id": a.id, "untriaged": untriaged}); return

    if not row["citations"] or not row["title"]:
        m = s2_batch([row["arxiv"] or row["id"].replace("s2:", "")], a.outdir)
        for v in m.values():
            upsert(con, **only_fields(from_s2(v)))
        row = con.execute("SELECT * FROM papers WHERE id=?", (a.id,)).fetchone()

    if a.no_code:
        code = {"code_url": None, "stars": None, "code_status": "declared_none"}
    else:
        code = gh_stars(a.code_query or row["title"], a.outdir, a.code_url)
    con.execute(
        """UPDATE papers SET status='done', summary=?, code_url=?, stars=?,
           code_status=?, updated_at=? WHERE id=?""",
        (a.summary.strip(), code["code_url"], code["stars"], code["code_status"],
         time.time(), a.id))
    _log(con, "record", a.id)
    con.commit()
    out({"ok": True, "paper_id": a.id, "title": row["title"],
         "citations": row["citations"], **code})


def cmd_criteria(a):
    """Set or update the screening criteria (inclusion/exclusion + core-class
    definition) stored in the survey. Adopted from ARS deep-research: criteria
    are defined BEFORE screening, not retrofitted -- and every worker claim
    surfaces them so relevance judgment is consistent across agents."""
    con = _db(a.outdir)
    if a.text:
        _setmeta(con, "criteria", a.text)
    else:
        _setmeta(con, "criteria", "")          # explicit clear
    con.commit()
    out({"ok": True, "criteria": a.text or None})


def cmd_accept(a):
    con = _db(a.outdir)
    if len((a.why or "").strip()) < 10:
        out({"error": "give a one-line reason tying the paper to the topic"}); return
    tier = a.tier
    why = a.why.strip()
    con.execute("""UPDATE papers SET status='frontier', relevance=?, updated_at=?
                   WHERE id=? AND status='candidate'""",
                (f"[{tier}] {why}", time.time(), a.id))
    con.commit()
    out({"ok": True, "accepted": a.id, "tier": tier})


def cmd_reject(a):
    con = _db(a.outdir)
    con.executemany("""UPDATE papers SET status='rejected', relevance=?, updated_at=?
                       WHERE id=? AND status IN ('candidate','frontier')""",
                    [(a.why or "off-topic", time.time(), i) for i in a.id])
    con.commit()
    out({"ok": True, "rejected": a.id})


def cmd_pending(a):
    """List EVERY untriaged candidate for a paper (or globally). Use this instead
    of `list` before recording -- `list` truncates, this does not."""
    con = _db(a.outdir)
    if a.parent:
        rows = con.execute(
            """SELECT id,title,year,citations,discovered_via FROM papers
               WHERE parent=? AND status='candidate'
               ORDER BY COALESCE(year,0) DESC""", (a.parent,)).fetchall()
    else:
        rows = con.execute(
            """SELECT id,title,year,citations,discovered_via FROM papers
               WHERE status='candidate' ORDER BY COALESCE(year,0) DESC""").fetchall()
    out({"untriaged": len(rows), "parent": a.parent,
         "ids": [r["id"] for r in rows], "items": [dict(r) for r in rows]})


def cmd_reject_rest(a):
    """Reject every still-untriaged candidate of one paper. Exists so a long tail
    of clearly off-topic items cannot stall the queue -- read them first."""
    con = _db(a.outdir)
    n = con.execute(
        """UPDATE papers SET status='rejected', relevance=?, updated_at=?
           WHERE parent=? AND status='candidate'""",
        (a.why, time.time(), a.parent)).rowcount
    con.commit()
    out({"ok": True, "parent": a.parent, "rejected": n})


def _counts(con):
    c = {r["status"]: r["c"] for r in
         con.execute("SELECT status, COUNT(*) c FROM papers GROUP BY status")}
    return {k: c.get(k, 0) for k in
            ("frontier", "in_progress", "done", "candidate", "deferred", "rejected")}


def cmd_gate(a):
    """THE stopping authority. exit 0 = keep working, exit 3 = survey complete."""
    con = _db(a.outdir)
    cut = time.time() - STALE_CLAIM_SEC
    reclaimed = con.execute(
        """UPDATE papers SET status='frontier', worker=NULL
           WHERE status='in_progress' AND COALESCE(claimed_at,0) < ?""", (cut,)).rowcount
    con.commit()

    c = _counts(con)
    md = int(_meta(con, "max_depth", "2"))
    target = int(_meta(con, "target_papers", "40"))
    min_q = int(_meta(con, "min_seed_queries", "6"))
    qrun = int(_meta(con, "queries_run", "0"))

    def reachable():
        return con.execute(
            "SELECT COUNT(*) c FROM papers WHERE status='frontier' AND depth<=?",
            (md,)).fetchone()["c"]

    # Frontier dry but target unmet -> revive parked candidates before giving up.
    revived = 0
    if (not reachable() and not c["candidate"] and not c["in_progress"]
            and c["done"] < target and c["deferred"]):
        revived = con.execute(
            """UPDATE papers SET status='candidate' WHERE id IN (
                 SELECT id FROM papers WHERE status='deferred' AND depth<=?
                 ORDER BY COALESCE(year,0) DESC, COALESCE(citations,0) DESC LIMIT ?)""",
            (md, a.revive)).rowcount
        con.commit()
        c = _counts(con)

    maxd = con.execute("SELECT COALESCE(MAX(depth),0) d FROM papers WHERE status='done'").fetchone()["d"]
    reach = reachable()

    reasons, directive = [], None
    if c["candidate"]:
        reasons.append(f"{c['candidate']} candidates untriaged")
        directive = "Triage candidates with accept/reject (see `list --status candidate`)."
    if c["in_progress"]:
        reasons.append(f"{c['in_progress']} papers claimed but not recorded")
        directive = directive or "Finish recording in-progress papers."
    if reach:
        reasons.append(f"{reach} frontier papers within depth {md}")
        directive = directive or f"Claim next batch: claim --n {a.batch}"
    if qrun < min_q:
        reasons.append(f"only {qrun}/{min_q} seed queries run")
        directive = directive or ("Run more seed queries from NEW angles "
                                  "(synonyms, adjacent subfields, method names, venues).")
    if c["done"] < target:
        reasons.append(f"only {c['done']}/{target} papers fully recorded")
        directive = directive or ("Frontier is dry and no parked candidates remain -- "
                                  "widen with fresh seed queries from new angles, or "
                                  "raise max_depth. DO NOT stop here.")

    done = not reasons
    res = {"verdict": "DONE" if done else "CONTINUE", "counts": c,
           "depth_reached": maxd, "max_depth": md,
           "papers_recorded": c["done"], "target_papers": target,
           "seed_queries_run": qrun, "min_seed_queries": min_q,
           "reclaimed_stale": reclaimed, "revived_deferred": revived,
           "blocking_reasons": reasons,
           "next_action": directive or "Write the report; then `report --out survey.md`."}
    out(res)
    sys.exit(3 if done else 0)


def cmd_list(a):
    con = _db(a.outdir)
    q = "SELECT id,title,year,citations,status,depth,stars,code_status,summary FROM papers"
    p = []
    if a.status:
        q += " WHERE status=?"; p.append(a.status)
    q += " ORDER BY depth, COALESCE(citations,0) DESC LIMIT ?"; p.append(a.n)
    rows = [dict(r) for r in con.execute(q, p)]
    for r in rows:
        if r.get("summary"):
            r["summary"] = r["summary"][:160]
    out({"count": len(rows), "items": rows})


def cmd_report(a):
    con = _db(a.outdir)
    topic = _meta(con, "topic", "(untitled)")
    # --tier core: only papers the workers tagged as core class. This is the
    # deliverable the user actually reads; ring2/others stay in the DB.
    tier_filter = ""
    if a.tier == "core":
        tier_filter = " AND relevance LIKE '[core]%'"
    elif a.tier == "ring2":
        tier_filter = " AND relevance LIKE '[ring2]%'"
    rows = con.execute(
        f"""SELECT * FROM papers WHERE status='done'{tier_filter}
           ORDER BY depth, COALESCE(citations,0) DESC""").fetchall()
    L = [f"# Literature survey: {topic}", ""]
    crit = _meta(con, "criteria")
    if crit:
        L += [f"**Screening criteria**: {crit}", "",
              f"**Tier filter**: {a.tier}", ""]
    L += [f"- Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
         f"- Papers recorded: {len(rows)} | rejected: {_counts(con)['rejected']}",
         f"- Depth reached: {max([r['depth'] for r in rows], default=0)}",
         "", "## Papers", "",
         "| # | Title | Year | Venue | Cites | Code | Stars | Depth | Found via |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        link = (f"[{r['id']}](https://arxiv.org/abs/{r['arxiv']})" if r["arxiv"]
                else f"[{r['id']}](https://doi.org/{r['doi']})" if r["doi"]
                else r["id"])
        code = f"[repo]({r['code_url']})" if r["code_url"] else "-"
        L.append(f"| {i} | {r['title']} ({link}) | {r['year'] or '-'} | "
                 f"{(r['venue'] or '-')[:28]} | "
                 f"{r['citations'] if r['citations'] is not None else '-'} | {code} | "
                 f"{r['stars'] if r['stars'] is not None else '-'} | {r['depth']} | "
                 f"{r['discovered_via'] or '-'} |")
    L += ["", "## Per-paper notes", ""]
    for r in rows:
        L += [f"### {r['title']}",
              f"- id: `{r['id']}` | year: {r['year'] or '?'} | citations: "
              f"{r['citations'] if r['citations'] is not None else '?'}",
              f"- code: {r['code_url'] or 'none found'} "
              f"(stars: {r['stars'] if r['stars'] is not None else '?'}, "
              f"{r['code_status'] or '?'})",
              f"- discovered via: {r['discovered_via'] or '-'}"
              + (f" from `{r['parent']}`" if r["parent"] else ""),
              f"- relevance: {r['relevance'] or 'seed'}",
              "", r["summary"] or "_no summary_", ""]
    md = "\n".join(L)
    path = os.path.join(a.outdir, a.out)
    with open(path, "w") as f:
        f.write(md)
    out({"ok": True, "written": os.path.abspath(path), "papers": len(rows)})


def cmd_sweep(a):
    """Retroactively apply the topic lexicon filter to parked rows. Same rule
    as expand's pre-filter: topic term in title/abstract OR citations >=
    --keep-cites, otherwise reject. --dry-run only reports. Never touches
    done/frontier/in_progress rows."""
    con = _db(a.outdir)
    statuses = [s.strip() for s in a.status.split(",") if s.strip()]
    killed, kept = [], 0
    for row in con.execute(
            f"SELECT id,title,abstract,citations FROM papers WHERE status IN "
            f"({','.join('?' * len(statuses))})", statuses):
        cc = row["citations"] or 0
        bypass = a.keep_cites > 0 and cc >= a.keep_cites
        if not bypass and not _topic_match(
                {"title": row["title"], "abstract": row["abstract"]},
                a.require_words):
            kept += 1
            continue
        killed.append(row["id"])
    if killed and not a.dry_run:
        con.executemany(
            """UPDATE papers SET status='rejected',
               relevance='sweep: no topic term, cites < keep-cites'
               WHERE id=?""", [(i,) for i in killed])
        con.commit()
    out({"dry_run": a.dry_run, "rejected": len(killed), "kept": kept,
         "note": ("re-run without --dry-run to apply" if a.dry_run
                  else "rows moved to rejected with reason; reversible via SQL"),
         "sample_killed": killed[:10]})


def cmd_promote(a):
    """Raise parked papers back into the pipeline by citation floor. The fix for
    'famous works are parked while obscure neighbours got the budget': candidates
    are re-triaged (default) or fast-tracked to frontier (--to frontier)."""
    con = _db(a.outdir)
    if a.to not in ("candidate", "frontier"):
        out({"error": "--to must be candidate or frontier"}); return
    md = int(_meta(con, "max_depth", "2"))
    rows = con.execute(
        """SELECT id,title,citations FROM papers WHERE status='deferred'
           AND COALESCE(citations,0)>=? AND depth<=?""",
        (a.min_cites, md)).fetchall()
    con.executemany("UPDATE papers SET status=? WHERE id=? AND status='deferred'",
                    [(a.to, r["id"]) for r in rows])
    con.commit()
    out({"promoted": len(rows), "to": a.to, "min_cites": a.min_cites,
         "items": [{"id": r["id"], "citations": r["citations"],
                    "title": r["title"]} for r in rows[:20]]})


def cmd_probe(a):
    """Live-check every backend. Run this whenever a source goes silent -- it
    separates 'no such papers' from 'this channel is down', which is the single
    most common cause of a survey silently under-covering its topic."""
    rows = sources.probe(fetch, a.outdir)
    out({"probed": len(rows),
         "backends": [{"backend": n, "status": s, "n": c, "sample": x}
                      for n, s, c, x in rows],
         "note": "EMPTY on a discovery source means that channel is currently "
                 "unusable; re-run seed with the remaining sources."})


def cmd_status(a):
    con = _db(a.outdir)
    out({"topic": _meta(con, "topic"), "counts": _counts(con),
         "criteria": _meta(con, "criteria"),
         "min_year": _meta(con, "min_year"), "max_depth": _meta(con, "max_depth"),
         "target_papers": _meta(con, "target_papers"),
         "seed_queries_run": _meta(con, "queries_run")})


# ---------------------------------------------------------------------- parser

def main():
    ap = argparse.ArgumentParser(prog="paperq")
    ap.add_argument("--outdir", default="survey")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init");     p.set_defaults(f=cmd_init)
    p.add_argument("--topic", required=True)
    p.add_argument("--min-year", type=int, default=2024)
    p.add_argument("--max-depth", type=int, default=2)
    p.add_argument("--target-papers", type=int, default=40)
    p.add_argument("--min-seed-queries", type=int, default=6)
    p.add_argument("--criteria",
                   help="inclusion/exclusion criteria + core-class definition; "
                        "surfaced in every claim so all workers screen "
                        "consistently (ARS-style PRISMA discipline)")

    p = sub.add_parser("seed");     p.set_defaults(f=cmd_seed)
    p.add_argument("query", nargs="+")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--min-year", type=int)
    p.add_argument("--sources", default="arxiv,crossref,s2",
                   help="comma list: arxiv,s2,crossref,dblp,gscholar "
                        "(add gscholar to reach non-arXiv venue work)")

    p = sub.add_parser("add");      p.set_defaults(f=cmd_add)
    p.add_argument("id", nargs="+")

    p = sub.add_parser("claim");    p.set_defaults(f=cmd_claim)
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--worker")
    p.add_argument("--order", choices=["depth", "cites"], default="depth",
                   help="depth = strict BFS (shallow first); cites = highest-"
                        "citation papers first regardless of depth")

    p = sub.add_parser("expand");   p.set_defaults(f=cmd_expand)
    p.add_argument("id")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--rec-limit", type=int, default=30)
    p.add_argument("--max-candidates", type=int, default=40)
    p.add_argument("--foundational-cites", type=int, default=150)
    p.add_argument("--generic-cites", type=int, default=8000,
                   help="drop older papers above this citation count as "
                        "field-defining classics rather than on-topic work")
    p.add_argument("--require-words", default=DEFAULT_TOPIC_WORDS,
                   help="regex of topic terms; a candidate must match in "
                        "title/abstract unless citations >= --keep-cites. "
                        "Pass empty string to disable")
    p.add_argument("--keep-cites", type=int, default=0,
                   help="papers above this citation count bypass the topic "
                        "filter. Default 0 = no bypass: the survey records only "
                        "topic-domain papers; methodology ancestors (DiT/LDM/CFG "
                        "for a TTS survey) are excluded even if highly cited")
    p.add_argument("--backends", default="s2,s2rec,gscholar,opencit",
                   help="comma list: s2,s2rec,opencit,gscholar. s2rec surfaces "
                        "papers with no citation-graph link; opencit needs a DOI; "
                        "gscholar needs a cluster id from a gscholar seed")

    p = sub.add_parser("probe");    p.set_defaults(f=cmd_probe)

    p = sub.add_parser("promote");  p.set_defaults(f=cmd_promote)
    p.add_argument("--min-cites", type=int, default=50)
    p.add_argument("--to", default="candidate",
                   help="candidate = requires triage; frontier = fast-track")

    p = sub.add_parser("sweep");    p.set_defaults(f=cmd_sweep)
    p.add_argument("--require-words", default=DEFAULT_TOPIC_WORDS)
    p.add_argument("--keep-cites", type=int, default=0)
    p.add_argument("--status", default="deferred,candidate")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("record");   p.set_defaults(f=cmd_record)
    p.add_argument("id")
    p.add_argument("--summary", required=True)
    p.add_argument("--code-url")
    p.add_argument("--code-query")
    p.add_argument("--no-code", action="store_true")
    p.add_argument("--min-summary-chars", type=int, default=80)
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("criteria"); p.set_defaults(f=cmd_criteria)
    p.add_argument("--text", required=True,
                   help="inclusion/exclusion criteria + core-class definition")

    p = sub.add_parser("accept");   p.set_defaults(f=cmd_accept)
    p.add_argument("id"); p.add_argument("--why", required=True)
    p.add_argument("--tier", choices=["core", "ring2"], default="core",
                   help="core = matches the survey's core class (the papers the "
                        "user actually wants to see); ring2 = relevant but "
                        "peripheral. Tag matters: report --tier core filters on it")

    p = sub.add_parser("reject");   p.set_defaults(f=cmd_reject)
    p.add_argument("id", nargs="+"); p.add_argument("--why")

    p = sub.add_parser("pending");  p.set_defaults(f=cmd_pending)
    p.add_argument("--parent")

    p = sub.add_parser("reject-rest"); p.set_defaults(f=cmd_reject_rest)
    p.add_argument("parent")
    p.add_argument("--why", required=True)

    p = sub.add_parser("gate");     p.set_defaults(f=cmd_gate)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--revive", type=int, default=15)

    p = sub.add_parser("list");     p.set_defaults(f=cmd_list)
    p.add_argument("--status"); p.add_argument("--n", type=int, default=50)

    p = sub.add_parser("report");   p.set_defaults(f=cmd_report)
    p.add_argument("--out", default="survey.md")
    p.add_argument("--tier", choices=["all", "core", "ring2"], default="all")

    p = sub.add_parser("status");   p.set_defaults(f=cmd_status)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
