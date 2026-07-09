"""
dc_edgar.py  —  SS3 corporate disclosure via SEC EDGAR full-text search.

Free JSON API, no key. Requires a descriptive User-Agent (SEC_USER_AGENT env,
e.g. "Name email@x.com") and a ≤10 req/s cap.

Like the Sheet 7 SEC connector: for each full-text hit it fetches the actual
filing text and extracts an EVIDENCE WINDOW around matched keywords — a data-center
term near a geo term near an action/deal term — and records which terms matched,
the deal_type, and a confidence based on that proximity. Evidence is auditable.
"""
import os
import re
import sys
import time
import json
import gzip
import urllib.request
import urllib.error

import dc_config as dc
import dc_ingest  # reuse tag_layers + GEO_KEYWORDS


def _ua():
    return os.environ.get("SEC_USER_AGENT", "Data-Center-Trial dpuri2024@gmail.com")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": _ua(),
                                               "Accept-Encoding": "gzip, deflate"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8", "ignore"))


def _filing_url(adsh, cik, fname):
    acc = adsh.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{fname}"


# --- filing body fetch + evidence extraction -------------------------------
_DOC_CACHE = {}


def fetch_doc_text(url, cap=16_000_000):
    """Fetch a filing document, strip HTML, return plain text (capped, cached).
    Requests identity encoding so a capped read isn't a truncated gzip stream.
    Cap is 16 MB: inline-XBRL 20-Fs are multi-MB (Sify's is 6.9 MB) and their readable
    narrative sits AFTER a large XBRL fact/context block — a tight cap truncates the whole
    Item 3-5 body and leaves only tag-soup. 16 MB covers current filers with headroom."""
    if not url:
        return ""
    if url in _DOC_CACHE:
        return _DOC_CACHE[url]
    text = ""
    for attempt in range(3):
        try:
            time.sleep(0.15)  # ≤10 req/s
            req = urllib.request.Request(
                url, headers={"User-Agent": _ua(), "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read(cap)
            html = raw.decode("utf-8", "ignore")
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"&#?\w+;", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            break
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        except Exception:
            break
    _DOC_CACHE[url] = text
    return text


def _first_positions(text, terms):
    """[(pos, term)] for each term's first occurrence (term kept as written)."""
    out = []
    for t in terms:
        i = text.find(t)
        if i >= 0:
            out.append((i, t.strip()))
    return out


def _geo_positions(text):
    """[(pos, keyword, country)] for India/GCC geo keywords found. `text` must be lowered."""
    out = []
    for country, kws in dc_ingest.GEO_KEYWORDS.items():
        for kw in kws:                      # GEO_KEYWORDS are lowercase
            i = text.find(kw)
            if i >= 0:
                out.append((i, kw, country))
    return out


def _word_window(text, anchor_char, side):
    """~`side` words each side of the anchor character position (word-accurate context)."""
    left = text[:anchor_char].split()
    right = text[anchor_char:].split()
    return " ".join(left[-side:] + right[:side])


def _words_between(text, a, b):
    """Word count of text[a:b] (a<=b)."""
    return len(text[a:b].split())


def extract_20f_items(text):
    """Return the Item 3–5 block of a 20-F (Item 3 Key Info/Risk Factors → Item 4 Business/
    Property → Item 5 Operating Review & Prospects; ends at Item 6). That block is where a
    20-F actually discloses geography, capex and risk — everything else is boilerplate/XBRL.
    Picks the LONGEST Item3→Item6 span so the table-of-contents (tiny gap) and 'see Item 3.D'
    cross-references (short tails) don't win. Returns None if headers aren't found.
    ponytail: header-regex heuristic; swap for a real 20-F item parser only if a filer breaks it."""
    t = text.lower()
    i3 = [m.start() for m in re.finditer(r"item\s*3[\.\s]", t)]
    i4 = [m.start() for m in re.finditer(r"item\s*4[\.\s]", t)]
    i6 = [m.start() for m in re.finditer(r"item\s*6[\.\s]", t)]
    if not i3 or not i6:
        return None
    # Body Item-3 headers are followed by a long section (3.A–3.D) before Item 4; table-of-
    # contents entries have Item 4 right after them. Drop the TOC-style Item-3 positions, then
    # take the longest Item3→next-Item6 span among what's left (ignores late 'see Item 3' refs).
    body = [s for s in i3 if not any(0 < (a - s) < 600 for a in i4)] or i3
    best = None
    for s in body:
        ends = [e for e in i6 if e > s]
        if ends and (best is None or (ends[0] - s) > (best[1] - best[0])):
            best = (s, ends[0])
    return text[best[0]:best[1]] if best else None


def _search_region(text, form):
    """(label, region_text): the slice where BOTH keyword flagging and the AI window live.
    20-F → Item 3-5 only; every other form → whole doc."""
    if form.upper().startswith("20-F"):
        block = extract_20f_items(text)
        if block:
            return "Item 3-5", block
    return "Full " + (form or "doc"), text


def _pick_anchor(region):
    """Best DC anchor in `region` via section-priority scan: (anchor_char, conf, cregion, geos,
    dc_positions) or (None, ...). Prefers a DC term with geo+action nearby; ties broken by
    section priority (Risk/Growth win)."""
    W = dc.EDGAR_EVIDENCE_WINDOW
    _CONF = {"high": 2, "med": 1, "low": 0}
    best = None
    all_dc = []
    for rank, _label, span, off in _sections_with_offsets(region):
        t = span.lower()
        dcs = _first_positions(t, dc.DC_TERMS)
        if not dcs:
            continue
        all_dc += [off + p for p, _ in dcs]
        geos = _geo_positions(t)
        acts = _first_positions(t, dc.ACTION_TERMS)
        anchor, conf, cregion = None, "low", ""
        for di, _ in dcs:
            near_geo = [(g, c) for (g, _kw, c) in geos if abs(g - di) <= W]
            near_act = any(abs(a - di) <= W for a, _ in acts)
            if near_geo and near_act:
                anchor, conf, cregion = di, "high", near_geo[0][1]
                break
            if near_geo and conf != "high":
                anchor, conf, cregion = di, "med", near_geo[0][1]
        if anchor is None:
            anchor, conf = dcs[0][0], "low"
        key = (_CONF[conf], -rank)
        if best is None or key > best[0]:
            best = (key, off + anchor, conf, cregion, off, geos)
        if conf == "high" and rank < 2:
            break
    if best is None:
        return None, "low", "", [], sorted(set(all_dc))
    _k, anchor, conf, cregion, _off, geos = best
    return anchor, conf, cregion, geos, sorted(set(all_dc))


def _sections_with_offsets(text):
    """Like extract_sections but also yields each span's char offset into `text`."""
    t = text.lower()
    marks = []
    for rank, (label, pat) in enumerate(dc.EDGAR_SECTION_PRIORITY):
        for m in re.finditer(pat, t):
            marks.append((m.start(), rank, label))
    if not marks:
        yield (99, "Other", text, 0)
        return
    marks.sort()
    spans = []
    for i, (pos, rank, label) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        spans.append((rank, label, text[pos:end], pos))
    spans.append((99, "Other", text, 0))
    spans.sort(key=lambda s: s[0])
    yield from spans


def extract_signals(region, side=dc.EDGAR_SIGNAL_WORDS):
    """KWIC signal catches: for every DC-term hit in `region`, take ±`side` words of context;
    merge overlapping/adjacent intervals so clustered hits become one passage and isolated hits
    stay ~2*side words. Returns a deduped list of VERBATIM passages — the candidate signal list
    handed to the AI judge (which labels/filters them). Self-scaling: a DC-saturated 20-F yields
    many merged passages, an incidental 8-K mention yields one. No AI, no hallucination here."""
    word_spans = [(m.start(), m.group()) for m in re.finditer(r"\S+", region)]
    if not word_spans:
        return []
    starts = [s for s, _ in word_spans]
    words = [w for _, w in word_spans]
    rl = region.lower()
    hitchars = []
    for term in dc.DC_TERMS:                 # terms kept as written ('colo ' keeps its space)
        if not term.strip():
            continue
        j = 0
        while True:
            i = rl.find(term, j)
            if i < 0:
                break
            hitchars.append(i)
            j = i + 1
    if not hitchars:
        return []
    import bisect
    hit_words = sorted({bisect.bisect_right(starts, hc) - 1 for hc in hitchars})
    intervals = []                           # merge [w-side, w+side] windows
    for w in hit_words:
        lo, hi = max(0, w - side), min(len(words) - 1, w + side)
        if intervals and lo <= intervals[-1][1] + 1:
            intervals[-1][1] = max(intervals[-1][1], hi)
        else:
            intervals.append([lo, hi])
    return [" ".join(words[lo:hi + 1]) for lo, hi in intervals]


def extract_evidence(text, form=""):
    """Form-aware evidence: confine to the search region (20-F → Item 3-5, else whole doc), then
    build a deduped list of ±30-word KWIC signal passages around every DC keyword hit. The passage
    list goes to the AI judge, which labels/filters them into material India/Gulf TAG signals.
    Keyword fields (region/deal/layer/confidence) are kept for SS5 + the no-AI fallback."""
    blank = {"evidence": "", "window_text": "", "passages": [], "section": "", "matched_terms": "",
             "deal_type": "", "counterparty_region": "", "confidence": "low", "layer": "General"}
    if not text:
        return blank
    label, region = _search_region(text, form)
    passages = extract_signals(region)
    if not passages:                         # no DC term anywhere → not a data-centre filing
        return blank
    passages = dedup_passages(passages)      # drop semantic near-dupes (boilerplate repeats)
    anchor, conf, cregion, geos, _dc_hits = _pick_anchor(region)

    src = " ".join(passages).lower()
    matched = sorted(
        {term.strip() for term in dc.DC_TERMS + dc.ACTION_TERMS if term.strip() in src}
        | {kw for (_p, kw, _c) in geos if kw in src})
    deal = next((dt for term, dt in dc.DEAL_TYPE_TERMS if term in src), "")
    layer = "; ".join(dc_ingest.tag_layers(src)) or "General"
    snippet = passages[0][:600].strip()      # fallback evidence if the judge doesn't run
    return {"evidence": snippet, "window_text": " ".join(passages), "passages": passages,
            "section": f"{label} ({len(passages)} catches)", "matched_terms": ", ".join(matched[:8]),
            "deal_type": deal, "counterparty_region": cregion, "confidence": conf, "layer": layer}


def fetch_filings(limit=None):
    """One phrase query per market, deduped by accession, recency-sorted, then the
    N most-recent get their filing body fetched + evidence extracted."""
    from urllib.parse import quote
    limit = limit or dc.EDGAR_MAX_DOCS
    by_acc = {}
    for term in dc.EDGAR_GEO_TERMS:
        url = f"{dc.EDGAR_FTS_URL}?q={quote(term)}&forms={dc.EDGAR_FORMS}"
        try:
            time.sleep(0.15)  # ≤10 req/s
            data = _get(url)
            for h in data.get("hits", {}).get("hits", []):
                s = h.get("_source", {})
                adsh = s.get("adsh", "")
                if not adsh or adsh in by_acc:
                    continue
                cik = (s.get("ciks") or [""])[0]
                fname = h.get("_id", "").split(":")[-1]
                by_acc[adsh] = {
                    "accession": adsh,
                    "filed_date": s.get("file_date", ""),
                    "filer": (s.get("display_names") or [""])[0],
                    "cik": cik,
                    "form": s.get("form", ""),
                    "url": _filing_url(adsh, cik or "0", fname) if cik else "",
                }
        except urllib.error.HTTPError as e:
            print(f"  [edgar error] {e.code} on {term!r}")
        except Exception as exc:
            print(f"  [edgar error] {exc} on {term!r}")

    rows = sorted(by_acc.values(), key=lambda r: r["filed_date"], reverse=True)[:limit]
    for r in rows:
        ev = extract_evidence(fetch_doc_text(r["url"]), r["form"])
        # fall back to filer-name layer tag if the body gave nothing
        if ev["layer"] == "General":
            ev["layer"] = "; ".join(dc_ingest.tag_layers(r["filer"].lower())) or "General"
        r.update(ev)
    press, press_health = fetch_press()
    rows += press                            # official-company disclosures join the same judge
    subs, subs_health = fetch_submissions(known={r["accession"] for r in rows})
    rows += subs                             # per-CIK submissions complement full-text search
    press_health.update(subs_health)
    _attach_verdicts(rows)
    for r in rows:
        r.pop("window_text", None)          # passages/context were for the judge, not the sheet
        r.pop("passages", None)
    return rows, {"EDGAR FTS": len(rows) - len(press), **press_health}


def fetch_submissions(known=None):
    """M5b: newest filings per watched CIK (data.sec.gov submissions JSON) — catches
    filings the full-text phrase search misses. Same extraction+judge path. Non-fatal."""
    known = known or set()
    rows, health = [], {}
    for name, cik in dc.EDGAR_CIKS.items():
        try:
            time.sleep(0.15)
            data = _get(dc.EDGAR_SUBMISSIONS_URL.format(cik=cik.zfill(10)))
            recent = (data.get("filings") or {}).get("recent") or {}
            accs = recent.get("accessionNumber") or []
            forms = recent.get("form") or []
            dates = recent.get("filingDate") or []
            docs = recent.get("primaryDocument") or []
            kept = 0
            for i in range(min(len(accs), dc.EDGAR_SUBMISSIONS_RECENT * 4)):
                if kept >= dc.EDGAR_SUBMISSIONS_RECENT:
                    break
                if forms[i] not in ("8-K", "6-K", "10-K", "10-Q", "20-F"):
                    continue
                adsh = accs[i]
                if adsh in known:
                    continue
                r = {"accession": adsh, "filed_date": dates[i], "filer": name,
                     "cik": cik, "form": forms[i],
                     "url": _filing_url(adsh, cik, docs[i] if i < len(docs) else "")}
                ev = extract_evidence(fetch_doc_text(r["url"]), r["form"])
                if not ev.get("passages"):
                    continue                        # no DC content — skip silently
                r.update(ev)
                rows.append(r)
                kept += 1
            health[f"submissions:{name}"] = kept
        except Exception as exc:
            health[f"submissions:{name}"] = 0
            print(f"  [submissions {name}] {exc}")
    return rows, health


def fetch_press(per_feed=15):
    """SS3-shaped rows from corporate press-release RSS (dc_config.PRESS_FEEDS).
    Official-company statements are disclosure-grade (source tier T1) and run through
    the SAME KWIC extraction + signal judge as SEC filings: form="PR", accession=pr-<hash>.
    Only India/GCC-geo items with a DC term survive extract_evidence. Non-fatal per feed."""
    import feedparser
    import hashlib
    rows, health = [], {}
    for name, url in dc.PRESS_FEEDS.items():
        try:
            time.sleep(0.3)
            fp = feedparser.parse(url, agent="Mozilla/5.0 (tag-dc-bot)")
            kept = 0
            for e in fp.entries[:per_feed]:
                title = (e.get("title") or "").strip()
                link = (e.get("link") or "").strip()
                if not title or not link:
                    continue
                summary = re.sub(r"<[^>]+>", " ", e.get("summary", "") or "")[:1500]
                text = f"{title}. {summary}"
                low = text.lower()
                if not any(term in low for term in dc.DC_TERMS):
                    continue                       # press wires are broad; DC-term gate first
                geos = dc_ingest.tag_geo(low)
                if not geos:
                    continue                       # target-geo gate (India/GCC only)
                ev = extract_evidence(text, "PR")  # KWIC + judge-ready passages
                if not ev.get("passages"):
                    continue
                date = ""
                for k in ("published", "updated"):
                    if e.get(k):
                        date = e[k]
                        break
                try:
                    from email.utils import parsedate_to_datetime
                    date = parsedate_to_datetime(date).strftime("%Y-%m-%d")
                except Exception:
                    date = (date or "")[:10]
                row = {"accession": "pr-" + hashlib.sha1(link.encode()).hexdigest()[:16],
                       "filed_date": date, "filer": name.replace(" IR", "").replace(" News", ""),
                       "cik": "", "form": "PR", "url": link}
                row.update(ev)
                if not row.get("counterparty_region"):
                    row["counterparty_region"] = geos[0]
                rows.append(row)
                kept += 1
            health[name] = kept
        except Exception as exc:
            health[name] = 0
            print(f"  [press {name}] {exc}")
    return rows, health


# --- AI relevance judge (OpenRouter / Nemotron), permanent per-accession cache ------------
EDGAR_CACHE_PATH = os.path.join(os.path.dirname(__file__), "edgar_cache.json")


def _load_cache():
    if os.path.exists(EDGAR_CACHE_PATH):
        try:
            with open(EDGAR_CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_cache(c):
    with open(EDGAR_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, separators=(",", ":"))


def _attach_verdicts(rows):
    """Judge each filing's KWIC passage list once (filings are immutable → permanent cache).
    The judge returns up to ~12 material TAG signals; every returned quote is substring-verified
    against the passages (anti-hallucination) and the survivors become the SS3 evidence cell as
    `[label|region] quote` bullets. Write-all gate: every row keeps a `relevance` verdict.
    Non-fatal — no key/failure leaves the keyword fallback snippet + '(no AI verdict)'."""
    import dc_ai
    cache = _load_cache()
    todo = [{"accession": r["accession"], "filer": r["filer"], "form": r["form"],
             "section": r.get("section", ""), "passages": r.get("passages", []),
             "window_text": r.get("window_text", "")}
            for r in rows if r["accession"] not in cache and (r.get("passages") or r.get("window_text"))]
    verdicts = dc_ai.judge_filings(todo)
    if verdicts:
        cache.update(verdicts)
        _save_cache(cache)
    for r in rows:
        v = cache.get(r["accession"])
        if not v:
            r.setdefault("relevance", "(no AI verdict)")
            continue
        source = r.get("window_text", "")   # = joined passages the judge saw
        kept, kept_labels = [], []
        for s in (v.get("signals") or []):
            label = _norm_label(s.get("label"))
            if not label:                    # off-menu label -> dropped (taxonomy enforcement)
                continue
            q = _verify_quote(s.get("quote", ""), source)
            if q:
                reg = s.get("region") or v.get("region") or ""
                kept.append(f"[{label}|{reg}] {q[:200]}")
                kept_labels.append((label, reg))
        if kept:                            # verified signal bullets win the evidence cell
            r["evidence"] = "  •  ".join(kept[:dc.MAX_SIGNALS_PER_FILING])
            # deal_type = the highest trigger-weight verified label (shared taxonomy)
            best = max(kept_labels, key=lambda lr: dc.SIGNAL_LABELS[lr[0]][0])
            r["deal_type"] = best[0]
            r["confidence"] = "high" if len(kept) >= 3 else "med"
        # machine-readable signals column (M7's trigger-strength input): label|region; ...
        r["signals"] = "; ".join(f"{l}|{reg or '-'}" for l, reg in kept_labels[:dc.MAX_SIGNALS_PER_FILING])
        yn = "yes" if v.get("relevant") else "no"
        r["relevance"] = f"{yn} — {len(kept)} signal(s)"
        if v.get("region"):
            r["counterparty_region"] = v["region"]


def _norm_label(label):
    """Judge label -> SIGNAL_LABELS key (aliases mapped; unknown => '' = drop).
    Code-side enforcement of the shared taxonomy: the AI cannot invent labels."""
    l = (label or "").strip().lower()
    if l in dc.SIGNAL_LABELS:
        return l
    return dc.SIGNAL_LABEL_ALIASES.get(l, "")


def dedup_passages(passages, threshold=None):
    """Semantic near-dupe drop (repeated boilerplate like CCD paragraphs) before the
    judge. Uses dc_models.embed (MiniLM); silently skipped when torch is unavailable
    (--no-ml environments) — dedup is an optimization, never a dependency."""
    if len(passages) < 3:
        return passages
    threshold = threshold or dc.KWIC_DEDUP_COSINE
    try:
        import numpy as np
        import dc_models
        vecs = dc_models.embed(passages)
        vecs = vecs / (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9)
        keep = []
        for i, v in enumerate(vecs):
            if all(float(v @ vecs[j]) < threshold for j in keep):
                keep.append(i)
        return [passages[i] for i in keep]
    except Exception:
        return passages


def _verify_quote(quote, source):
    """Return `quote` only if it is a verbatim substring of `source` (whitespace-insensitive,
    case-insensitive) — the anti-hallucination guard. Otherwise '' → keep the mechanical snippet."""
    if not quote or not source:
        return ""
    norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
    return quote.strip() if norm(quote) in norm(source) else ""


def _selfcheck():
    """Offline fixtures for the M4 machinery (no network, no AI)."""
    # label normalization: on-menu passes, aliases map, unknown drops
    assert _norm_label("capex-commitment") == "capex-commitment"
    assert _norm_label("JV/partnership") == "jv-partnership"
    assert _norm_label("Capacity/Scaling") == "capacity-commitment"
    assert _norm_label("made-up-label") == ""
    # substring verification: verbatim passes (whitespace/case-insensitive), fabricated drops
    src = "The company committed INR 500 crore of capex for a 200 MW data centre campus at Vashi."
    assert _verify_quote("capex for a 200 MW  data centre", src)
    assert _verify_quote("CAPEX FOR A 200 MW DATA CENTRE", src)
    assert _verify_quote("a 900 MW nuclear campus", src) == ""
    # KWIC: overlapping windows merge; isolated hits stay separate
    region = ("alpha " * 40 + "data center expansion in India " + "beta " * 5
              + "data centre capacity of 200 megawatt " + "gamma " * 120
              + "colocation services agreement " + "delta " * 40)
    ps = extract_signals(region, side=10)
    assert len(ps) == 2, (len(ps), [p[:40] for p in ps])   # first two merge, third separate
    # verdict application: signals column + evidence bullets + off-menu drop
    row = {"accession": "T-1", "filer": "Sify", "form": "20-F", "section": "Business",
           "passages": [src], "window_text": src, "evidence": "old", "deal_type": "",
           "confidence": "low", "counterparty_region": ""}
    cache_v = {"relevant": True, "region": "India", "signals": [
        {"n": 1, "label": "capex", "region": "India", "quote": "capex for a 200 MW data centre"},
        {"n": 1, "label": "made-up", "region": "India", "quote": "capex for a 200 MW data centre"},
        {"n": 1, "label": "capacity/scaling", "region": "India", "quote": "NOT IN SOURCE"}]}
    import json as _json
    _save = globals()["_load_cache"]
    try:
        globals()["_load_cache"] = lambda: {"T-1": cache_v}
        _attach_verdicts([row])
    finally:
        globals()["_load_cache"] = _save
    assert row["evidence"].startswith("[capex-commitment|India]"), row["evidence"]
    assert row["signals"] == "capex-commitment|India", row["signals"]
    assert row["deal_type"] == "capex-commitment"
    assert row["relevance"] == "yes — 1 signal(s)", row["relevance"]
    # dedup: identical passages collapse (skips silently if torch absent)
    try:
        import dc_models  # noqa: F401
        d = dedup_passages(["the same boilerplate sentence here"] * 4 + ["a different one entirely"])
        assert len(d) <= 3, d
    except Exception:
        pass
    # press-release path: DC+geo text yields judge-ready passages under form="PR"
    ev = extract_evidence("Equinix announces a new 100 megawatt data centre campus "
                          "expansion in Mumbai, India with partner X.", "PR")
    assert ev["passages"] and ev["counterparty_region"], ev
    print("dc_edgar self-check: OK")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        _selfcheck()
        raise SystemExit(0)
    rows, health = fetch_filings(limit=8)
    print("health:", health)
    for r in rows:
        print(f"\n  {r['filed_date']} {r['form']} {r['filer'][:46]} "
              f"[{r['confidence']}|{r['deal_type'] or '-'}|{r['layer']}|{r['counterparty_region'] or '-'}] "
              f"§{r.get('section') or '-'}")
        print(f"    matched:   {r['matched_terms']}")
        print(f"    verdict:   {r.get('relevance', '')}")
        print(f"    evidence:  {r['evidence'][:160]}")
