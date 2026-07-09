"""
dc_transcripts.py  —  M5b: earnings-call subtext (Alpha Vantage EARNINGS_CALL_TRANSCRIPT).

Watchlist tickers' latest quarterly call transcripts are scanned for India/GCC
data-centre language through the SAME machinery as SEC filings: dc_edgar.extract_evidence
(KWIC passages) + the SS3 signal judge. Rows are SS3-shaped (form="ECT",
accession="ect-<ticker>-<quarter>") so every downstream consumer (tiers, signals
column, BD trigger-strength) works unchanged.

Free-tier friendly: one request per ticker per run, permanent per-(ticker,quarter)
cache in tender-style JSON (a transcript never changes once published). Non-fatal.
"""
import json
import os
import time
import urllib.request
from datetime import date

import dc_config as dc

CACHE_PATH = os.path.join(os.path.dirname(__file__), "transcript_cache.json")


def _load_cache():
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(c):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, separators=(",", ":"))


def latest_quarter(today=None):
    """The most recent COMPLETED quarter (transcripts publish after quarter end)."""
    t = today or date.today()
    q = (t.month - 1) // 3            # 0-based current quarter; previous = completed
    y = t.year
    if q == 0:
        return f"{y - 1}Q4"
    return f"{y}Q{q}"


def transcript_text(payload):
    """Alpha Vantage payload -> one prose blob (speaker turns joined)."""
    turns = payload.get("transcript") or []
    return " ".join(t.get("content", "") for t in turns if isinstance(t, dict))


def rows_from_text(ticker, company, quarter, text):
    """SS3-shaped row via the SAME KWIC + judge path as filings ('' -> no row)."""
    import dc_edgar
    ev = dc_edgar.extract_evidence(text, "ECT")
    if not ev.get("passages"):
        return None
    row = {"accession": f"ect-{ticker.lower()}-{quarter}",
           "filed_date": f"{quarter[:4]}-{'03 06 09 12'.split()[int(quarter[-1]) - 1]}-30",
           "filer": company, "cik": "", "form": "ECT",
           "url": f"https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol={ticker}&quarter={quarter}"}
    row.update(ev)
    return row


def fetch_all():
    """-> (ss3_rows, health). Non-fatal; [] without ALPHAVANTAGE_API_KEY."""
    key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not key:
        return [], {}
    cache = _load_cache()
    quarter = latest_quarter()
    rows, health = [], {}
    for ticker, company in dc.TRANSCRIPT_TICKERS.items():
        ck = f"{ticker}:{quarter}"
        if ck in cache:                    # permanent: transcript content is immutable
            cached = cache[ck]
            if cached:                     # {} = cached miss (no DC/geo content)
                rows.append(dict(cached))
            continue
        try:
            time.sleep(1.0)                # free tier is rate-limited
            url = (f"https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT"
                   f"&symbol={ticker}&quarter={quarter}&apikey={key}")
            req = urllib.request.Request(url, headers={"User-Agent": "tag-dc-bot/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                payload = json.loads(r.read().decode("utf-8", "ignore"))
            text = transcript_text(payload)
            row = rows_from_text(ticker, company, quarter, text) if text else None
            cache[ck] = {k: v for k, v in (row or {}).items()
                         if k not in ("passages", "window_text")}
            if row:
                rows.append(row)
            health[f"ect:{ticker}"] = 1 if row else 0
        except Exception as exc:
            health[f"ect:{ticker}"] = 0
            print(f"  [transcript {ticker}] {exc}")
    _save_cache(cache)
    return rows, health


def _selfcheck():
    assert latest_quarter(date(2026, 7, 8)) == "2026Q2"
    assert latest_quarter(date(2026, 1, 15)) == "2025Q4"
    text = transcript_text({"transcript": [
        {"speaker": "CEO", "content": "We committed capital expenditure for a new "
                                      "data centre campus expansion in Mumbai, India."},
        {"speaker": "CFO", "content": "Margins were stable."}]})
    row = rows_from_text("EQIX", "Equinix", "2026Q2", text)
    assert row and row["form"] == "ECT" and row["passages"], row
    assert rows_from_text("EQIX", "Equinix", "2026Q2", "Margins were stable.") is None
    print("dc_transcripts self-check: OK")


if __name__ == "__main__":
    _selfcheck()
