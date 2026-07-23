# Claude Handover — India Data Centre State Bible

Status: authoritative architecture handover  
Prepared: 2026-07-20  
Reference implementation: Gujarat  
Supersedes for future implementation: `../STATE_STRUCTURE_AND_LLM_HANDOFF.md`

## Purpose

This pack defines the state-level knowledge architecture for the India Data Centre Bible and the LLM context-loading mechanism that should consume it. The primary design decision is that a state is the contextual retrieval unit. Tags and atomic claim records may assist navigation, but they must never be used to reduce a state question to isolated fragments that omit policy lineage, caveats, project history, execution evidence or unresolved conflicts.

For a Gujarat question, the LLM must receive the complete `states/gujarat/state_context.md`. Additional source documents are loaded only when the question requires clause-level proof, document interpretation, a dated research gap or a full project diligence trail.

## Locked decisions

1. Every state uses the same directory and file names.
2. `state_context.md` is the complete LLM-readable synthesis and is loaded in full for a state query.
3. `source_gaps.md` is a separate Markdown document beside `state_context.md`.
4. `research_queue.xlsx` and `change_log.xlsx` are separate workbooks beside `state_context.md`.
5. `source_library/source_register.xlsx` is the source-control workbook.
6. Complete underlying files live in `source_library/documents/`.
7. Source metadata is one row per source, not one row per sentence or content tag.
8. Material uncertainty is stated inline in `state_context.md`; it is not hidden only in `source_gaps.md`.
9. A missing field is written as a dated negative finding, never silently omitted.
10. Historical content and superseded sources are retained and clearly labelled.
11. The existing `knowledge/india_state_bank.md` may not be deleted, replaced or edited without Darsh Puri's specific approval. The Gujarat migration does not alter it.
12. Existing Gujarat evidence IDs remain permanent. Future source IDs should be category-neutral.

## Read order

1. `01_CANONICAL_STATE_ARCHITECTURE.md`
2. `02_LLM_CONTEXT_ASSEMBLY_CONTRACT.md`
3. `03_CONTROL_FILE_SCHEMAS.md`
4. `04_MIGRATION_AND_PRESERVATION_RULES.md`
5. `05_GUJARAT_HANDOVER.md`

## Authority hierarchy

If implementation documents conflict, apply this order:

1. Explicit instructions from Darsh Puri.
2. This handover pack.
3. The canonical files within the relevant state directory.
4. Archived research notes and the legacy architecture document.

The legacy `STATE_STRUCTURE_AND_LLM_HANDOFF.md` describes an earlier retrieval-heavy design. It is retained for history, but its `state.json`, JSONL claim store, topic-tag retrieval and fragment-ranking model are not the approved target architecture.

## Gujarat starting point

The Gujarat package contains 72 registered sources and 73 physical source files at the migration cut-off. The difference is caused by the official Gujarat policy-launch record being preserved in both JSON and HTML forms under one evidence ID. The most important current legal source is the user-authenticated official `Viksit Gujarat Data Center Policy (2026–2029)` booklet, `GJ-POL-2026-001`.

The policy booklet is authoritative text, but its notification/GR metadata is not printed in the booklet and clause 5(h) contains an unresolved `XXXXXX` deadline placeholder. Those defects must remain visible in the state context and gap register.

## Completion test

A state package is structurally complete when:

- all canonical files exist;
- all 22 numbered `state_context.md` sections (`00` through `21`) exist in the prescribed order;
- every source row resolves to a file or explicitly records why no local file exists;
- material uncertainty is visible beside the affected analysis;
- project stages are evidence-based;
- source gaps and research tasks are current;
- corrections and supersessions are logged; and
- no legacy content was silently discarded during migration.
