# TAG BD Criteria — the grounding rubric

**Purpose.** Single source of truth that grounds every AI ranker and the judge in the
48h-spotlight + operators feature. This doc is passed verbatim into the LLM context. It
consolidates what already lives in code (`dc_config.BD_FACTORS`, `dc_bd.fee_viability`,
`dc_bd._deal_usd`, `dc_states.targeting_matrix`) + `knowledge/india_state_bank.md`, so the
model ranks on the *same* logic the deterministic pipeline already uses. Numbers here are
copied from code — if code changes, update this doc in the same PR.

> **Discipline (LOCKED).** The AI may only **rank, drop, or label** grounded rows. It never
> invents companies, deals, dates, states, or ids, and never overrides the deterministic
> role/type/priority the pipeline already computed. Every id it returns is validated against
> the real input rows and dropped if fabricated.

---

## 1. The engagement TAG sells

A **~$50k/month retainer (~$600k/yr)** for **India market-entry advisory**: state selection,
land + power coordination, government & regulatory affairs, incentive capture, and
JV/partner selection. So the best row is one where a company is **about to make an India
data-centre move and would pay for help making it.**

## 2. Who ranks high (ideal client)

A row scores high when it shows a company that is:

- **A cross-border mover** — foreign or GCC player *entering* India, or making its *first*
  India expansion. (This is the strongest single signal; TAG's whole wedge is helping
  outsiders land.)
- **Above the fee bar** — the deal or backer is big enough to fund a $600k/yr retainer:
  - **deal ≥ $50M** = floor (`medium`), **deal ≥ $500M** = strong (`high`).
    (`FEE_VIABILITY_DEAL_USD = {high: 500M, medium: 50M}`.)
  - **or** a mega-fund / sovereign / hyperscaler-scale **backer** (see §5) — backer scale
    can clear the bar even without a stated deal number.
- **On an active trigger** — land, capex, capacity, JV/partnership, or energy/power move.
  A stated `deal_value` or a JV counts as a trigger by itself.
- **In an attractive state** — a **Priority-1** state (§4).
- **Novel** — a new name / new deal, not something already tracked and stale.

**LOCKED:** affordability is a **gate, not the ranking axis**. The retainer/fee bar is a
*scoring signal* that lifts a row, **not** a hard floor that deletes everything under $50M —
a small-but-novel cross-border first-mover can still rank.

## 3. Disqualifiers (rank low / drop)

- **Hyperscalers** — AWS, Amazon, Microsoft, Google, Oracle, Meta. They can pay but run
  their own India policy teams (they carry the `⚠ gov-affairs` badge), so TAG can't win
  them. Rank low; never a top pick.
- **Entrenched domestic incumbents** — established Indian operators with no cross-border
  motion (they don't need market-entry help).
- **Sub-scale** — clearly under the $50M floor **and** no mega-backer **and** not a novel
  first-mover.
- **T3 chatter** — thin, single-weak-source, unverified noise.

## 4. State attractiveness (from `knowledge/india_state_bank.md`, the truth table)

Rank an India row higher when its matched state is Priority-1. **Quote the matched state's
pitch, and always respect the validity warning** — an expired/unverified policy base weakens
the row.

| Priority | States |
|---|---|
| **P1** | **Maharashtra, Uttar Pradesh, Telangana, Tamil Nadu, Andhra Pradesh** |
| P2 | Odisha, Gujarat, West Bengal, Karnataka, Haryana |
| P3 | Himachal Pradesh, Uttarakhand |

**Validity warnings to honor (do not treat an expired base as strong):**
- **Tamil Nadu** — policy **expired unless extended** past 31 Mar 2026.
- **Uttar Pradesh** — 2026 official GO/clauses still needed; current text is secondary.
- **Telangana** — policy status update check needed.
- **West Bengal** — expiry Sep 2026, replacement/extension check needed.
- **Andhra Pradesh** — broader incentive code / essential-service status not verified.

**Upside / whitespace pattern (LOCKED):** high **policy** confidence + low **execution**
confidence = a first-mover opening (the **Odisha** pattern). Worth surfacing even though
execution is thin — it's exactly where TAG adds value.

## 5. Backer scale (fee-bar shortcut, from `dc_config.BACKER_SCALE`)

A named backer at these scales clears the fee bar on its own:

- **Mega-fund / sovereign:** Blackstone, Brookfield, GIC, KKR, Macquarie, Keppel, Kotak,
  Mubadala, ADIA, PIF.
- **Hyperscaler:** AWS, Amazon, Microsoft, Google, Oracle, Meta. *(fundable, but
  disqualified as a client per §3 — a hyperscaler backing someone else's deal is fine; the
  hyperscaler itself is not the prospect.)*
- **Platform:** AirTrunk, Vantage, STACK Infrastructure, EdgeConneX, Princeton Digital,
  Digital Realty, Equinix, NTT, G42.

## 6. How the deterministic score already weighs these (`dc_config.BD_FACTORS`)

The model's ranking should *align* with this weighting (it's what the pipeline already uses,
so the AI top-slice shouldn't fight the deterministic BD score):

| Factor | Weight | Meaning |
|---|---:|---|
| trigger_strength | 0.25 | strongest verified signal × recency |
| tag_fit | 0.15 | role/type/stage — TAG's realistic ability to help |
| buyer_access | 0.15 | accessibility by company type* |
| cross_border | 0.10 | foreign→India / GCC→India motion |
| policy_exposure | 0.10 | genuine policy classes for the layer/geo/state |
| deal_size | 0.10 | deal buckets + fee-viability backer scale |
| timing | 0.10 | recency of last signal |
| source_confidence | 0.05 | T1 share of the evidence mix |

*buyer_access by `company_type`: Infra-investor 0.9 · Other 0.8 · GCC-operator 0.7 ·
Indian-operator 0.6 · **Hyperscaler 0.2**. cross_border: foreign+India 1.0 · GCC-operator+India
0.9 · India-only 0.3 · none 0.

## 7. What "most important — last 48h" means (ranker instruction)

Given a feed's real last-48h rows (each pre-tagged with its `deal_usd` bucket and matched
state), return the **top 10 by BD relevance for TAG**, judged on:

1. **Cross-border motion** (foreign/GCC → India) — weigh heaviest.
2. **Deal value** — use the passed `deal_usd` bucket, not headline-guessing.
3. **State attractiveness** — P1 state + valid policy base.
4. **Trigger freshness & novelty** — new name / new deal beats a restated old one.

Drop hyperscaler-as-client rows and T3 chatter from the top slice. If fewer than 10 rows are
genuinely BD-relevant, **return fewer** — a padded list is worse than a short one.

## 8. Operator extraction (Feature B grounding)

From the ranked news, extract **DC value-chain company names**, each tagged by segment:
`operator · energy/power · cooling/coolant · hardware/compute · transmission/network`.
**Promotable = operators + cross-border movers only** (the names TAG could advise). Suppliers
may be surfaced as context but are not promoted. Never propose a name already in
`WATCH_OPERATORS_*` or the tracked prospects.
