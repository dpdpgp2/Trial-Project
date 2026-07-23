# State Data-Centre Intelligence Structure and LLM Handoff Specification

> **Legacy architecture — superseded 2026-07-20.** This document is retained without removing its historical design content. Do not implement its `state.json`, JSONL claim-store, topic-tag retrieval or ranked-fragment architecture. The approved state-context architecture and Claude implementation contract are in [`claude_handover/README.md`](claude_handover/README.md). Gujarat's canonical implementation is in [`states/gujarat/state_context.md`](states/gujarat/state_context.md).

Status: planning specification  
Prepared: 2026-07-20  
Reference implementation: Gujarat  
Intended reader: an engineer or another LLM redesigning the state-intelligence query mechanism

## 1. Executive decision

The state research system should use the same **analytical structure** for every Indian state, but it should not require every state to populate a large set of evidence categories.

The distinction is:

- **Analytical fields are fixed.** Every state is evaluated against the same questions so comparisons remain possible.
- **Evidence storage is flexible.** Evidence is stored in one flat state evidence collection and can support multiple fields through tags and claim links.
- **Unknown is a valid result.** A missing field is recorded as `unknown`, `not_found_publicly` or `not_applicable`; it does not require padding or a weak source.
- **Claims, not folders, are the unit of knowledge.** Each factual proposition is atomic, dated and linked to one or more evidence records.
- **The LLM receives only the relevant state, section, claims and evidence.** It must never receive the entire India bank for a state-specific query.

This solves the current concern: a state does not need nine well-populated evidence folders to be usable. One policy PDF may support policy status, incentives, eligibility, validity, approvals, power concessions and continuity simultaneously.

## 2. Current production context

The existing application currently treats `knowledge/india_state_bank.md` as its source of truth:

- `dc_config.STATE_BANK_PATH` points to the monolithic Markdown bank.
- `dc_states.state_section(state)` extracts only the matching state's Markdown section.
- The current AI boundary correctly prevents the full bank from being passed to the model.
- The Gujarat Bible workspace is presently a parallel research/evidence layer and is not yet consumed by `dc_states.py`.

This specification does not authorize replacing the current bank. The new state package should be built and validated in parallel. Production should switch only after a separate migration and user approval.

## 3. Design principles

### 3.1 Jurisdiction-neutral

The same file names, section IDs, field IDs, claim schema, project-stage vocabulary and query contract apply to every state and union territory.

### 3.2 Sparse by design

No evidence topic has a minimum record count. A state with one policy and no known private data centre is still representable without inventing content.

### 3.3 Evidence may serve many fields

Evidence is not assigned to one exclusive subject. A tariff order can support:

- distribution-licensee identity;
- applicable tariff;
- network maturity;
- demand growth;
- execution risk; and
- a project case study.

These relationships live in claim records and `topic_tags`, not directory placement.

### 3.4 Atomic and dated

One claim should express one independently testable proposition. Every date-sensitive claim has an `as_of_date` or operative period.

### 3.5 Negative findings are bounded

`not_found_publicly` means a defined public-source search did not locate the record by a stated date. It never means the record does not exist.

### 3.6 Historical material is retained

Superseded policies and corrected claims remain in the record. They are marked `superseded` or `incorrect`; they are not silently deleted.

### 3.7 Human and machine layers are separate

- JSON/JSONL files are the canonical structured layer for retrieval and validation.
- Markdown files are the human-readable synthesis, audit and editorial layer.
- CSV is a generated audit view, not the richest canonical representation.

## 4. Canonical state directory

Every jurisdiction uses this exact structure:

```text
knowledge/india_state_bible/states/<state-slug>/
├── state.json
├── state.md
├── claims.jsonl
├── evidence.jsonl
├── evidence_manifest.csv
├── projects.jsonl
├── research_queue.jsonl
├── source_gaps.md
├── projects/
│   └── <project-slug>.md
├── research/
│   ├── source-intake/
│   │   └── YYYY-MM-DD.md
│   └── audits/
│       ├── sources/
│       │   └── <source-slug>__YYYY-MM-DD.md
│       └── projects/
│           └── <project-slug>__YYYY-MM-DD.md
└── evidence/
    └── <state-code>-E-<year>-<serial>__<source-slug>.<ext>
```

There are no mandatory evidence subfolders by topic. The `evidence/` directory is flat.

### 4.1 File roles

| File | Canonical or generated | Purpose |
|---|---|---|
| `state.json` | Canonical | State identity, research date, package version and aggregate coverage metadata. |
| `state.md` | Canonical editorial | Complete human-readable state chapter using the fixed section structure. |
| `claims.jsonl` | Canonical | Atomic state and project claims, each linked to evidence. |
| `evidence.jsonl` | Canonical | Rich evidence metadata, artifacts, scope, provenance, hashes and tags. |
| `evidence_manifest.csv` | Generated audit view | Flat spreadsheet-friendly export of `evidence.jsonl`. |
| `projects.jsonl` | Canonical | Structured project and facility records with evidence-supported stage. |
| `research_queue.jsonl` | Canonical | Machine-readable unresolved questions used to generate future searches. |
| `source_gaps.md` | Human-readable | Prioritized explanation of material missing records and why they matter. |
| `projects/*.md` | Editorial | Detailed case studies for projects that warrant narrative treatment. |
| `research/source-intake/*.md` | Audit log | What was received/found on a date and how it was classified. |
| `research/audits/*.md` | Audit log | Claim audits, correction packets and project-stage reviews. |
| `evidence/*` | Immutable artifacts | PDFs, HTML captures, JSON, transcripts and user-supplied documents. |

## 5. Fixed `state.md` analytical structure

Every `state.md` uses exactly eight numbered sections. Subsections can be brief when evidence is sparse, but the section and field IDs remain stable.

```markdown
# <State> Data-Centre Intelligence

## S0. State snapshot
## S1. Rules, incentives and eligibility
## S2. Infrastructure and approvals
## S3. Market and ecosystem
## S4. Projects and execution
## S5. Government and continuity
## S6. Risks and investability
## S7. Evidence limits and next research
```

### 5.1 Field catalog

| Field ID | Required question | Valid sparse-state response |
|---|---|---|
| `S0.01` | What jurisdiction and state code does this package cover? | Always populated. |
| `S0.02` | When was the package last verified? | Always populated. |
| `S0.03` | What is the state's overall data-centre maturity? | `unknown` if no basis. |
| `S0.04` | What is the one-paragraph current investment position? | Evidence-backed summary or explicit insufficiency. |
| `S1.01` | Does the state have a dedicated data-centre policy? | `yes`, `no`, `announced`, `expired`, `superseded`, `unknown`. |
| `S1.02` | What instruments govern the sector and what is their lineage? | List only verified instruments. |
| `S1.03` | What are the effective dates, expiry, transition and grandfathering rules? | Exact dates or `not established`. |
| `S1.04` | Who and what projects are eligible? | Verified thresholds or `not established`. |
| `S1.05` | What fiscal and non-fiscal incentives exist? | Atomic incentive table or `none verified`. |
| `S1.06` | How are applications, sanctions, disbursement and clawbacks handled? | Verified process or `implementation instrument not found`. |
| `S2.01` | What is known about power supply, tariffs, redundancy and renewable procurement? | State/city/project scope must be distinguished. |
| `S2.02` | What is known about land, zoning and building controls? | Framework or project-specific position. |
| `S2.03` | What is known about water, cooling and environmental constraints? | Framework, location risk or `not established`. |
| `S2.04` | What approvals are required and who issues them? | Verified approval path; unknown SLAs remain explicit. |
| `S2.05` | What is known about fibre, interconnection, cable landings and latency? | Verified facilities/routes or `not established`. |
| `S3.01` | What demand drivers exist? | Evidence-backed demand thesis or `insufficient evidence`. |
| `S3.02` | Which operators and customers are active? | Entity inventory with stage/scope. |
| `S3.03` | Which suppliers, utilities, developers and advisers form the value chain? | Evidence-backed inventory; no quota. |
| `S3.04` | What is known about talent and operating capability? | Evidence-backed assessment or gap. |
| `S4.01` | What operational facilities exist? | Facility records or dated negative finding. |
| `S4.02` | What announced or proposed pipeline exists? | Project records with stage vocabulary. |
| `S4.03` | Which projects merit case studies? | Zero or more project files. |
| `S4.04` | What execution evidence exists beyond announcements? | Land, permits, financing, construction, commissioning or explicit absence. |
| `S5.01` | Which agencies and political actors shape the sector? | Verified actions and statements only. |
| `S5.02` | What continuity or policy-change risks exist? | Evidence-backed chronology and expiry risk. |
| `S5.03` | What opposition, community or social-license evidence exists? | Verified positions or `none located by <date>`. |
| `S6.01` | What are the material risks? | Ranked risks linked to claims. |
| `S6.02` | What project types fit or do not fit the state? | Analyst judgment, clearly labelled. |
| `S6.03` | What questions must an investor resolve? | Diligence list tied to gaps. |
| `S6.04` | What BD opportunities are evidence-supported? | Analyst judgment with supporting claims. |
| `S7.01` | What material evidence remains missing? | Prioritized gaps. |
| `S7.02` | Which claims are conflicted, superseded or date-sensitive? | Conflict register. |
| `S7.03` | What should the next research queries target? | Rendered queue summary. |

The field catalog is the comparison framework. It is not an evidence quota.

## 6. `state.json` schema

Example:

```json
{
  "schema_version": "1.0",
  "state_code": "GJ",
  "state_name": "Gujarat",
  "state_slug": "gujarat",
  "country": "India",
  "last_verified": "2026-07-20",
  "package_status": "research_in_progress",
  "production_status": "not_connected",
  "current_policy_status": "dedicated_policy_official",
  "evidence_count": 72,
  "project_count": 5,
  "claim_count": null,
  "coverage": {
    "strong": ["S1.01", "S1.02"],
    "partial": ["S1.03", "S1.04", "S1.05", "S2.01", "S2.02", "S2.03", "S2.04", "S3.02", "S4.02"],
    "weak": ["S1.06", "S2.05", "S3.01", "S3.03", "S3.04", "S4.04", "S5.03"],
    "not_assessed": ["S6.02", "S6.04"]
  }
}
```

Coverage is an assessment of claim support, not a count of evidence files.

## 7. Evidence model

### 7.1 New evidence ID

Use a topic-neutral format:

```text
<STATE>-E-<YEAR>-<FOUR-DIGIT-SERIAL>
```

Examples:

```text
GJ-E-2026-0001
MH-E-2024-0017
TN-E-2021-0003
```

Topic-neutral IDs prevent a multi-purpose source from being forced into one category.

Existing Gujarat IDs such as `GJ-POL-2026-001` must not be rewritten immediately. Preserve them in `legacy_eids` and introduce new IDs only during a controlled migration.

### 7.2 Evidence record schema

One line in `evidence.jsonl` represents one logical source. It may contain multiple local artifacts, such as an HTML capture and structured JSON capture.

```json
{
  "eid": "GJ-E-2026-0001",
  "legacy_eids": ["GJ-POL-2026-001"],
  "title": "Viksit Gujarat Data Center Policy 2026-2029",
  "state_code": "GJ",
  "source_class": "official_legal",
  "authority": "Government of Gujarat, Department of Science and Technology",
  "document_type": "policy",
  "dates": {
    "published": "2026",
    "effective": null,
    "expiry": null,
    "accessed": "2026-07-19"
  },
  "scope": {
    "level": "state",
    "geographies": ["Gujarat"],
    "entities": [],
    "projects": []
  },
  "topic_tags": [
    "policy",
    "incentives",
    "eligibility",
    "power",
    "land",
    "building",
    "water",
    "implementation"
  ],
  "status": {
    "completeness": "full",
    "text": "embedded_text",
    "legal": "official_policy_effective_date_unresolved",
    "superseded_by": null
  },
  "source": {
    "url": "https://vainetra.com/wp-content/uploads/2026/07/gujarat-data-centre-policy.pdf",
    "retrieval_note": "User confirmed this is the official policy PDF; the host is provenance only.",
    "artifacts": [
      {
        "path": "evidence/GJ-E-2026-0001__viksit-gujarat-data-centre-policy.pdf",
        "mime": "application/pdf",
        "pages": 16,
        "sha256": "860a61cba19f9b98bef54510a1e5c8b7110f66bd557336365ef394bad57d80e9"
      }
    ]
  },
  "pinpoints": [
    {
      "locator": "page 8, definition 5(h)",
      "note": "Operative period and unresolved XXXXXX approval deadline."
    }
  ],
  "notes": "Official policy text. Notification date/number and placeholder clarification remain gaps."
}
```

### 7.3 Source classes

Use only these five classes:

| Value | Meaning |
|---|---|
| `official_legal` | Gazette, act, rule, regulation, regulatory order, government resolution, notification or official policy. |
| `official_administrative` | Government portal, form, dataset, agency report, tender, committee minutes or implementation material. |
| `company_primary` | Stock-exchange filing, annual report, company release, investor transcript or official project page. |
| `independent_secondary` | Independent high-trust reporting, academic work or established specialist research. |
| `working_material` | User-supplied research, transcript, discovery page, search result or other aid that cannot independently establish the claim. |

These classes express provenance, not subject matter.

### 7.4 Topic tags

`topic_tags` are multi-valued retrieval hints. They do not create folders or coverage requirements.

Recommended controlled tags:

```text
policy, incentive, eligibility, validity, application, clawback,
power, renewable, tariff, open_access, land, zoning, building,
water, environment, climate, approval, connectivity, demand,
company, project, construction, financing, government, politics,
community, risk, talent, market
```

A source can have any number of tags, including zero during initial intake.

### 7.5 Scope levels

Use one of:

```text
national, state, region, city, site, project, entity
```

The LLM must not convert a state-, city- or region-level fact into a project-specific fact.

## 8. Claim model

### 8.1 Claim ID

```text
<STATE>-CLM-<SIX-DIGIT-SERIAL>
```

Example: `GJ-CLM-000127`.

### 8.2 Claim schema

```json
{
  "claim_id": "GJ-CLM-000127",
  "state_code": "GJ",
  "field_id": "S4.04",
  "project_id": "GJ-PRJ-LT-VYOMA-DHOLERA",
  "claim_text": "Project-specific land allotment for the proposed L&T Vyoma Dholera campus was not located in the public sources checked through 2026-07-20.",
  "claim_status": "not_found_publicly",
  "as_of_date": "2026-07-20",
  "confidence": "medium",
  "evidence": [
    {
      "eid": "GJ-E-2026-0042",
      "relationship": "supports_search_scope",
      "pinpoint": "DICDL site search result"
    }
  ],
  "supersedes_claim_id": null,
  "analyst_note": "This does not establish that no confidential or unindexed record exists."
}
```

### 8.3 Claim statuses

Use exactly these values:

| Status | Meaning |
|---|---|
| `verified_primary` | Directly supported by official or company-primary evidence. |
| `verified_secondary` | Supported by credible independent reporting but primary evidence is unavailable. |
| `qualified` | Substantially supported but requires an important limitation. |
| `analyst_judgment` | Inference or investment interpretation, not a source fact. |
| `not_found_publicly` | Defined public search did not locate the record by the stated date. |
| `unknown` | Insufficient work or evidence to form a position. |
| `conflicted` | Credible sources materially disagree. |
| `superseded` | Historically correct or previously recorded but replaced by later evidence. |
| `incorrect` | Demonstrably false or misattributed. |
| `not_applicable` | Field does not apply to the jurisdiction/project. |

### 8.4 Evidence relationships

Use:

```text
supports, qualifies, contradicts, supersedes, supports_search_scope
```

An evidence record is never a citation merely because its topic tag matches. It must be explicitly linked to the claim.

## 9. Project model

### 9.1 Project ID

```text
<STATE>-PRJ-<NORMALIZED-PROJECT-SLUG>
```

Examples:

```text
GJ-PRJ-LT-VYOMA-DHOLERA
GJ-PRJ-RELIANCE-META-JAMNAGAR
GJ-PRJ-STT-AHMEDABAD-DC1
```

### 9.2 Project-stage vocabulary

Use exactly one current public-evidence stage:

```text
concept
announced
mou
feasibility
site_controlled
permitted
financed
under_construction
commissioned
operational
expanding
stalled
cancelled
unknown
```

### 9.3 Stage escalation rules

| Stage | Minimum public evidence |
|---|---|
| `announced` | Attributable government or company announcement. |
| `mou` | Signed-MoU confirmation from a party; the MoU PDF is preferred but not mandatory for the stage label. |
| `feasibility` | Explicit feasibility/site-study mandate or completed feasibility disclosure. |
| `site_controlled` | Executed land right and possession/site-control evidence. |
| `permitted` | Material project-specific land/building/environmental approvals. |
| `financed` | Board/lender/financial-close evidence sufficient to fund execution. |
| `under_construction` | Commencement permission plus physical/EPC evidence. |
| `commissioned` | Energisation, completion, occupancy or integrated-testing evidence. |
| `operational` | Facility is accepting/serving workloads or operator confirms live operations. |
| `stalled` | Credible evidence of missed milestones, suspended work or prolonged inactivity. |
| `cancelled` | Attributable cancellation/termination evidence. |

Never infer a higher stage from investment value, target date, generic infrastructure or political language.

### 9.4 Project record schema

```json
{
  "project_id": "GJ-PRJ-LT-VYOMA-DHOLERA",
  "state_code": "GJ",
  "name": "L&T Vyoma Dholera AI data-centre campus",
  "entities": ["Larsen & Toubro", "L&T Vyoma"],
  "location": {
    "city_or_region": "Dholera SIR",
    "site": null,
    "coordinates": null
  },
  "stage": "feasibility",
  "stage_as_of": "2026-07-20",
  "stage_claim_id": "GJ-CLM-000127",
  "announced_capacity_mw": 250,
  "capacity_basis": "proposed; IT-load versus facility-load basis not established",
  "announced_investment_inr_crore": 25000,
  "target_date": "2028",
  "target_date_status": "aspirational",
  "case_study_path": "projects/lt-vyoma-dholera.md",
  "open_questions": [
    "signed MoU",
    "feasibility report",
    "selected plot",
    "load sanction",
    "water allocation",
    "project approvals",
    "incentive sanction"
  ]
}
```

## 10. Research queue model

The query generator should read `research_queue.jsonl`. It should not infer research tasks from empty directories.

### 10.1 Queue record

```json
{
  "research_id": "GJ-RQ-000043",
  "state_code": "GJ",
  "field_id": "S4.04",
  "project_id": "GJ-PRJ-LT-VYOMA-DHOLERA",
  "question": "Has DICDL or DSIRDA issued a plot allotment, lease or possession record for Larsen & Toubro, L&T Vyoma, L&T-Cloudfiniti or a nominated SPV?",
  "priority": "critical",
  "status": "open",
  "reason": "Required to move the project beyond feasibility to site_controlled.",
  "preferred_sources": [
    "DICDL board records",
    "DSIRDA development-permission records",
    "executed lease or possession memorandum"
  ],
  "last_searched": "2026-07-20",
  "search_limitations": "Public indexed sources only",
  "resolved_by_claim_id": null
}
```

### 10.2 Queue priorities

```text
critical, high, medium, low
```

Critical means the answer changes legal eligibility, project stage, material cost or investability.

### 10.3 Queue statuses

```text
open, researching, resolved, blocked, obsolete
```

## 11. LLM query contract

### 11.1 Input object

Every state-intelligence model call should receive a structured request:

```json
{
  "query_id": "Q-2026-07-20-0001",
  "state_code": "GJ",
  "target_type": "project_field",
  "target_id": "GJ-PRJ-LT-VYOMA-DHOLERA",
  "field_ids": ["S4.04", "S2.01", "S2.02", "S2.03"],
  "question": "What public execution evidence exists beyond the L&T Vyoma MoU?",
  "as_of_date": "2026-07-20",
  "allowed_claim_statuses": [
    "verified_primary",
    "verified_secondary",
    "qualified",
    "not_found_publicly",
    "conflicted",
    "superseded",
    "incorrect"
  ],
  "output_schema_version": "1.0"
}
```

The caller should resolve the state and target deterministically before the LLM call.

### 11.2 Context assembly

The retrieval layer should supply:

1. `state.json`.
2. Only the requested `state.md` sections.
3. Existing claims matching the requested field IDs or project ID.
4. Evidence explicitly linked to those claims.
5. Additional evidence ranked by state, entity/project, scope, topic tags, trust and operative date.
6. Every evidence record that conflicts with or supersedes a selected record.
7. Relevant open research-queue entries.

Do not supply:

- other states;
- the entire India state bank;
- unrelated evidence merely to fill a context window;
- discovery-only material when stronger linked evidence already answers the question;
- a project-level conclusion based only on state- or city-level evidence.

### 11.3 Retrieval ranking

Use this order:

1. Exact project/site match.
2. Exact field and state match.
3. Exact entity and state match.
4. Official legal source currently operative.
5. Official administrative or company-primary source.
6. Independent corroboration.
7. Working/discovery material.

Recency does not automatically beat legal authority. Supersession and effective dates must be resolved before ranking.

### 11.4 Minimum context rules

- Include all evidence records directly cited by selected claims.
- Include all known contradictions and superseding records.
- Prefer at least one primary source when one exists.
- If no primary source exists, say so in the context metadata.
- Do not manufacture a minimum evidence count.

## 12. LLM output contract

The model should return structured JSON, not free-form prose:

```json
{
  "query_id": "Q-2026-07-20-0001",
  "answer_status": "partial",
  "answer": "The public record supports MoU and feasibility status, but not site control, utility sanction, permitting or construction.",
  "claims": [
    {
      "claim_text": "L&T Vyoma was assigned a detailed feasibility assessment covering land suitability and infrastructure readiness.",
      "claim_status": "verified_secondary",
      "field_id": "S4.04",
      "project_id": "GJ-PRJ-LT-VYOMA-DHOLERA",
      "as_of_date": "2026-07-20",
      "evidence": [
        {
          "eid": "GJ-PROJ-2026-003",
          "pinpoint": "quoted Gujarat government statement",
          "relationship": "supports"
        }
      ]
    }
  ],
  "gaps": [
    {
      "field_id": "S4.04",
      "question": "Obtain the executed plot allotment or lease.",
      "priority": "critical"
    }
  ],
  "warnings": [
    "No signed MoU PDF was available in the supplied context.",
    "Generic Dholera infrastructure does not establish project reservation."
  ]
}
```

### 12.1 Answer statuses

```text
complete, partial, insufficient_evidence, conflicted
```

### 12.2 Validation before persistence

A deterministic validator must reject an output when:

- an EID does not exist;
- a pinpoint is missing for a legal/incentive claim;
- the evidence state/scope cannot support the claim scope;
- a project stage exceeds the minimum evidence rule;
- a `not_found_publicly` claim lacks a search date or limitation;
- a policy claim ignores a known superseding instrument;
- a factual claim is marked `analyst_judgment`; or
- a claim changes the legacy bank without a separate approval workflow.

## 13. Gujarat reference implementation

### 13.1 Current Gujarat package

Current location:

```text
knowledge/india_state_bible/states/gujarat/
```

Current contents:

- 6 authored Markdown research/audit documents.
- 72 unique manifest records.
- 73 physical evidence files because one evidence record has both HTML and JSON representations.
- 9 topic-specific evidence directories.
- No completed `state.md`.
- No atomic `claims.jsonl`.
- No structured `projects.jsonl`.
- No machine-readable `research_queue.jsonl`.
- No connection to the production `dc_states.py` path.

### 13.2 Current evidence distribution

The present categories are a description of what has been collected, not a future requirement:

| Current legacy category | Records | Future treatment |
|---|---:|---|
| Power | 18 | Flat evidence with `power`, `tariff`, `renewable` or `open_access` tags. |
| Land and approvals | 12 | Flat evidence with relevant multi-tags. |
| Policy and law | 10 | Flat evidence; usually `official_legal`. |
| Projects and case studies | 10 | Flat evidence linked to `projects.jsonl`. |
| Companies and filings | 9 | Flat evidence; usually `company_primary`. |
| Environment and water | 4 | Flat evidence with `water`, `environment`, `climate` tags. |
| Connectivity and market | 3 | Flat evidence with `connectivity`, `demand`, `market` tags. |
| Government and politics | 3 | Flat evidence with `government`, `politics`, `continuity` tags. |
| Transcripts and datasets | 3 | Source class depends on origin; user research remains `working_material`. |

No other state needs to match these counts or even have evidence for every listed tag.

### 13.3 Gujarat analytical coverage

| Field group | Current position | Coverage |
|---|---|---|
| `S1.01-S1.02` policy existence and lineage | Official Viksit Gujarat Data Centre Policy 2026-2029 plus IT/ITeS history and launch records. | Strong |
| `S1.03` validity and transition | Official booklet says three years from notification, but notification metadata and clause 5(h) placeholder remain unresolved. | Partial |
| `S1.04-S1.05` eligibility and incentives | Official booklet is available and clause extraction can proceed. | Partial-to-strong after structured extraction |
| `S1.06` application and disbursement | Portal status and older guidelines exist; 2026 implementation documents and project sanctions remain missing. | Weak |
| `S2.01` power | Strong policy/regulatory framework for Gujarat, GIFT and Dholera; weak project-specific proof. | Partial |
| `S2.02` land/building | Dholera GDCR, land policy and forms exist; current consolidation and project plot/permission remain missing. | Partial |
| `S2.03` water/environment | DSIR umbrella EC, CRZ context and water form exist; project allocation/applicability remains missing. | Partial |
| `S2.04` approvals | Several process portals/forms exist; SLAs, costs and project decisions remain incomplete. | Partial |
| `S2.05` connectivity | Gujarat CLS EOIs and national benchmark exist; award, landing execution and detailed fibre topology remain weak. | Weak |
| `S3.01` demand | GIFT, enterprise, manufacturing and AI theses are not yet systematically evidenced. | Weak |
| `S3.02` active companies | STT, L&T Vyoma, Reliance/Meta, Data First and public-sector records exist. | Partial |
| `S3.03-S3.04` value chain and talent | Not yet exhaustively built. | Weak |
| `S4.01` operational facilities | STT Ahmedabad DC1, Gujarat State Data Centre and Data First leads exist but require full case-study validation. | Partial |
| `S4.02-S4.04` project pipeline/execution | L&T and Jamnagar announcements exist; downstream execution evidence is thin. | Partial/weak |
| `S5` government and continuity | Launch/MoU records exist; full political-economy chronology remains incomplete. | Partial |
| `S6` risks and investability | Source ingredients exist; final synthesis has not been written. | Not assessed |
| `S7` evidence limits | Strong dated gap and audit documents exist. | Strong |

### 13.4 Gujarat projects to represent

The initial `projects.jsonl` should contain at least:

| Project ID | Working stage | Basis |
|---|---|---|
| `GJ-PRJ-STT-AHMEDABAD-DC1` | `operational` | GIFT/STT primary facility evidence; current operations need refresh. |
| `GJ-PRJ-GUJARAT-STATE-DATA-CENTRE` | `operational` | Official Gujarat State Data Centre record. |
| `GJ-PRJ-LT-VYOMA-DHOLERA` | `feasibility` | MoU plus explicit detailed-feasibility mandate; no site-control/execution proof. |
| `GJ-PRJ-RELIANCE-META-JAMNAGAR` | `announced` | Reliance and Meta primary announcements; downstream execution not yet verified. |
| `GJ-PRJ-DATA-FIRST-AHMEDABAD` | `operational` or `unknown` pending verification | Company facility page exists; operating scale and current status require source-qualified review. |

The model must not upgrade a project because another project in the same city has approvals or because the city has generic infrastructure.

### 13.5 Mapping current Gujarat authored files

| Current file | New location/role |
|---|---|
| `PROJECT_SPECIFIC_SOURCE_REQUEST_CHECKLIST.md` | Move to shared `knowledge/india_state_bible/templates/PROJECT_SOURCE_REQUEST_TEMPLATE.md`; Gujarat-specific open items become queue records. |
| `SOURCE_INTAKE_2026-07-19.md` | `research/source-intake/2026-07-19.md`. |
| `SOURCE_INTAKE_2026-07-20.md` | `research/source-intake/2026-07-20.md`. |
| `LT_VYOMA_DHOLERA_SOURCE_AUDIT_2026-07-19.md` | `research/audits/projects/lt-vyoma-dholera__2026-07-20.md`. |
| `DEEP_RESEARCH_REPORT_3_AUDIT_2026-07-20.md` | `research/audits/sources/lt-vyoma-deep-research-report__2026-07-20.md`. |
| `SOURCE_GAPS.md` | Normalize to `source_gaps.md`; also convert every actionable gap into `research_queue.jsonl`. |
| `evidence_manifest.csv` | Retain as audit export; create richer `evidence.jsonl`. |
| Topic-specific evidence directories | Flatten only during controlled migration; keep existing paths as artifact aliases until every checksum and reference validates. |

### 13.6 Proposed Gujarat target tree

```text
states/gujarat/
├── state.json
├── state.md
├── claims.jsonl
├── evidence.jsonl
├── evidence_manifest.csv
├── projects.jsonl
├── research_queue.jsonl
├── source_gaps.md
├── projects/
│   ├── stt-ahmedabad-dc1.md
│   ├── gujarat-state-data-centre.md
│   ├── lt-vyoma-dholera.md
│   ├── reliance-meta-jamnagar.md
│   └── data-first-ahmedabad.md
├── research/
│   ├── source-intake/
│   │   ├── 2026-07-19.md
│   │   └── 2026-07-20.md
│   └── audits/
│       ├── sources/
│       │   └── lt-vyoma-deep-research-report__2026-07-20.md
│       └── projects/
│           └── lt-vyoma-dholera__2026-07-20.md
└── evidence/
    └── <flat immutable evidence artifacts>
```

## 14. Migration approach

### Phase A - freeze and model

1. Preserve `india_state_bank.md` unchanged.
2. Preserve every current Gujarat file and checksum.
3. Create `state.json`, `claims.jsonl`, `evidence.jsonl`, `projects.jsonl` and `research_queue.jsonl` alongside the existing structure.
4. Map every legacy EID to a topic-neutral EID through `legacy_eids`.

### Phase B - validate Gujarat

1. Confirm every claim points to an existing evidence record.
2. Confirm every evidence artifact hash matches.
3. Confirm all project stages pass the escalation rules.
4. Confirm all negative findings have dates and search limitations.
5. Render `state.md` from validated claims plus explicit analyst sections.
6. Compare the rendered Gujarat section with the legacy bank and prepare a redline; do not replace it.

### Phase C - change the LLM mechanism

1. Keep deterministic state mapping.
2. Replace monolithic-bank retrieval with the state package.
3. Select exact field IDs/project IDs before retrieval.
4. Build the context pack from linked claims and evidence.
5. Require structured output and deterministic validation.
6. Render prose only after validation.
7. Preserve the current rule that states may enrich policy exposure but may not upgrade company role or priority without separate evidence.

### Phase D - roll out other states

For each state:

1. Create the canonical empty package.
2. Import existing legacy state text as historical claims.
3. Add only the evidence actually available.
4. Mark unverified fields honestly.
5. Generate research-queue entries from material decision gaps.
6. Produce `state.md` after claim validation.

No state is blocked merely because a topic has no evidence folder or minimum count.

## 15. Acceptance criteria

The architecture is acceptable when:

1. Every state uses the same eight analytical sections and field IDs.
2. Evidence storage has no mandatory topic folders.
3. One evidence record can support multiple claims and fields.
4. Every factual sentence in `state.md` resolves to claim IDs and evidence IDs.
5. Unknown, not-found and not-applicable states are distinguishable.
6. Project stages cannot be upgraded without the minimum evidence.
7. Superseded and incorrect claims remain auditable.
8. The query generator reads `research_queue.jsonl`, not directory emptiness.
9. The LLM receives only the matched state and requested fields/project.
10. Structured output is validated before persistence or rendering.
11. Gujarat's 72 existing evidence records migrate without deletion or checksum change.
12. `india_state_bank.md` remains unchanged until a separately approved production migration.

## 16. Decisions requested from the implementation planner

Claude or the implementation planner should decide:

1. Whether JSONL remains canonical or is backed by SQLite while retaining JSONL exports.
2. Whether `state.md` is fully generated or contains protected analyst-authored sections.
3. Whether topic-neutral EIDs are introduced immediately or only for new evidence.
4. How legacy EID aliases are exposed in UI and exports.
5. Whether the production dashboard reads state packages directly or a compiled aggregate.
6. Which deterministic validator owns claim scope, project-stage and policy-supersession checks.
7. How claim-level citations are rendered in the dashboard without exposing internal file paths.

The analytical and data contracts above should remain stable regardless of those implementation choices.
