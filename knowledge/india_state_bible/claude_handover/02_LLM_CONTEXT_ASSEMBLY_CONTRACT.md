# LLM Context Assembly Contract

## 1. Core principle

The state, not a content tag, is the primary context unit.

If a query materially concerns Gujarat, load the complete Gujarat `state_context.md`. Do not select only the paragraphs tagged `power`, `incentives` or `Dholera`. A power question may depend on project stage, location-specific licensee, policy eligibility, renewable-energy conditions, water technology and a time-limited surcharge order.

## 2. State detection

A query should map to a state when it contains or resolves to any of the following:

- state name or code;
- city, district, industrial region, special investment region or state authority;
- project or company site known to be in the state;
- state policy, regulator, distribution licensee or development authority;
- a follow-up in a conversation whose active jurisdiction is that state.

Maintain an alias table outside the prose document. For Gujarat it should recognise at minimum Gujarat, GJ, Ahmedabad, Gandhinagar, GIFT City, Dholera, DSIR, DICDL, DSIRDA, Jamnagar, Surat, Vadodara and Gujarat-specific authorities/licensees.

## 3. Mandatory load

For a single-state question:

```text
system and application instructions
+ complete states/<state>/state_context.md
+ user query and conversation context
```

The complete state context is mandatory even if the question appears narrow.

## 4. Conditional additions

Load `source_gaps.md` when the query asks about:

- whether something has been verified;
- missing records;
- conflicts, uncertainty or diligence;
- what to research or request next;
- project execution beyond an announcement;
- freshness, expiry or policy implementation gaps.

Load rows from `research_queue.xlsx` when the system is planning research, reporting progress or deciding the next browser task.

Load rows from `change_log.xlsx` when the query asks what changed, why a previous answer differed, whether a statement was corrected or which approval was required.

Load selected source-register rows and full source documents when the query requires:

- exact clause, page, number, date or legal wording;
- interpretation of a supplied policy or regulatory instrument;
- a source-quality challenge;
- a quote or detailed source comparison;
- confirmation that an appendix, schedule or amendment exists;
- resolving a conflict recorded in the state context.

## 5. Source selection is citation-led

When deeper evidence is required, begin with source IDs already cited in the relevant state-context section. Then consult `source_register.xlsx` for related sources, supersession status and file paths. Topics may help discovery, but no source is excluded merely because a tag does not match the query.

## 6. Context-budget fallback

The preferred behaviour is to load the complete file. If a model context limit is genuinely exceeded:

1. Preserve Sections 00, 01, 17, 19 and 21.
2. Preserve the complete queried section and every section it explicitly cross-references.
3. Preserve project case studies and location sections for every named project/location.
4. Preserve all inline caveats and citations attached to retained content.
5. Split only at numbered heading boundaries.
6. State which numbered sections were not supplied.

Do not use embedding similarity alone to discard sections. Deterministic section loading is the fallback, not the default.

## 7. Recommended assembly pseudocode

```text
states = resolve_states(query, conversation)

for state in states:
    context += read(state/state_context.md)          # always

    if asks_about_gaps_or_research(query):
        context += read(state/source_gaps.md)

    if asks_about_research_operations(query):
        context += serialize(relevant_rows(state/research_queue.xlsx))

    if asks_about_changes_or_corrections(query):
        context += serialize(relevant_rows(state/change_log.xlsx))

    if requires_document_level_proof(query):
        ids = citations_in_relevant_sections(state_context)
        records = lookup(ids, state/source_library/source_register.xlsx)
        context += records
        context += read_required_documents(records)
```

For a multi-state comparison, load each complete state context if the model permits. If it does not, use the deterministic section fallback equally across states and disclose the reduction.

## 8. Answer discipline

An answer generated from this system must:

- distinguish current rules from historical rules;
- state the information cut-off for date-sensitive conclusions;
- distinguish policy availability from project eligibility and sanction;
- distinguish announced capacity from approved IT load, connected demand, construction and operating capacity;
- distinguish official/company statements from independent verification;
- retain source IDs and pinpoints when making factual claims;
- surface material uncertainty in the answer, not only in hidden metadata;
- avoid converting absence from a website or filing into proof of cancellation; and
- route new unresolved questions into the source-gap and research-queue workflow.

## 9. Persistence rules

Do not automatically write an LLM answer into `state_context.md`.

A new statement may be persisted only after:

1. its supporting source is registered;
2. the document is preserved or its absence explained;
3. the current/superseded relationship is checked;
4. project-stage implications are reviewed;
5. any correction is added to `change_log.xlsx`; and
6. the relevant narrative is edited without silently removing historical context.

## 10. Anti-patterns

The following behaviours are prohibited:

- retrieving one tagged sentence without its surrounding caveat;
- treating source IDs as topic filters;
- returning a policy incentive as though a project has received it;
- using generic state power prices instead of the applicable licensee/order;
- treating an EOI as an award;
- treating an MoU as site control or construction;
- treating master-plan infrastructure as project reservation;
- silently replacing an old policy position without recording lineage; and
- deleting legacy Gujarat bank content without user approval.

