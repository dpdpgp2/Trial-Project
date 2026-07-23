# Finalized Plan — Per-Feed 48h Highlight + OPERATORS Expansion

Status: **finalized, revised 2026-07-24** (supersedes the original single-call design). Targets
current `main` (post gov-affairs feature, post `dc_ai` rewrite). Scope: the AI-ranked
"Most Important — last 48h" highlight (now **per feed**) and the OPERATORS value-chain
expansion. Every design fork the team decided is marked **LOCKED**.

Runtime reality that shapes everything: the pipeline runs in **ephemeral GitHub Actions**
(`ubuntu-latest`, 25-min timeout, daily cron `41 5 * * *` + manual dispatch). No persistent
host — so no self-hosted services; verification leans on free APIs already in the repo.

---

## Prerequisite — `docs/TAG_BD_CRITERIA.md` (the grounding rubric)

The single source of truth that grounds every ranker + the judge. Consolidates what is
currently scattered across `BD_FACTORS` (dc_config), `dc_bd.fee_viability`, and
`knowledge/india_state_bank.md`. Contents (finalized):

- **Engagement:** ~$50k/mo retainer (~$600k/yr) for India market-entry advisory — state
  selection, land + power coordination, government & regulatory affairs, incentive
  capture, JV/partner selection.
- **Ideal client (ranks high):** cross-border mover (foreign/GCC entering or
  first-expanding in India) · clears the fee bar (deal ≥ $50M floor, ≥ $500M strong, **or**
  mega-fund/sovereign backer) · active trigger (land/capex/capacity/JV/energy) · attractive
  state (P1: Maharashtra, UP, Telangana, TN, AP) · novel.
- **Disqualifiers:** hyperscalers (can pay, can't win — now carry the `⚠ gov-affairs`
  badge) · entrenched domestic incumbents · sub-$50M · T3 chatter.
- **LOCKED:** affordability is a *gate*, not the ranking axis. Retainer = **scoring
  signal**, not a hard floor.

---

## Feature A — Per-feed "Most Important — last 48h"

Each source feed **except OSINT** gets its own AI-ranked 48h highlight, shown at the top of
that feed's stream view. A single judge pass then gates all of them for usefulness and
data-stream health, with a bounded widen-and-retry loop for any feed that fails.

This is the codebase's existing **retrieve → judge → widen** pattern (`dc_ai.py:704`,
`MAX_PASSES, BASE_ID_BUDGET, WIDEN_STEP = 3, 12, 10`), applied per feed.

### LOCKED decisions

- **Feeds ranked (one call each):** **SS1 News · SS2 Policy · SS3 Disclosures.**
  **SS4 OSINT is excluded** (job postings / Reddit are not "most important news").
- **Window = last 2 days** (`SPOTLIGHT_DAYS = 2`). Each ranker sees only its own feed's
  last-48h rows. Empty feed → skip its call entirely, hide its panel.
- **Top 10 per feed**, ranked by BD relevance for TAG, grounded on `TAG_BD_CRITERIA.md`
  + the P1-state list from `dc_states.targeting_matrix()`.
- **Grounding hint per row:** pass the *already-computed* `deal_usd` bucket
  (`dc_bd._deal_usd`) and matched state (`dc_states.map_state`) alongside each row, so
  "high deal value / attractive state" is judged on real extraction, not headline-guessing.
  (Policy rows carry no deal value — pass what applies.)
- **Judge pass (one call, over all feeds' picks):** returns a **per-feed** verdict —
  `useful` or `widen`. Its job is NOT hallucination (see below) but quality + stream
  health: catch a feed that returned technically-real-but-useless picks, or a stream that
  is broken/stale this window.
- **Widen (LOCKED semantics):** **stay inside the 48h window, loosen the filter** — pull
  more candidate rows / drop the relevance bar for the failing feed(s) only, then re-rank
  and re-judge. **Never extend the window past 48h.** Bounded: **max 2 retries per feed**,
  then publish what survives or hide the panel with a soft "nothing material in the last
  48h" note.
- **Anti-hallucination (already handled upstream):** every ranker's output ids are
  validated against that feed's real input rows; invented ids are dropped before the judge
  ever runs — same guard as `triangulate` / Ask-the-Analyst. So the judge is a *usefulness*
  gate layered on top of a hard *existence* gate.
- **Non-fatal + cached:** mirror `triangulate()` — per-feed hash over (feed's in-window
  rows + date); unchanged feed serves cached with **no call**; any failure falls back to
  deterministic tier+recency ranking and the last good result. A bad spotlight never
  breaks the pipeline or the data export.

### Output contract (per feed)

```
spotlight[feed] = {
  "generated_at": "...", "window_days": 2, "status": "ok|cached|widened|empty",
  "items": [ { "id", "rank", "reason", "criteria_hits": [...] } ],   # top 10, id-validated
  "orgs":  [ ... ]                                                   # Feature B, News+Disclosure only
}
```

### Render (LOCKED)

A **"Most Important — last 48h"** section at the top of each of the three stream views —
News, Policy, Disclosures — using the existing article-row markup (`titleLink`/`extLink`/
`shortDate`), same article + link, just the ranked top slice. No new nav item; no repeat on
the Overview home. The existing **Analyst Desk** (corroborated, actionable plays with
act-by dates) stays a separate lens and is untouched.

---

## Feature B — OPERATORS Expansion (value-chain discovery → Proposed queue → promote)

Rides **free** on top of Feature A: the News + Disclosures rankers already read every
in-window row, so they emit an extra `orgs` field — value-chain company names extracted
from the ranked news — at **no extra LLM call**. Verification then uses **free registries
already in the repo**, so the queue is not credit-limited at realistic (human-gated) volume.

### LOCKED decisions

- **Extraction:** the News + Disclosure ranker calls tag **DC value-chain company names**
  by segment: **operator, energy/power, cooling/coolant, hardware/compute,
  transmission/network**. (Policy ranker does not extract orgs.)
- **Promotable scope (LOCKED — Option A from the session):** only **operators + cross-border
  movers** become promotable prospects (the names TAG can actually advise). Pure suppliers
  (energy/cooling/hardware/transmission) may be surfaced as context but are **not**
  promoted/scored. Keeps the queue high-signal.
- **Verification chain (LOCKED — free-registry first, no self-hosted crawler):**
  1. **MCA** (`dc_mca.py`) — authoritative India entity resolution (CIN-backed), free, cached.
  2. **EDGAR** (`dc_edgar.py`) — foreign filers, free, no key.
  3. **Wikidata API** — free, unlimited, structured; the open-web tail ("is this a real
     company, what does it do").
  4. **Hosted Firecrawl search** — last-resort tail only, credit-capped, cached once-ever.
  These are HTTP/registry lookups, **not** LLM calls, and run only on human-promoted names,
  so they don't touch the LLM budget. **No self-hosted crawler / headless browser** — from
  CI datacenter IPs it gets captcha'd (the reason gov-affairs uses a search API), and
  Firecrawl-self-hosted needs a persistent host CI doesn't provide. Parked as a separate
  infra project if bulk open-web crawling is ever actually needed.
- **Proposed queue, human promotes (LOCKED — repo's AI boundary):** AI writes ONLY to a
  `Proposed Operators` store — nothing is scored until a human promotes it.
- **Promote mechanism (LOCKED — mirror `ask.js`, not direct sheet writes):** the dashboard
  Promote button hits `dashboard/api/promote.js`, which — exactly like `ask.js` —
  **password-gates and drops a GitHub Issue** (label `promote-operator`). Vercel gets **no
  Google-Sheets credentials**; the pipeline (which has them) does the write. **Next
  pipeline run:** reads open `promote-operator` issues → flips the sheet row to
  `status=approved` → **runtime-unions** the name into the effective watchlist → closes the
  issue.
- **Watchlist merge = runtime union (LOCKED):** `WATCH_OPERATORS_*` (`dc_config.py:226`) are
  Python lists the pipeline can't rewrite at runtime. So the `Proposed Operators` sheet tab
  is the **mutable store**; the config lists stay the **seed**; the pipeline unions
  `approved` rows in-memory each run. Reversible (un-approve in the sheet).
- **Retrieval expansion on promote (opt-in):** matching auto-expands for free the moment a
  name enters the watchlist. To also pull *new* articles, approved foreign names get
  appended to the one company-parameterized feed (`GNews Foreign Players`,
  `dc_config.py:51`). EDGAR per-company lookup already exists via `dc_edgar.py`.

### Store

`Proposed Operators` sheet tab (`name, segment, evidence_url, status, first_seen,
verified_by`) + `proposed_operators` array in `data.json`. Persisted like the other caches.
Dedup on write against existing `WATCH_OPERATORS_*` + tracked prospects so we never propose
a name already covered. Stale un-promoted rows expire after 30 days.

---

## Shared — the daily LLM budget

Per run: **3 per-feed rankers + 1 judge = 4 calls baseline** (News/Disclosure rankers also
emit `orgs`, folding extraction in for free). Widen retries add at most **2 calls per
failing feed**, worst case ~6–7; typical steady-state is **0** (per-feed hash caching skips
unchanged feeds). All built on the existing `dc_ai._chat`, id-validated, cached, non-fatal.
Verification lookups (MCA/EDGAR/Wikidata/Firecrawl) are free/registry calls off the LLM
budget, human-gated and cached.

---

## Files touched

| File | Change |
|---|---|
| `docs/TAG_BD_CRITERIA.md` | new — the rubric that grounds every ranker + judge |
| `dc_spotlight.py` | new — per-feed rankers + judge + widen loop + `orgs` extraction; mirrors `triangulate()` (cached, id-validated, non-fatal) |
| `dc_operators.py` | new — Proposed queue: dedup, verify chain (MCA→EDGAR→Wikidata→Firecrawl), read approved issues, runtime-union into watchlist |
| `dc_config.py` | `SPOTLIGHT_DAYS=2`, `SPOTLIGHT_MAX_PER_FEED=10`, `SPOTLIGHT_MAX_ROWS` safety valve, segment list, `PROPOSED_OPERATORS_TAB`, promote-issue label |
| `dc_pipeline.py` | run `dc_spotlight` after the register is built; run `dc_operators` (read approved issues → merge) near watchlist assembly |
| `dc_export.py` | `spotlight` (per-feed) + `proposed_operators` in `data.json` |
| `dashboard/index.html` | per-feed "Most Important — last 48h" section atop News/Policy/Disclosure views; Proposed Operators panel w/ Promote button |
| `dashboard/api/promote.js` | serverless promote endpoint — password-gated GitHub-Issue drop, mirrors `ask.js` |
| `.github/workflows/dc-pipeline.yml` | (if needed) `promote-operator` issues read/write already covered by existing `GITHUB_TOKEN` |

## Build order

1. `docs/TAG_BD_CRITERIA.md` — grounds everything; human judgment drives this. **Start here.**
2. `dc_spotlight.py` — the 3 per-feed rankers + judge + widen loop, cached + non-fatal.
   Ship Feature A first, verify on a real run.
3. `spotlight` export + the three per-feed dashboard sections.
4. `orgs` extraction added to the News + Disclosure rankers (Feature B data starts flowing).
5. `dc_operators.py` verify chain (MCA→EDGAR→Wikidata→Firecrawl) + `Proposed Operators`
   store + dedup + `proposed_operators` export.
6. Proposed Operators dashboard panel + `promote.js` (GitHub-Issue drop) + next-run
   read-approved → runtime-union into watchlist.
7. `GNews Foreign Players` template expansion on promote.

## Deferred / out of scope here

- **Self-hosted crawler / SearXNG on a persistent host** — only if bulk open-web crawling
  is ever needed at scale; a deliberate infra project, never bolted into CI.
- Disclosure link-fix + relevance sort (original ask #3 — separate quick-win).
- Extending the spotlight window past 48h (explicitly rejected — widen loosens the filter,
  not the window).

---

## Context already shipped (for reference)

- **In-house government-affairs detection** — advisory `⚠ gov-affairs` badge on prospects,
  grounded (curated backstop + job/news LLM classification + Firecrawl web enrichment),
  cached once-ever per company (`govaffairs_cache.json`), credit-capped. Live on `main`.
  The disqualifier logic in the rubric above leans on this. (Badge now renders across
  Prospects/MD/Analyst views with real citations, incl. the curated giants.)
