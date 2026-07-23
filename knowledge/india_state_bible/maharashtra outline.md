# Maharashtra Data Centre Bible — Sequential Build Plan

## Document control

- State package: `knowledge/india_state_bible/states/maharashtra/`
- Plan archived: 2026-07-21
- Evidence cutoff at archive: 2026-07-21
- Protected legacy bank: `knowledge/india_state_bank.md`
- Protected-bank starting SHA-256: `a633f05e93d4b5e60c4eaa3b475028d745b0ef72664c004d483b2d751391b421`
- Preservation rule: the protected legacy bank is not edited during the Maharashtra build. Any later edit requires a separately approved redline.

## 1. Archive and scaffold

The canonical Maharashtra package uses this exact structure:

```text
knowledge/india_state_bible/states/maharashtra/
├── state_context.md
├── source_gaps.md
├── research_queue.xlsx
├── change_log.xlsx
└── source_library/
    ├── source_register.xlsx
    └── documents/
```

`state_context.md` contains all 22 universal headings. Unresearched sections are marked `BUILD STATUS — NOT YET RESEARCHED`; they are not presented as negative findings.

## 2. Repeatable part-by-part workflow

Every part follows the same gated cycle:

1. Search official portals, gazettes, regulators, government databases, company filings, project pages and credible reporting.
2. Download and authenticate every complete, readable document available.
3. Add source files and metadata to the Maharashtra source library.
4. Identify documents that are missing, incomplete, illegible, paywalled or unavailable in full.
5. Ask the user only for those unavailable materials, specifying the document, authority, date and relevance.
6. Incorporate supplied materials and document unresolved absence.
7. Write only the current part of the Maharashtra synthesis.
8. Update the source register, source gaps, research queue and change log together.
9. Validate citations, pinpoints, files, checksums, project stages and conflicting claims.
10. Report the completed part before opening the next one.

A part may proceed with a dated negative finding if the user confirms that an unavailable source cannot be supplied. Missing evidence is never silently converted into a factual conclusion.

## 3. Build sequence

### Part 1 — Foundation, legacy audit and policy stack

Research every existing Maharashtra claim and source in `india_state_bank.md`; historical IT, industrial and data-centre policy lineage; Maharashtra IT/ITeS Policy 2023; the Green Integrated Data Centre Park amendment and related GRs; Maharashtra Industries, Investment and Services Policy 2025; MAHITI; the MAITRI Act and Rules; implementation instruments; definitions and eligibility; ordinary and green-park incentives; stamp duty, electricity duty, tariff subsidy, land and FSI benefits; application, sanction, disbursement, monitoring and clawback rules; transitional and overlap treatment; negotiated packages; and essential-service and continuity provisions.

Build Sections 00, 04, 05, 06 and the policy-continuity portion of Section 15.

### Part 2 — Power and renewable energy

Build Section 07 using location- and licensee-specific evidence for MSEDCL, Tata Power, AEML, BEST and relevant deemed or estate licensees; HT/EHT tariffs; electricity duty; tariff subsidies; grid connection; dual feed; open access; captive structures; wheeling; transmission; banking; cross-subsidy surcharge; additional surcharge; renewable supply; storage; delivered cost and grid risk.

### Part 3 — Land, approvals, buildings, water and physical risk

Build Sections 08–10. Cover MIDC, MMRDA, CIDCO, PMRDA, municipal and planning pathways; title and allotment; zoning; FSI; fire; building; electrical and environmental approvals; water allocation; recycled water; groundwater; cooling; flood, coastal, heat, water, seismic and community risks; and stated SLA versus execution evidence.

### Part 4 — Geography, ecosystem, connectivity and demand

Build Sections 02, 03, 11, 12 and 18. Assess Greater Mumbai; Airoli–Rabale–Mahape and Navi Mumbai; Panvel–Palava–Taloja–Khalapur; Raigad–Pen; Pune/Hinjawadi; Nagpur/MIHAN; Nashik; Talegaon; Chhatrapati Sambhajinagar/AURIC; cable landings; IXPs; on-ramps; fibre diversity; BFSI, cloud, AI, enterprise, manufacturing and DR demand; talent; costs; and location comparisons.

### Part 5 — Companies and complete facility inventory

Build Section 13 and the project inventory supporting Section 14. Catalogue every source-qualified operational, under-construction, approved and announced facility and relevant operator, hyperscaler, carrier, utility, renewable provider, EPC contractor, equipment supplier, landowner, water provider, financier and adviser. Keep IT load, facility load, current building capacity and campus pipeline distinct.

### Part 6 — Established public and operating platforms

1. Maharashtra State Data Centre and MahaGov Cloud.
2. NTT Mumbai/Navi Mumbai.
3. STT GDC Mumbai–Mahape–Pune.
4. Yotta NM1/Panvel.
5. Sify Vashi–Airoli–Rabale.
6. Equinix MB1–MB4.

### Part 7 — Growth platforms and cloud regions

7. Iron Mountain/Web Werks Mumbai–Pune and MUM3.
8. Colt–RMZ Navi Mumbai.
9. Digital Edge Navi Mumbai.
10. AWS Mumbai Region.
11. Microsoft Pune/Central India.

### Part 8 — Green parks and mega-project proposals

12. Lodha/Palava Green Integrated Data Centre Park.
13. Adani’s proposed 500 MW Taloja project.
14. AirTrunk’s proposed 3 GW Raigad–Pen project.
15. Tata–MMRDA AI data-centre and Innovation City proposal.

Nxtra, CtrlS, Princeton Digital Group and other qualified operators remain in the complete inventory even if they are not full case studies. Evidence is verified through the actual build date in 2026. Any 2027 date is labelled as a future target and queued for later verification.

### Part 9 — Political economy, execution, risks and investment judgment

Complete Sections 01 and 15–21. Cover government-company engagement, continuity, incentive delivery, delays, cancellations, disputes, policy and execution risks, investability conditions, best-fit projects, business-development opportunities, diligence questions and the final source map.

## 4. Evidence and workbook controls

- Use `MH-SRC-YYYY-NNN`, `MH-GAP-NNN`, `MH-RQ-NNN` and `MH-CHG-YYYY-NNN`.
- Cite every factual paragraph and substantive table row with a source ID and pinpoint.
- Preserve full sources where available and record SHA-256 checksums.
- Distinguish announcement, MoU, offer, site control, approval, construction, energisation, operation and incentive disbursement.
- Convert unresolved material questions into source gaps and bounded research tasks.
- Match Gujarat workbook schemas and visual styling, enable filters at row 4 and freeze at `A5`.
- Apply the same non-content filter/freeze correction to Gujarat workbooks, with no other Gujarat changes.

## 5. Acceptance

Each part is complete only when its primary-source search is exhausted; unavailable documents have been requested; sources, citations, gaps, tasks and changes are synchronized; local paths and checksums validate; conflicts and stages are explicit; workbooks pass schema, validation, filter, freeze and rendering QA; unresearched sections remain clearly pending; and `india_state_bank.md` remains byte-for-byte unchanged.
