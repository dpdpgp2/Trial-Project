# 48h Spotlight + Operators — Cold-Start Build Guide

For a fresh Claude session with no prior context. Read these three in order, then build:

1. **`docs/48H_HIGHLIGHT_AND_OPERATORS_PLAN.md`** — the decision-locked design (WHAT + WHY).
2. **`docs/TAG_BD_CRITERIA.md`** — the rubric passed into every LLM call (grounds ranking).
3. **this file** — the codebase anchors + contracts + acceptance gates (HOW, in THIS repo).

The pipeline runs in **GitHub Actions** (`.github/workflows/dc-pipeline.yml`, `ubuntu-latest`,
25-min timeout, daily cron + `workflow_dispatch`). It commits caches + `dashboard/data.json`
back to `main`; Vercel serves `dashboard/` from `main`. Nothing runs the full pipeline
locally without secrets — but every new module MUST ship a **network-free `demo()`
self-check** (see `dc_govaffairs.py`) that runs with `python3 dc_<module>.py`.

---

## Non-negotiable guardrails (the repo's locked AI discipline)

- **AI may only DROP / LABEL / RANK grounded rows.** It never invents companies, deals,
  dates, ids, or overrides the deterministic role/type/priority. The only human upgrade path
  is the Entity Overrides tab and the Promote flow.
- **id-validation:** every id the model returns is validated against the real input rows and
  dropped if fabricated. Copy the pattern from `dc_ai._validate_tri` (`dc_ai.py:593`).
- **Non-fatal, always:** every new pipeline step is wrapped so a failure prints
  `[module] non-fatal: …` and never breaks the SS1–SS5 pipeline or the export. See how
  `triangulate` and `dc_govaffairs.attach` are called in `dc_pipeline.py`.
- **Cached, cheapest-first:** hash the inputs; unchanged inputs → serve cached, make **no
  call**. Copy `load_cache`/`save_cache` + the `tri_hash` pattern (`dc_ai.py:663`).
- **Minimal diff.** Reuse the helpers below; do not re-implement fetching, JSON parsing,
  scoring, state mapping, or dedup.

---

## Reuse these — do not rebuild

| Need | Use | Location |
|---|---|---|
| Low-level LLM call | `_chat(key, system, user, max_tokens, temperature, reason)` | `dc_ai.py:311` |
| Parse model JSON | `_json_obj(text)` / `_json_array(text)` | `dc_ai.py:483 / 356` |
| Compact evidence index for a prompt | `_ev_index(tabs)` | `dc_ai.py:152` |
| Connection/budget preflight | `test_connection(key)` | `dc_ai.py:296` |
| **Reference implementation to mirror** | `triangulate(ss, tabs, computed, register)` | `dc_ai.py:649` |
| id-validation against candidates | `_validate_tri(obj, cands, …)` | `dc_ai.py:593` |
| Deal-size USD bucket | `dc_bd._deal_usd(deal_value)` | `dc_bd.py:93` |
| Fee-bar check | `dc_bd.fee_viability(r, entities)` | `dc_bd.py:110` |
| States named in text | `dc_states.map_state(text)` | `dc_states.py:62` |
| P1/P2/P3 truth table | `dc_states.targeting_matrix()` | `dc_states.py:82` |
| Policy expiry warnings | `dc_states.validity_flags()` | `dc_states.py` |
| India entity verify (CIN) | `dc_mca.py` (needs `DATA_GOV_IN_API_KEY`) | `dc_mca.py` |
| Foreign filer verify | `dc_edgar.py` (needs `SEC_USER_AGENT`) | `dc_edgar.py` |
| Model id / OpenRouter | `dc.DC_AI_MODEL` (`nvidia/nemotron-3-super-120b-a12b:free`) | `dc_config.py:386` |
| Promote endpoint template | `dashboard/api/ask.js` (password-gate → GitHub Issue) | `dashboard/api/ask.js` |

**Row schemas** (from `dc_sheets.py` / frozen in `dc_export.FROZEN_HEADERS`):
- **SS1 News** = `id, date, source, layer, geo, title, url, summary, sentiment, entities, type, event_id`
- **SS2 Policy** = same article schema (+ policy class)
- **SS3 Disclosure** = `accession, filed_date, filer, cik, form, …, confidence, section, relevance, evidence, url, …`
- **SS4 OSINT** = `id, observed_date, signal_type, actor, geo, layer, magnitude, confidence, url, excerpt` — **not used by the spotlight.**

The pipeline reads these into `a1,a2,a3,a4` and passes `tabs = {"ss1":a1,"ss2":a2,"ss3":a3,"ss4":a4}` (`dc_pipeline.py:241`).

---

## Phase 1 — `docs/TAG_BD_CRITERIA.md`  ✅ DONE

Already written and committed. It's the grounding string; load it into every ranker + judge
prompt. If BD_FACTORS / fee thresholds / state table change in code, update this doc in the
same PR.

## Phase 2 — `dc_spotlight.py` (Feature A core)

**Mirror `triangulate()`.** Signature suggestion:
`spotlight(ss, tabs, register) -> {feed: {generated_at, window_days, status, items, orgs}} | None`.

Per feed in `("ss1","ss2","ss3")`:
1. Filter rows to the last `SPOTLIGHT_DAYS` (2) by `date` / `filed_date`. Empty → skip, no call.
2. Build a compact candidate index; per row attach `deal_usd = dc_bd._deal_usd(...)` bucket
   and `state = dc_states.map_state(text)`.
3. Hash `(feed rows in window + today)`; if unchanged and cached → serve cached, no call.
4. One `_chat` ranker call grounded on `TAG_BD_CRITERIA.md` + `targeting_matrix()`; ask for
   top-`SPOTLIGHT_MAX_PER_FEED` (10) by BD relevance, **fewer if fewer are relevant**.
5. id-validate output against that feed's input rows (drop invented ids).

Then **one judge call** over all feeds' picks → per-feed `useful | widen`. For each `widen`
feed: **loosen the filter inside the 48h window** (pull more candidate rows / drop the
relevance floor — DO NOT extend past 48h), re-rank, re-judge. **Max 2 retries per feed**,
then publish survivors or mark `status:"empty"` (panel hides with a soft note).

Non-fatal wrapper + last-good fallback + deterministic tier/recency fallback ranking.

**Self-check (`demo()`):** stub `_chat` + judge; feed synthetic SS1/SS2/SS3 rows (some in
window, some stale, one feed empty, one feed the judge fails once then passes on widen);
assert: stale rows excluded, invented ids dropped, empty feed skipped, widened feed
re-ranked, never raises. Run: `python3 dc_spotlight.py` → `dc_spotlight self-check OK`.

**Wire in `dc_pipeline.py`** after the evidence register is built (near the `triangulate`
call ~`dc_pipeline.py:283`), wrapped non-fatal.

## Phase 3 — `spotlight` export + dashboard sections

- **`dc_export.py`:** add `"spotlight"` to the payload. Add it to the frozen key list
  (`dc_export.py:34`) and keep `validate()`/`_selfcheck()` (`:306/:441`) green — the export
  self-check fails hard on an unexpected key, so update the frozen contract in the same edit.
- **`dashboard/index.html`:** render a **"Most Important — last 48h"** section at the top of
  each stream view — `viewStreamNews` (`:407`), `viewStreamPolicy` (`:418`),
  `viewStreamDisclosure` (`:426`). Reuse existing row helpers: `titleLink(title,url)` (`:254`),
  `extLink(url)` (`:253`), `shortDate(date)` (`:252`), `esc()` (`:249`). Missing/empty
  `spotlight[feed]` → render nothing (dashboard is graceful). Do **not** add a nav item or a
  home-page hero; do **not** touch `viewStreamOsint` or the Analyst Desk.

**Verify:** dispatch a run (`gh workflow run dc-pipeline.yml`), then screenshot each stream
view with `pixelshot` (serve `dashboard/`, temporarily default `go('home')`→`go('news')` in
a throwaway copy — see prior gov-affairs session for the exact trick).

## Phase 4 — `orgs` extraction (Feature B data)

Add an `orgs` output field to the **News + Disclosure** rankers only (same call, no new
request): value-chain names tagged `operator|energy/power|cooling/coolant|hardware/compute|
transmission/network`. Dedup against `WATCH_OPERATORS_*` (`dc_config.py:226`) + tracked
prospect names before emitting. This just fills the `orgs` array in the Phase-2 contract.

## Phase 5 — `dc_operators.py` (verify + Proposed store)

- **Verify chain (free, off the LLM budget), in order, stop at first hit:**
  `dc_mca.py` (India) → `dc_edgar.py` (foreign) → **Wikidata API** (free/unlimited; add a
  small `urllib` lookup) → hosted Firecrawl search (last resort, credit-capped, cached).
  Record `verified_by` (which source confirmed it).
- **Promotable filter:** only `operator` + cross-border movers become promotable; suppliers
  are surfaced as context only.
- **Store:** `Proposed Operators` sheet tab (`name, segment, evidence_url, status,
  first_seen, verified_by`) + `proposed_operators` array in `data.json`. Expire un-promoted
  rows after 30 days. Add the tab name to `dc_config.py` and a `PROPOSED_OPERATORS_TAB`
  constant alongside the other `*_TAB` names (`dc_config.py:367+`).
- **Self-check:** stub the registries; assert dedup works, suppliers aren't promotable,
  verify-chain stops at first hit, expiry drops stale rows.

## Phase 6 — Promote flow (`promote.js` + next-run merge)

- **`dashboard/api/promote.js`:** clone `ask.js` exactly. Password-gate (reuse
  `ASK_PASSWORD`), then create a GitHub Issue labeled **`promote-operator`** with
  `{name, segment, evidence_url}` JSON in the body. Vercel gets **no Google creds.**
- **Dashboard:** a Proposed Operators panel; each promotable row has a **Promote** button
  that POSTs to `/api/promote` (mirror the Ask-the-Analyst fetch at `index.html:599`).
- **Next-run merge (`dc_operators` + `dc_pipeline`):** read open `promote-operator` issues →
  flip that row's `status` to `approved` in the sheet → **runtime-union** the name into the
  effective watchlist (config lists stay the seed; sheet is the mutable store) → close the
  issue. This is the "promote → added next run" flow; it is eventually-consistent by design.

## Phase 7 — GNews expansion on promote (opt-in)

Approved **foreign** names get appended to the `GNews Foreign Players` query template
(`dc_config.py:51`) so the next run also pulls fresh articles for them. EDGAR per-company is
already covered by `dc_edgar.py`.

---

## Config to add (`dc_config.py`)

```python
SPOTLIGHT_DAYS          = 2
SPOTLIGHT_MAX_PER_FEED  = 10
SPOTLIGHT_MAX_ROWS      = 400          # safety valve vs a feed malfunction
SPOTLIGHT_FEEDS         = ("ss1", "ss2", "ss3")   # OSINT excluded
OPERATOR_SEGMENTS       = ["operator", "energy/power", "cooling/coolant",
                           "hardware/compute", "transmission/network"]
PROPOSED_OPERATORS_TAB  = "Proposed Operators"
PROMOTE_ISSUE_LABEL     = "promote-operator"
```

## Secrets (already GitHub Actions secrets unless noted)

`OPENROUTER_API_KEY`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `DATA_GOV_IN_API_KEY` (MCA),
`SEC_USER_AGENT` (EDGAR), `FIRECRAWL_API_KEY` (tail only), `GITHUB_TOKEN` +
`GITHUB_REPO` + `ASK_PASSWORD` (Vercel, for promote.js — same as ask.js). Wikidata needs
no key.

## Definition of done

- [ ] Each of News/Policy/Disclosure shows a "Most Important — last 48h" top-10 (fewer when
      quiet); OSINT and Analyst Desk unchanged.
- [ ] Judge widens only failing feeds, inside 48h, ≤2 retries; a broken feed hides its panel.
- [ ] Every new module has a passing `python3 dc_<module>.py` self-check.
- [ ] `dc_export._selfcheck()` green with the new `spotlight` + `proposed_operators` keys.
- [ ] Proposed Operators panel + Promote button; a promote creates a `promote-operator` issue;
      the next run flips status to `approved`, unions the name in, closes the issue.
- [ ] Only operators + cross-border movers are promotable; suppliers are context only.
- [ ] Verified live: `gh workflow run dc-pipeline.yml` succeeds, `data.json` regenerates,
      Vercel (`trial-project-nu.vercel.app`, served at `/`) renders it.
- [ ] Steady-state extra LLM budget ≈ 0 on unchanged feeds; ≤ ~7 calls on a fully-fresh run.
