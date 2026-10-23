#!/usr/bin/env python3
"""sources.py -- multi-source paper discovery + citation-graph backends.

Stdlib only, no pip install. Every backend was probed live (2026-09) before
being included; see SKILL.md for the measured status table.

Discovery sources (keyword search):
    arxiv       -- reliable, newest-first, preprints only
    s2          -- relevance ranking, 429s hard without an API key
    crossref    -- published/peer-reviewed work, DOI-native
    dblp        -- CS venue records, intermittently flaky
    gscholar    -- HTML scrape; indexes venue+non-arXiv work nothing else sees

Citation-graph backends (expand a paper):
    s2          -- primary: both directions, arXiv-native
    s2rec       -- S2 recommendations; surfaces papers the graph misses entirely
    opencit     -- OpenCitations, DOI-only, weak on arXiv preprints
    gscholar    -- cited-by via cluster id; catches non-arXiv citing work

Import from paperq.py; also runnable for probing:  python3 sources.py probe
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

S2 = "https://api.semanticscholar.org/graph/v1"
S2_REC = "https://api.semanticscholar.org/recommendations/v1"
ARXIV = "https://export.arxiv.org/api/query"     # https is mandatory (http 301s to empty)
CROSSREF = "https://api.crossref.org/works"
DBLP = "https://dblp.org/search/publ/api"
OPENCIT = "https://opencitations.net/index/api/v1"
GS = "https://scholar.google.com/scholar"

GS_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

S2_FIELDS = "title,year,venue,citationCount,externalIds,abstract,authors,openAccessPdf"

# Extra per-EDGE fields. These separate "this paper studies X" from "this paper
# mentions X once in related work" -- the single biggest noise source in
# citation-graph BFS.
S2_EDGE_FIELDS = S2_FIELDS + ",isInfluential,contexts,intents"

ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")

_STOP = {"for", "the", "a", "an", "of", "in", "on", "and", "to", "with", "via",
         "using", "based", "toward", "towards", "from", "at", "by", "its",
         "their", "this", "that", "are", "is", "be", "as", "we", "our", "llm",
         "llms", "model", "models"}

_BG_RE = re.compile(r"\b(background|such as|e\.g\.|among others|for example|"
                    r"inter alia|and others)\b", re.I)


def topic_terms(topic, extra=None):
    """Content words of the topic string, used for relevance scoring.
    Generic words ('model', 'llm') are dropped: they match everything and would
    flatten the ranking."""
    ts = [t for t in re.findall(r"[a-z0-9]+", (topic or "").lower())
          if t not in _STOP and len(t) > 2]
    for e in (extra or []):
        ts += [t for t in re.findall(r"[a-z0-9]+", e.lower())
               if t not in _STOP and len(t) > 2]
    return sorted(set(ts))


def relevance(rec, terms):
    """Score how likely a candidate actually belongs to the topic.

    Measured on the 200 papers citing the speculative-decoding seed paper,
    with 'on-topic' judged by title keywords:

        no filter                 200 kept   59.5% on-topic
        isInfluential only         17 kept     76%   (recall only 8.5% -- too low to gate on)
        n_contexts >= 3            34 kept     85%
        topic term in abstract    100 kept     87%   (strongest single signal)
        this score, top-40         40 kept     98%

    Weights follow that measurement: title > abstract > context richness,
    isInfluential as a bonus not a gate, background-only phrasing as negative
    evidence.
    """
    if not terms:
        return 0.0
    t = (rec.get("title") or "").lower()
    a = (rec.get("abstract") or "").lower()
    ctx = rec.get("contexts") or []
    s = 0.0
    s += 3.0 * sum(1 for w in terms if w in t)
    s += 2.0 * sum(1 for w in terms if w in a)
    s += 0.8 * min(len(ctx), 4)
    if rec.get("is_influential"):
        s += 3.0
    if ctx and all(_BG_RE.search(c) for c in ctx):
        s -= 2.0
    if not a:
        # missing abstract must not read as irrelevance
        s += 1.0
    return round(s, 2)


def norm_arxiv(s):
    if not s:
        return None
    m = ARXIV_RE.search(str(s))
    return m.group(1) if m else None


def _rec(arxiv=None, s2id=None, doi=None, title=None, year=None, venue=None,
         citations=None, abstract=None, authors=None, gs_cluster=None,
         source=None, ext_url=None, contexts=None, is_influential=None):
    return dict(arxiv=norm_arxiv(arxiv), s2id=s2id, doi=doi, title=title,
                year=year, venue=venue, citations=citations, abstract=abstract,
                authors=authors, gs_cluster=gs_cluster, source=source,
                ext_url=ext_url, contexts=contexts or [],
                is_influential=is_influential)


# ---------------------------------------------------------------- discovery

def arxiv_search(fetch, query, outdir, limit=25, min_year=None):
    if not re.search(r"\b(abs|ti|au|cat|all|co|jr):", query):
        q = query.strip().strip('"')
        query = f'abs:"{q}" OR ti:"{q}"'
    url = f"{ARXIV}?" + urllib.parse.urlencode({
        "search_query": query, "start": 0, "max_results": limit,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    xml = fetch(url, outdir, raw=True)
    if not xml:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    res = []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    for e in root.findall("a:entry", ns):
        pub = e.findtext("a:published", "", ns) or ""
        yr = int(pub[:4]) if pub[:4].isdigit() else None
        if min_year and yr and yr < int(min_year):
            continue
        res.append(_rec(
            arxiv=e.findtext("a:id", "", ns),
            title=" ".join((e.findtext("a:title", "", ns) or "").split()),
            year=yr,
            abstract=" ".join((e.findtext("a:summary", "", ns) or "").split()),
            authors=", ".join(x.findtext("a:name", "", ns)
                              for x in e.findall("a:author", ns)[:6]),
            source="arxiv"))
    return res


def _from_s2(d, source="s2"):
    ext = d.get("externalIds") or {}
    return _rec(arxiv=ext.get("ArXiv"), s2id=d.get("paperId"), doi=ext.get("DOI"),
                title=d.get("title"), year=d.get("year"), venue=d.get("venue"),
                citations=d.get("citationCount"), abstract=d.get("abstract"),
                authors=", ".join(a.get("name", "") for a in (d.get("authors") or [])[:6]),
                source=source)


def s2_search(fetch, query, outdir, limit=20, min_year=None):
    """Free pool 429s constantly -> single attempt, treated as a bonus."""
    p = {"query": query, "limit": limit, "fields": S2_FIELDS}
    if min_year:
        p["year"] = f"{min_year}-"
    d = fetch(f"{S2}/paper/search?{urllib.parse.urlencode(p)}", outdir, tries=1)
    if not d or "data" not in d:
        return []
    return [_from_s2(x) for x in d["data"] if x.get("title")]


def crossref_search(fetch, query, outdir, limit=20, min_year=None):
    """Published/peer-reviewed work. Complements arXiv's preprint-only view."""
    p = {"query.bibliographic": query, "rows": limit,
         "select": "DOI,title,issued,is-referenced-by-count,container-title,author,abstract"}
    if min_year:
        p["filter"] = f"from-pub-date:{min_year}-01-01"
    d = fetch(f"{CROSSREF}?{urllib.parse.urlencode(p)}", outdir)
    items = ((d or {}).get("message") or {}).get("items") or []
    res = []
    for it in items:
        parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        auth = ", ".join(f"{a.get('given','')} {a.get('family','')}".strip()
                         for a in (it.get("author") or [])[:6])
        abst = re.sub(r"<[^>]+>", " ", it.get("abstract") or "").strip() or None
        res.append(_rec(doi=it.get("DOI"),
                        title=(it.get("title") or [None])[0],
                        year=parts[0] if parts else None,
                        venue=(it.get("container-title") or [None])[0],
                        citations=it.get("is-referenced-by-count"),
                        abstract=abst, authors=auth, source="crossref"))
    return [r for r in res if r["title"]]


def dblp_search(fetch, query, outdir, limit=20, min_year=None):
    """CS venue records. Flaky: observed http=000 on repeat calls -- never
    let it be the only source for a query."""
    p = {"q": query, "format": "json", "h": limit}
    d = fetch(f"{DBLP}?{urllib.parse.urlencode(p)}", outdir)
    hits = (((d or {}).get("result") or {}).get("hits") or {}).get("hit") or []
    res = []
    for h_ in hits:
        i = h_.get("info") or {}
        yr = int(i["year"]) if str(i.get("year", "")).isdigit() else None
        if min_year and yr and yr < int(min_year):
            continue
        au = i.get("authors", {}).get("author", [])
        au = [au] if isinstance(au, dict) else au
        res.append(_rec(doi=i.get("doi"), title=i.get("title"), year=yr,
                        venue=i.get("venue"),
                        authors=", ".join(a.get("text", "") for a in au[:6]),
                        ext_url=i.get("ee"), source="dblp"))
    return [r for r in res if r["title"]]


# ------------------------------------------------------------- google scholar

def _gs_parse(page):
    """Parse GS result blocks. Measured: 10/10 blocks expose cluster id and
    cited-by count. Titles/venues come from gs_rt / gs_a."""
    out = []
    blocks = re.findall(
        r'<div class="gs_r gs_or gs_scl".*?'
        r'(?=<div class="gs_r gs_or gs_scl"|<div id="gs_res_ccl_bot")', page, re.S)
    for b in blocks:
        mt = re.search(r'<h3 class="gs_rt".*?>(.*?)</h3>', b, re.S)
        if not mt:
            continue
        title = html.unescape(re.sub(r"<[^>]+>", "", mt.group(1))).strip()
        title = re.sub(r"^\[(PDF|HTML|BOOK|CITATION|B|C)\]\s*", "", title).strip()
        meta = re.search(r'<div class="gs_a">(.*?)</div>', b, re.S)
        meta_txt = html.unescape(re.sub(r"<[^>]+>", "", meta.group(1))) if meta else ""
        yr = re.search(r"\b(19|20)\d{2}\b", meta_txt)
        authors = meta_txt.split(" - ")[0].strip() if " - " in meta_txt else None
        venue = None
        seg = meta_txt.split(" - ")
        if len(seg) >= 2:
            venue = re.sub(r",?\s*(19|20)\d{2}\s*$", "", seg[1]).strip() or None
        cby = re.search(r"Cited by (\d+)", b)
        cid = re.search(r"cites=(\d+)", b)
        arx = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", b)
        doi = re.search(r"(?:doi\.org/|doi[:=])(10\.\d{4,9}/[^\s\"'&<>]+)", b)
        snip = re.search(r'<div class="gs_rs">(.*?)</div>', b, re.S)
        out.append(_rec(
            arxiv=arx.group(1) if arx else None,
            doi=doi.group(1) if doi else None,
            title=title, year=int(yr.group(0)) if yr else None, venue=venue,
            citations=int(cby.group(1)) if cby else None,
            authors=authors,
            abstract=html.unescape(re.sub(r"<[^>]+>", "", snip.group(1))).strip()
            if snip else None,
            gs_cluster=cid.group(1) if cid else None, source="gscholar"))
    return out


def gscholar_search(fetch, query, outdir, limit=20, min_year=None):
    """HTML scrape. Its unique value: indexes conference/journal work that has
    no arXiv version at all. Keep volume low and always cache."""
    p = {"q": query, "hl": "en", "num": min(limit, 20)}
    if min_year:
        p["as_ylo"] = min_year
    page = fetch(f"{GS}?{urllib.parse.urlencode(p)}", outdir, raw=True,
                 headers={"User-Agent": GS_UA}, tries=2)
    if not page:
        return []
    if any(m in page.lower() for m in ("captcha", "unusual traffic", "not a robot")):
        sys.stderr.write("[warn] google scholar is challenging requests; backing off\n")
        return []
    return _gs_parse(page)


def gscholar_citedby(fetch, cluster_id, outdir, limit=20, min_year=None):
    """Forward citations via GS cluster id -- catches citing work that never
    reached arXiv or S2."""
    p = {"cites": cluster_id, "hl": "en", "num": min(limit, 20)}
    if min_year:
        p["as_ylo"] = min_year
    page = fetch(f"{GS}?{urllib.parse.urlencode(p)}", outdir, raw=True,
                 headers={"User-Agent": GS_UA}, tries=2)
    if not page or any(m in page.lower() for m in
                       ("captcha", "unusual traffic", "not a robot")):
        return []
    return _gs_parse(page)


# ----------------------------------------------------------- citation graph

def s2_graph(fetch, pid, outdir, limit=200):
    """Primary citation-graph backend. Returns (records, failed_directions)."""
    res, failed = [], []
    for kind, endpoint, node in (("cited_by", "citations", "citingPaper"),
                                 ("cites", "references", "citedPaper")):
        url = (f"{S2}/paper/{urllib.parse.quote(pid, safe=':')}/{endpoint}"
               f"?limit={limit}&fields={urllib.parse.quote(S2_FIELDS)}")
        d = fetch(url, outdir)
        if not d or not isinstance(d.get("data"), list):
            failed.append(kind)
            continue
        for item in d["data"]:
            p = item.get(node) or {}
            if p.get("title"):
                r = _from_s2(p)
                r["relation"] = kind
                res.append(r)
    return res, failed


def s2_recommend(fetch, pid, outdir, limit=30):
    """S2 recommendation engine -- a genuinely different discovery mechanism.
    Measured: returns on-topic papers with no arXiv ID and zero citation-graph
    connection to the seed, i.e. work pure BFS cannot reach."""
    url = (f"{S2_REC}/papers/forpaper/{urllib.parse.quote(pid, safe=':')}"
           f"?limit={limit}&fields={urllib.parse.quote(S2_FIELDS)}")
    d = fetch(url, outdir, tries=2)
    out = []
    for p in (d or {}).get("recommendedPapers") or []:
        if p.get("title"):
            r = _from_s2(p, source="s2rec")
            r["relation"] = "recommended"
            out.append(r)
    return out


def opencit_citedby(fetch, doi, outdir, limit=200):
    """OpenCitations forward citations. DOI-only and weak on arXiv preprints
    (measured: 5 citations vs S2's 1959 for the same paper), but it is an
    independent index -- useful for published venue work."""
    d = fetch(f"{OPENCIT}/citations/{doi}", outdir, follow=True)
    if not isinstance(d, list):
        return []
    out = []
    for e in d[:limit]:
        citing = e.get("citing")
        if citing:
            r = _rec(doi=citing, source="opencit")
            r["relation"] = "cited_by"
            out.append(r)
    return out


# ------------------------------------------------------------------- probing

DISCOVERY = {"arxiv": arxiv_search, "s2": s2_search, "crossref": crossref_search,
             "dblp": dblp_search, "gscholar": gscholar_search}


def probe(fetch, outdir="."):
    """Live-check every backend. Run this when results look suspicious --
    it distinguishes 'no such paper' from 'this channel is down'.

    Every call is single-attempt: a probe that retries with backoff takes
    minutes and gets killed, which is itself indistinguishable from failure."""
    def f1(url, od, **kw):
        kw["tries"] = 1
        kw.setdefault("timeout", 12)
        return fetch(url, od, **kw)

    rows = []
    for name, fn in DISCOVERY.items():
        try:
            r = fn(f1, "speculative decoding", outdir, 3, 2024)
            rows.append((name, "OK" if r else "EMPTY", len(r),
                         (r[0]["title"] or "")[:45] if r else ""))
        except Exception as e:                                    # noqa: BLE001
            rows.append((name, f"ERROR {type(e).__name__}", 0, str(e)[:45]))

    try:
        g, failed = s2_graph(f1, "arXiv:2211.17192", outdir, 5)
        rows.append(("s2_graph", "OK" if g else "EMPTY", len(g), f"failed={failed}"))
    except Exception as e:                                        # noqa: BLE001
        rows.append(("s2_graph", f"ERROR {type(e).__name__}", 0, str(e)[:45]))
    try:
        rec = s2_recommend(f1, "arXiv:2211.17192", outdir, 5)
        rows.append(("s2_recommend", "OK" if rec else "EMPTY", len(rec), ""))
    except Exception as e:                                        # noqa: BLE001
        rows.append(("s2_recommend", f"ERROR {type(e).__name__}", 0, str(e)[:45]))
    try:
        oc = opencit_citedby(f1, "10.1145/3292500.3330925", outdir, 5)
        rows.append(("opencitations", "OK" if oc else "EMPTY", len(oc), ""))
    except Exception as e:                                        # noqa: BLE001
        rows.append(("opencitations", f"ERROR {type(e).__name__}", 0, str(e)[:45]))
    return rows


if __name__ == "__main__":
    from paperq import fetch as _f          # reuse the cached/backoff fetcher
    print(f"{'backend':<16}{'status':<22}{'n':>4}  sample")
    for n, s, c, x in probe(_f, sys.argv[2] if len(sys.argv) > 2 else "."):
        print(f"{n:<16}{s:<22}{c:>4}  {x}")
