# Ask-the-Analyst Q&A — Handoff

Consultant-grade Q&A: state-context loading + multi-pass reasoning + verified,
linked citations. Repo is **private**. No live web retrieval anywhere.

## Flow (per question)

Dashboard ask form → GitHub issue (label `analyst-question`) → pipeline answers → back to dashboard.

1. **`dc_qa.py`** pulls open `analyst-question` issues (oldest 5), sanitizes, calls
   `dc_ai.answer_questions(...)`, comments+closes the issue, persists to `qa_log.json`.
2. **`dc_ai.answer_questions` → `_answer_one`** (the mechanism), per question:
   - **Resolve state(s)** deterministically (`dc_state_context.resolve_states`, alias table).
   - **Load COMPLETE state context** — Gujarat `state_context.md` (bible); other states fall
     back to legacy `india_state_bank.md`. `source_gaps.md` added on verification questions.
   - **Select → answer → judge → widen** loop, max 3 passes (2 widenings). Selector reasoning
     OFF; answerer + judge reasoning ON. Widening enlarges the evidence-id budget + pulls the
     gap register. Non-fatal throughout.
   - **Verify citations** — the answer's inline `[GJ-…]` cites are kept only if they exist in
     the bible's §21 Source Reference Map. Deterministic set-membership, **not** an LLM call.
   - Returns `{a, evidence_ids, state_cites}`. `state_cites = [{id, desc, url, provider}]`.
3. **Email audit** — full per-pass trail to `AUDIT_EMAIL` via stdlib smtplib (non-fatal).
4. **Export/dashboard** — `data.json` qa entries carry `state_cites`; the drawer renders them.

## Citations (the "Cited evidence" chip)

Counts register evidence **plus** verified state-context sources. Each drawer item shows its ID.
State-context source rendering:
- **Public source** → description links to the source URL.
- **User-supplied source** (`provider: true`) → labelled *"pre-requisite research confirmed by
  provider"*, no link. Flag = the register's own "User-supplied research aid" class
  (currently only `GJ-TRANS-2026-003`, the one source with no public URL).

## Key files

| File | Role |
|---|---|
| `dc_state_context.py` | state resolution, complete-context load, §21 `source_map`, `source_urls` |
| `dc_ai.py` | `_answer_one` multi-pass loop, `_state_cites` verification, `_chat(reason=)`, email digest |
| `dc_qa.py` | issue queue → answers → `qa_log.json` |
| `dashboard/index.html` | Q&A drawer render (chip count, links, provider label) |
| `knowledge/india_state_bible/states/gujarat/state_context.md` | complete state context (§21 = source map) |
| `knowledge/india_state_bible/states/gujarat/source_urls.json` | `id → {url, provider}` (from `source_register.xlsx`) |
| `qa_log.json` | answered-question store (also the answer cache) |
| `test_desk.py` | offline asserts (resolution, verification, widen cap, backfill) |

## Secrets (GitHub Actions)

`OPENROUTER_API_KEY`, `GMAIL_ADDRESS` (sender), `GMAIL_APP_PASSWORD`, `AUDIT_EMAIL`
(default darshpuri2006@gmail.com). All set.

## Caching

- **Answers** — `qa_log.json`; answered questions never re-answered (no repeat token spend).
- **Data** — pipeline "Commit caches" step keeps SS1–SS5 raw data between runs.
- Not built: prompt-caching the ~14K-token state context across questions (only worth it if
  the token bill grows).

## Regenerating source_urls.json (when the bible register changes)

Source of truth is the **uncommitted** `source_library/source_register.xlsx` on Desktop
(`knowledge/india_state_bible/states/gujarat/source_library/`). Per source id, take the first
`http…` cell as `url` and `provider = (type column == "User-supplied research aid")`. Only the
id→{url,provider} subset is committed — none of the register's checksums/trust-note columns.

## Known limits / open items

- **Published answers are world-readable** — repo-private does NOT gate the Vercel deployment;
  `data.json` is served without auth. The ask-form password gates *submitting* only. Ready
  upgrades (not built): Vercel Deployment Protection, or an answer sanitizer stripping §19/gap
  content from published answers while keeping full reasoning in the private email digest.
- **Only Gujarat is bible-backed.** Other states use the legacy bank (no §21 → no verified
  state cites) until their `state_context.md` lands. `india_state_bank.md` must NOT be edited
  without Darsh's approval.
- **`dc_ai.compile_context` is dead code** (old Q&A path) — safe to delete (~95 lines).
- Fixes apply to **new** answers; older `qa_log.json` entries were backfilled once.
