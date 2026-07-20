---
schema_version: "1.0"
state_name: "Gujarat"
state_code: "GJ"
document_status: "working"
last_substantive_update: "2026-07-20"
information_cutoff: "2026-07-20"
---

# Gujarat Data Centre Context

## 00. How to Use This Document

This is the canonical, comprehensive Gujarat context for the India Data Centre Bible. It should be supplied in full whenever an LLM answers a question materially concerning Gujarat, a Gujarat data-centre location, a Gujarat authority or a Gujarat project. Tags and source-ID prefixes are navigation aids only; they must not be used to retrieve isolated fragments while omitting surrounding qualifications.

The information cut-off is 20 July 2026. Power tariffs, surcharges, policy implementation instruments, project stages and company plans are date-sensitive. Material uncertainty is stated beside the affected analysis. The consolidated evidence-gap register is `source_gaps.md`; detailed research actions and corrections are maintained in `research_queue.xlsx` and `change_log.xlsx`.

Citations use permanent source IDs from `source_library/source_register.xlsx`. Existing category-coded IDs are legacy identifiers and remain stable. A citation to a policy shows an entitlement or rule; it does not prove that a named project received an incentive, approval, connection or allocation.

Project stages are conservative. “Announced,” “MoU signed,” “site controlled,” “permitted,” “under construction,” “commissioned” and “operational” are not interchangeable.

## 01. Executive State Context

### Current position

Gujarat now has a dedicated state data-centre policy. The official `Viksit Gujarat Data Center Policy (2026–2029)` booklet was launched on 9 July 2026 and is the present headline state framework for very large projects. The earlier position that Gujarat relied only on its IT/ITeS framework is historical and superseded as a current conclusion. [GJ-POL-2026-001, pp. 4–14] [GJ-GOV-2026-001] [GJ-GOV-2026-002]

The policy is deliberately hyperscale-oriented: only projects with approved installed IT load of at least 150 MW qualify. It targets aggregate installed capacity of 7.5 GW in the state and permits support only until that aggregate target is reached. [GJ-POL-2026-001, p. 13, cls. 7.6 and 7.9]

The strongest current investment proposition is a combination of long-duration operating incentives, Dholera-only capital support, building relaxations, renewable-energy access and government facilitation. The strongest current diligence warning is that the booklet omits its notification/GR metadata, contains an unresolved `XXXXXX` deadline in clause 5(h), depends on future implementation guidelines and had no completed online application workflow visible at the research cut-off. [GJ-POL-2026-001, pp. 8 and 14] [GJ-POL-2026-002]

### What exists and what is proposed

Verified operating or established facilities in the collected record include STT Ahmedabad DC1 at GIFT City, the Gujarat State Data Centre in Gandhinagar and Data First's Ahmedabad operation, although current capacity, approvals and operating evidence are uneven. [GJ-CORP-2023-001] [GJ-PROJ-2015-001] [GJ-PROJ-2010-001] [GJ-CORP-2026-003]

The most significant announced projects are:

- Reliance–Meta's 168 MW AI-enabled built-to-suit data centre in Jamnagar, announced for delivery within two years with an option to scale. Reliance says it will design, construct and operate the utility, renewable-power, network and managed-service stack, while Meta will lease capacity. Exact site, approvals and physical progress were not verified. [GJ-CORP-2026-001, pp. 1–2] [GJ-CORP-2026-002]
- L&T Vyoma's proposed 250 MW green AI-ready campus at Dholera, associated with an INR 25,000 crore proposal and a 2028 aspiration. The best evidence says the MoU contemplated a detailed feasibility assessment; no project-specific land, grid, water, approval, incentive, financing or construction record was publicly verified. [GJ-GOV-2026-003] [GJ-PROJ-2026-003]

### Decision summary

Gujarat is potentially attractive for new hyperscale and AI infrastructure that can clear the 150 MW threshold, structure renewable supply, tolerate implementation uncertainty and secure project-specific utility and permitting evidence. The dedicated policy is not designed for ordinary small and mid-sized colocation projects unless an aggregation or approved multi-entity structure satisfies the policy.

Dholera offers the clearest explicit capital-subsidy advantage but also carries the largest gap between city-level infrastructure claims and project-specific proof. GIFT City offers the strongest verified operating precedent and an identifiable regulated licensee. Jamnagar has a major sponsor-led AI case with primary company announcements, but the site and approval stack remain opaque. Ahmedabad/Gandhinagar has the clearest existing operating base but less direct fit with the 150 MW policy threshold.

## 02. State Geography and Economic Context

The 2026 policy presents Ahmedabad, Gandhinagar, Vadodara, Surat, Dholera SIR and GIFT City as parts of Gujarat's emerging digital economy. It also emphasizes the state's industrial base, special investment regions, renewable-energy position, high-speed connectivity and more than 5,000 ICT companies and 12,900 DPIIT-recognised startups. These figures are policy-booklet claims and have not been independently rebuilt in this package. [GJ-POL-2026-001, p. 5]

For data-centre analysis, Gujarat should not be treated as one uniform location:

- **GIFT City / Gandhinagar:** established financial-services and government demand, an operating enterprise facility and a distinct regulated electricity licensee.
- **Ahmedabad:** existing regional enterprise hosting and proximity to the Gandhinagar/GIFT cluster.
- **Dholera SIR:** planned industrial-city environment with a special development authority, DICDL infrastructure and explicit policy preference through a Dholera-only capital subsidy.
- **Jamnagar:** sponsor-led hyperscale AI logic tied to Reliance's industrial, renewable, fibre and water/desalination capabilities.
- **Surat and Vadodara:** identified by the policy as emerging digital-economy cities, but no source-qualified data-centre project case was established in the collected package.

Location-specific flood, storm-surge, cyclone, salinity, heat, seismic, drainage and water risks require plot-level work. General regional conditions cannot substitute for a site study.

## 03. Existing Data Centre Ecosystem

### Operating and established facilities

| Facility | Location | Defensible status | Evidence currently held | Principal limitation |
|---|---|---|---|---|
| STT Ahmedabad DC1 | GIFT City | Operational | STT's 2023 factsheet says operational since 2015; GIFT's page describes a purpose-built four-storey facility of approximately 70,000 sq ft, approximately 3 MW IT load, availability SLA up to 99.999 and TIA-942 Rated 4, plus listed certifications. | Specifications and certificates require current re-verification; current load, ownership chain, customers and expansion are not established. [GJ-CORP-2023-001] [GJ-PROJ-2015-001] |
| Gujarat State Data Centre | Gandhinagar | Established public-sector facility | DST says it was established in 2010 under the National e-Governance Plan, hosts state applications/data, provides compute, storage, network and security, has 30 Gbps redundant bandwidth and a cloud-enabled IaaS environment. | Precise current facility capacity, tier, refresh programme, operator contracts and any conflicting operational-date claim require reconciliation. [GJ-PROJ-2010-001] |
| Data First | Ahmedabad | Company-claimed operating regional facility | Company site says it owns and operates a Tier-III-built facility and DC/DR sites, provides colocation/cloud/hosting/security services and claims ISO/IEC 27001:2013. | Capacity, exact operating entity, certification validity, statutory approvals, current customers and independent operating proof are not established. [GJ-CORP-2026-003] |

### Scale limitation

The collected evidence does not establish Gujarat as a current metro-scale colocation market comparable with Mumbai or Chennai. A March 2026 PIB parliamentary-answer release reported national operational capacity above 1,500 MW through 2025 and listed major-city capacity without a Gujarat city. This is a dated national benchmark with definitional limits; it does not prove the absence of all Gujarat capacity or invalidate subsequent announcements. [GJ-CONN-2026-001]

### Announced pipeline

The two headline announced projects—Reliance–Meta Jamnagar and L&T Vyoma Dholera—would materially change the state's scale if executed, but neither announcement should be counted as operating capacity at the information cut-off. [GJ-CORP-2026-001] [GJ-GOV-2026-003] [GJ-PROJ-2026-003]

## 04. Policy, Law and Regulatory Lineage

### Current operative framework

The 2026 booklet says the policy comes into force from the date of notification and remains in operation for three years unless superseded earlier, with possible extension by the HPC/state government and annual review. Because the notification/GR number and date are not printed, the exact legal start and end dates are not independently fixed in this package. The title “2026–2029” and 9 July launch should not be substituted for missing notification metadata without the instrument. [GJ-POL-2026-001, p. 8, cl. 5(h)]

The policy says applicants claiming incentives under other Gujarat government policies may not claim incentives under this policy, while Government of India incentives may be additional. This prohibits an uncaveated assumption that 2022–27 state incentives and 2026 policy incentives can be stacked for the same applicant/project. [GJ-POL-2026-001, p. 9]

### Policy lineage

| Date/period | Instrument | Current relevance |
|---|---|---|
| 7 February 2022 | Gujarat IT/ITeS Policy 2022–27 | Historical/general IT framework and possible transition issue; not the complete current data-centre framework. [GJ-POL-2022-001] |
| 6 July 2022 | IT/ITeS implementation guidelines | GR No. ITP/10/2021/583612/IT; relevant to older applications and lineage. [GJ-POL-2022-002] |
| 11 October 2024 | Modification/addendum | Introduced/modified data-centre treatment under the 2022–27 framework; earlier 25% CAPEX/INR 150 crore and INR 1/unit descriptions must be read historically and reconciled against the dedicated policy. [GJ-POL-2024-001] |
| 2024 | Implementation-guideline amendment | Must be read with the October modification. [GJ-POL-2024-002] |
| January 2025 | Data-centre incentive EOI and bid document | Pre-2026 market-sounding/application evidence, not a final incentive award. [GJ-POL-2025-001] [GJ-POL-2025-002] |
| 9 July 2026 | Viksit Gujarat Data Center Policy launch | Current dedicated headline framework. [GJ-POL-2026-001] [GJ-GOV-2026-001] [GJ-GOV-2026-002] |
| 19 July 2026 | Portal status capture | Official portal said the application portal was under development. [GJ-POL-2026-002] |

### Governance

DST is the nodal department. The Office of the Director, Directorate of ICT and e-Governance, is the implementing office. The policy contemplates a High-Powered Committee for project approval, review, interpretation and in-principle approval and a State Level Empowered Committee for evaluation, approval and disbursement of assistance for HPC-approved projects. [GJ-POL-2026-001, pp. 8 and 14]

The policy says DST will issue detailed implementation guidelines. None had been source-qualified in the package by 20 July 2026. [GJ-POL-2026-001, p. 14]

## 05. Definitions and Project Eligibility

### Eligible entity

A “Data Centre Entity” may include a company, SPV, partnership, trust, body corporate or other legally recognised organisation that owns, leases, develops, establishes, holds or controls the land, building or core infrastructure of a data centre or integrated data-centre park, directly or through group entities, and is responsible for investment, development, operation, sub-leasing, management or administration. [GJ-POL-2026-001, p. 7, cl. 5(f)]

FCI and EFCI may be made independently or through a JV, SPV, subsidiary, affiliate, developer, operator, user entity or combination and aggregated for eligibility, capacity, incentive calculation, approval and disbursement, subject to conditions and HPC approval. This creates structural flexibility but not automatic aggregation; the approved entity/entities and implementation guidance matter. [GJ-POL-2026-001, p. 13, cl. 7.5]

### Capacity threshold

Only projects with approved installed IT load of at least 150 MW are eligible. “IT load” must not be confused with facility load, contract demand or substation MVA. The evidence package does not establish an independent policy definition resolving every boundary of “approved installed IT load.” [GJ-POL-2026-001, p. 13, cl. 7.6]

### Eligible investment

EFCI includes core technical infrastructure: buildings/civil construction, electrical systems, mechanical/cooling systems, backup power, captive BESS, data-centre-specific equipment, networking/cabling, security/fire systems and other essential fixed systems needed to make the facility operational. It excludes land, land development and semiconductor chips. [GJ-POL-2026-001, p. 7, cl. 5(d)]

EFCI considered under the policy may not exceed 80% of total FCI or INR 60,000 crore, whichever is lower, for a 1 GW project, with proportional adjustment for higher or lower approved capacity. The booklet does not itself provide a worked calculator for phased or mixed-use projects. [GJ-POL-2026-001, p. 7, cl. 5(d)]

### Eligible investment period

The period is eight years from in-principle approval. The HPC may extend it by up to two years case-by-case when substantial investment, significant implementation activity and satisfactory progress are demonstrated. [GJ-POL-2026-001, p. 7, cl. 5(e)]

### Applications and deadlines

The booklet says an entity must apply within three years of notification and receive in-principle approval by a date printed as `XXXXXX`. The unresolved placeholder makes the final approval deadline unusable without an official correction or implementation instrument. [GJ-POL-2026-001, p. 8, cl. 5(h)]

### Location treatment

The 150 MW threshold applies statewide on the face of the booklet. Capital subsidy is expressly Dholera-only. Other incentives are presented as statewide unless implementation guidance or another applicable instrument narrows them. [GJ-POL-2026-001, pp. 9–13]

### Items not established

The booklet does not establish a rack, processor-core, floor-area or Tier-certification threshold. Treatment of brownfield expansion, an existing facility combined with a new phase, common infrastructure shared across customers and exact commercial-operation certification requires implementation guidance or an HPC/SLEC decision.

## 06. Incentives and Government Support

### Financial incentives

| Incentive | Booklet position | Critical qualification |
|---|---|---|
| Dholera capital subsidy | 2.5% of EFCI made in the eligible investment period; claims may be submitted for up to ten years from in-principle approval. | Dholera only; EFCI, project approval and claim/disbursement rules still require implementation evidence. [GJ-POL-2026-001, p. 9] |
| Interest subsidy | Up to 4% for ten years, capped at INR 25 crore per year, on term-loan portion used for FCI. | “Term Loan” excludes NBFC loans and counts only actual disbursement. [GJ-POL-2026-001, pp. 8–9] |
| Power-tariff subsidy | INR 1/unit for twenty years from commercial operations. | Net delivered cost still depends on licensee, voltage, tariff, duties, OA charges and metering. [GJ-POL-2026-001, p. 9] |
| Stamp duty and registration | 100% exemption on amounts paid to government for land lease/purchase. | Legal mechanism, timing and eligible instrument need implementation treatment. [GJ-POL-2026-001, p. 9] |
| Electricity duty | 100% reimbursement of duty actually paid for twenty years from commercial operations, subject to law/rules. | Reimbursement is not necessarily upfront exemption. [GJ-POL-2026-001, p. 9] |
| SGST on plant and machinery | 100% of SGST eligible for reimbursement for eight years from in-principle approval to the extent of permanent ITC reversal. | Tax and documentation mechanics are material. [GJ-POL-2026-001, p. 9] |
| SGST on building/allied infrastructure consumption | Same eight-year/permanent-ITC-reversal formulation. | Exact eligible consumption and proof require guidance. [GJ-POL-2026-001, p. 9] |
| Net SGST on eligible operational services consumed in Gujarat | 100% reimbursement for twenty years from commercial operations. | “Eligible services,” place-of-supply and net-tax methodology need implementation detail. [GJ-POL-2026-001, p. 9] |
| Captive desalination support | 20% of eligible capex excluding land or INR 2 crore/MLD, whichever is lower; support up to 20 MLD for 1 GW, proportionally scaled. | Example caps: 10 MLD for 500 MW and 5 MLD for 250 MW; counts toward total financial-incentive ceiling. [GJ-POL-2026-001, p. 11] |

### Overall ceilings and disbursement

Total financial incentives are limited to 75% of EFCI made within eight years and disbursed over twenty years. Annual disbursement is capped at 5% of total eligible incentive; unused amount above the annual cap carries forward subject to the same annual and total caps. [GJ-POL-2026-001, pp. 12–13, cls. 7.2–7.4]

Capital subsidy on a captive BESS component may not exceed 10% of the total capital subsidy claimed. Because the general capital subsidy is Dholera-only, implementation guidance is needed before assuming a standalone BESS capital benefit elsewhere. [GJ-POL-2026-001, p. 13, cl. 7.10]

### State and central stacking

Government of India incentives may be additional. Applicants claiming incentives under other Gujarat government policies may not claim under this policy. Project-specific confirmation is necessary for legacy applications, multi-entity structures and benefits not characterised as “incentives.” [GJ-POL-2026-001, p. 9]

### Non-fiscal and building support

The policy provides for additional FSI under applicable DCR, parking at one equivalent car space per 1,000 sq m of designated office area, multi-level/rooftop stacking of utilities, DG sets and distribution transformers subject to applicable GDCR and fire NOC, up to 70% ground coverage, flexible floor-to-ceiling height within overall/NBC limits, rooftop chillers outside FAR subject to structural safety and AAI clearance, boundary walls up to 3.6 m, internal roads per fire norms and underground fire-water tanks in up to 50% of recreational-ground area. These policy statements still require local-rule implementation and project approval. [GJ-POL-2026-001, p. 10]

The policy also contemplates first-instance sub-letting without additional transfer charges or stamp duty subject to applicable law, 24x7 water to the doorstep, statutory-approval facilitation and processing through the Investor Facilitation Portal and/or DST portal. These are support commitments, not self-executing project rights. [GJ-POL-2026-001, p. 12]

### Sanction and disbursement evidence

No project-level 2026-policy application acknowledgement, in-principle approval, eligibility certificate, sanction order, claim approval, disbursement or clawback record was verified in the collected package.

## 07. Power and Energy

### Policy requirement

A data-centre entity must source at least 51% of electricity consumption for core operations from green and renewable energy. The booklet does not itself specify the annual/interval accounting method, treatment of RECs, storage, losses, captive structures or the denominator boundary. [GJ-POL-2026-001, p. 12, cl. 7.1]

The policy contemplates open access under prevailing regulations, state facilitation of two independent and electrically diverse incoming feeders from STU/CTU networks and possible facilitation of a distribution-license application by the entity or infrastructure co-developer. Facilitation is not a connectivity approval or guarantee. [GJ-POL-2026-001, p. 11]

### Regulatory stack

The collected stack includes the Gujarat Integrated Renewable Energy Policy 2025, the preserved 2023 policy and executive procedure, GERC Green Energy Open Access Regulations 2024 with five amendments through June 2026, RPO regulations and a time-limited additional-surcharge order. [GJ-POW-2023-001] [GJ-POW-2023-002] [GJ-POW-2024-001] [GJ-POW-2024-002] [GJ-POW-2025-001] [GJ-POW-2025-002] [GJ-POW-2026-003] [GJ-POW-2026-004] [GJ-POW-2025-003] [GJ-POW-2026-005]

The Energy and Petrochemicals Department's current index identifies the 2025 integrated policy and separately preserves the 2023 policy. It states that projects sanctioned under the 2023 policy may complete within their agreement timeline or six months, whichever is later. [GJ-POW-2026-007]

### Location-specific licensees

- **GIFT City:** GIFT Power Company Limited; FY2026–27 tariff schedule and GERC order are archived. [GJ-POW-2026-001] [GJ-POW-2026-002]
- **Dholera:** Torrent Power Limited–Distribution (Dholera); MYT/tariff materials and the FY2026–27 GERC order are archived. [GJ-POW-2024-003] [GJ-POW-2024-004] [GJ-POW-2025-005] [GJ-POW-2026-006]
- **Other Gujarat locations:** the applicable DISCOM or licensee must be identified for the exact site; no generic statewide tariff should be used.

### Dholera system evidence

DICDL describes two Torrent Power substations including a 400/220 kV GIS, current distribution capacity of 500 MVA scalable to 1,500 MVA and a GETCO 400 kV source under development for redundancy. TPL-D regulatory materials confirm an operational distribution framework, a commissioned 220/33/11 kV GIS and network/load-growth planning. None proves capacity reserved for L&T Vyoma or a 250 MW project connection. [GJ-LAND-2026-001] [GJ-POW-2024-003] [GJ-POW-2024-004] [GJ-POW-2025-005]

### Cost interpretation

NICDC published an indicative Dholera power figure of INR 5.80/unit on a page last updated 5 August 2025. It is not a binding quote, current tariff calculation or delivered hyperscale cost. A bankable model must use current tariff schedules, demand/energy charges, electricity duty, connection costs, transmission/wheeling, losses, banking, CSS, additional surcharge, standby and renewable-shaping costs for the actual structure. [GJ-PROJ-2025-001]

The archived additional-surcharge order expires 30 September 2026 and must be refreshed before use outside its period. [GJ-POW-2026-005]

## 08. Land, Planning and Buildings

### Dholera governance and baseline rules

Dholera land and planning involve DSIRDA and DICDL, with the Gujarat SIR/planning framework and development-control documents. The official 2012 Final Development Plan–DSIRDA Report 2/GDCR cover states that it was sanctioned by GIDB and came into force on 10 September 2012. Internal headers still say “Draft GDCR,” so the implementing gazette/resolution and complete amendment chain remain desirable authentication layers. [GJ-LAND-2012-001]

Section 10.5 establishes a Knowledge and IT Zone and requires an approved Campus Master Plan including an infrastructure/utilities plan. Table 10-4 provides plot, FAR, coverage, height and setback controls. The document does not separately define a data centre in the inspected permitted-use text, identify an L&T plot or prove a project approval. [GJ-LAND-2012-001, sec. 10.5 and table 10-4]

The private 273-page January 2012 mirror is an older draft and is not byte-identical to the 274-page government-hosted version. It is retained for comparison and must not replace the official baseline. [GJ-LAND-2012-002]

### Land process evidence

The library includes DICDL's land-allotment policy, a draft allotment-letter template and draft lease deed. They establish process fields and typical obligations, not an executed right for a named data-centre project. [GJ-LAND-2015-001] [GJ-LAND-2021-001] [GJ-LAND-2021-002]

NICDC published an indicative Dholera land rate of INR 2,750/sq m. This is dated city-level marketing information, not a plot offer, premium demand or executed land instrument. [GJ-PROJ-2025-001]

### Development permission

DSIRDA Form C and the current planning/forms page identify the development-permission channel and checklist environment. A blank form is not permission. No L&T Vyoma Campus Master Plan, development-permission order, sanctioned drawing, commencement record or occupancy document was found. [GJ-LAND-2025-001] [GJ-LAND-2026-004]

### Policy building relaxations

The 2026 policy provides a state support framework for FSI, parking, ground coverage, utility/DG stacking, height, rooftop chillers, boundary walls, internal roads and fire-water tanks. Each project still requires the applicable local authority to incorporate or approve the treatment under its development-control and safety rules. [GJ-POL-2026-001, p. 10]

### Other locations

Current land, sublease, title and development-control documents for STT at GIFT, Data First in Ahmedabad and the Reliance–Meta Jamnagar site were not assembled. The GIFT, municipal/area-development, revenue, SEZ and industrial-estate authority stack must be determined for each exact parcel.

## 09. Approvals and Compliance Path

### Policy administration

The likely policy sequence is portal application, scrutiny/evaluation, HPC in-principle/project approval, SLEC assistance approval/disbursement and continuing compliance, but the definitive forms, SLAs, document lists, appeals and disbursement sequence depend on implementation guidelines not yet held. [GJ-POL-2026-001, pp. 8, 12 and 14]

### Project approval stack

The exact stack varies by location and project design, but diligence should address:

1. applicant/SPV identity and corporate authority;
2. land/site control and certified use/zoning;
3. development permission, sanctioned plans and commencement;
4. grid load, STU/CTU interface, connection agreement and energisation;
5. water allocation, sewer/drainage and cooling design;
6. environmental applicability, GPCB consent and CRZ/groundwater decisions;
7. fire-plan approval, final fire certificate and renewals;
8. Chief Electrical Inspector and specialist approvals including fuel/BESS where applicable;
9. completion/occupancy/use permission and Consent to Operate where applicable; and
10. policy eligibility, sanction, claims, compliance and disbursement.

### Fire and electrical routes

The Gujarat Fire Safety Compliance Portal and citizen services portal describe the state channels for Fire Safety Plan Approval, Fire Safety Certificate Approval and renewal, including paperless application/status workflows. The captures do not establish any named project's certificate. [GJ-LAND-2026-005] [GJ-LAND-2026-006]

### Approval status

No complete public project approval stack was verified for L&T Vyoma/Dholera or Reliance–Meta/Jamnagar. Existing operational facilities also require current approval/renewal verification before transaction reliance.

## 10. Water, Environment and Physical Risk

### Policy position

The 2026 policy promises facilitation of 24x7 water to the doorstep and supports captive desalination. A promise of facilitation does not establish source, quantity, pressure, quality, delivery date, drought priority or project allocation. [GJ-POL-2026-001, pp. 11–12]

### Dholera water evidence

DICDL describes a 50 MLD water-treatment plant scalable to 150 MLD. NICDC published indicative treated-water and recycled-water figures of INR 71/KL and INR 25/KL. These are city-level capacity and dated indicative-rate statements, not a bulk-water agreement for a data centre. [GJ-LAND-2026-001] [GJ-PROJ-2025-001]

The DICDL water application form requires plot details, potable and recycled demand, GPCB-approved quantity, wastewater, source and connection information. It establishes process, not an allocation to L&T Vyoma. [GJ-WAT-2026-001]

### Regional environmental framework

The 19 September 2014 environmental clearance for DSIR records a long-term water concept, CRZ restrictions, water-source NOCs and conditions for individual industrial units. The 2016 material records transfer history. Neither is a project-specific clearance for a data centre. [GJ-ENV-2014-001] [GJ-ENV-2016-001]

CRZ EAC minutes for a Dholera solar-park proposal demonstrate that coastal regulation is material in parts of the region. They cannot be applied to an unidentified data-centre plot without a site map and project-specific applicability assessment. [GJ-ENV-2021-001]

### Jamnagar water and cooling

Reliance says the 168 MW Meta facility will be powered with renewable energy and cooled using desalinated seawater. This is a primary company commitment, but no project water balance, committed desalination capacity, intake/outfall approval, CRZ/EIA/GPCB package or commissioning schedule was held. [GJ-CORP-2026-001, p. 1]

### Physical-risk diligence

No project-specific flood-depth, storm-surge, cyclone, salinity/corrosion, heat, seismic, finished-floor-level or drainage study was held for the announced projects. Dholera and Jamnagar require particular coastal and water-system diligence; GIFT/Ahmedabad require urban/river/pluvial flood, heat and utility-redundancy assessment. These are diligence requirements, not findings that a particular site is unacceptable.

## 11. Connectivity and Digital Infrastructure

### Cable landing stations

Gujarat issued a January 2025 EOI for cable landing stations and a materially revised July 2025 EOI. The July instrument removed earlier INR 500 crore turnover/project-experience tests and clarified that admissible GFCI concerned CLS civil works and network hardware, excluding cable laying and network cables. The July document supersedes the January market-sounding instrument, but remains an EOI rather than an award or concession. [GJ-CONN-2025-001] [GJ-CONN-2025-002]

No award, concession agreement, definitive landing site, named cable system, construction contract or ready-for-service date was verified.

The March 2026 PIB release lists commissioned/planned cable systems at Mumbai, Chennai and Raigad locations but no Gujarat landing station. Treat this as a dated official national table, not proof against a later Gujarat project. [GJ-CONN-2026-001]

### Fibre and interconnection

Reliance says the Jamnagar project will benefit from proximity to western submarine-cable landing stations and Jio's fibre network and that Reliance will provide network connectivity. Exact routes, physically diverse entrances, carrier-neutrality and interconnection commitments were not disclosed in the held release. [GJ-CORP-2026-001]

STT/GIFT and Data First materials support existing connectivity/hosting use, but a current carrier inventory, PeeringDB/IXP map, route-diversity analysis and latency comparison with Mumbai were not completed.

## 12. Demand, Customers, Talent and Operating Economics

### Demand anchors

Gujarat's plausible demand anchors include GIFT/IFSC financial services, state e-governance, Gujarat enterprise/manufacturing demand, cloud and DR workloads and sponsor-led AI demand at Jamnagar. The only specifically named hyperscale customer in the held project evidence is Meta for Reliance's announced built-to-suit Jamnagar facility. [GJ-CORP-2026-001] [GJ-CORP-2026-002]

The GSDC provides a demonstrated state-government workload base. STT Ahmedabad DC1 and Data First demonstrate enterprise/colocation/managed-service presence, but customer lists, utilisation and churn are not public in the collected material. [GJ-PROJ-2010-001] [GJ-PROJ-2015-001] [GJ-CORP-2026-003]

### Market position

The policy seeks to position Gujarat as a hyperscale AI destination, but policy ambition and announced capacity should not be used as current market absorption. Gujarat may function as a complement, disaster-recovery location or future competitor to Mumbai depending on cable execution, carrier depth, customer commitments and operating-cost delivery. A quantified latency, demand and total-cost comparison has not yet been completed.

### Talent

The policy identifies job and skill development across data centres, cloud engineering, cybersecurity and emerging technologies as objectives. A Gujarat-specific data-centre labour pool, wage benchmark, operations staffing model and training-provider inventory were not established. [GJ-POL-2026-001, p. 6]

### Operating economics

No universal Gujarat operating-cost figure is defensible. Economics must be built for the exact location and design, including power structure, demand/energy charges, open-access costs, water/cooling, land, local development charges, redundancy capex, fibre, taxes, incentives, compliance and the timing/risk of disbursement.

## 13. Companies and Data Centre Value Chain

### Operators, platforms and customers

| Company/entity | Gujarat role | Location | Stage/evidence |
|---|---|---|---|
| ST Telemedia Global Data Centres | Enterprise colocation/data-centre operator | GIFT City | Operating DC1; current specifications need refresh. [GJ-CORP-2023-001] [GJ-PROJ-2015-001] |
| Government of Gujarat / GSDC | Public-sector shared hosting and cloud-enabled e-governance infrastructure | Gandhinagar | Established since 2010 per DST. [GJ-PROJ-2010-001] |
| Data First | Regional colocation, hosting, cloud and DR provider | Ahmedabad | Company-claimed operating facility; independent capacity/compliance verification outstanding. [GJ-CORP-2026-003] |
| Reliance Industries | Developer/operator and end-to-end service provider for announced Meta facility | Jamnagar | Primary announcement; 168 MW within two years with scale option. [GJ-CORP-2026-001] |
| Meta Platforms | Anchor tenant/customer for announced AI-enabled built-to-suit capacity | Jamnagar | Primary counterpart announcement; exact commercial terms not public. [GJ-CORP-2026-002] |
| Larsen & Toubro / Vyoma | Sponsor of proposed Dholera AI-ready campus; broader Indian DC/AI infrastructure business | Dholera proposal | MoU/pre-feasibility; no project SPV or execution stack verified. [GJ-CORP-2025-001] [GJ-PROJ-2026-003] |
| NVIDIA | National AI-factory collaboration with L&T | No Gujarat site established | L&T release names Chennai/Mumbai deployment context, not Dholera. [GJ-CORP-2026-005] |

### Utilities and authorities

Relevant organisations include GIFT PCL, Torrent Power Distribution–Dholera, GETCO, Gujarat SLDC, GERC, Gujarat renewable-energy authorities, DICDL, DSIRDA, GIFT City entities, local development authorities, GPCB and fire/electrical authorities. Their involvement is location- and approval-specific.

### Value-chain gaps

A systematic Gujarat inventory of EPC contractors, cooling vendors, UPS/battery/transformer suppliers, fibre carriers, renewable developers, water/desalination providers, real-estate firms, financiers and advisors has not yet been completed. Company presence should not be inferred merely from a national operation.

## 14. Projects and Case Studies

### 14.1 STT Ahmedabad DC1 at GIFT City

**Status:** Operational.

STT's factsheet says the facility has operated since 2015. GIFT's page describes it as a purpose-built four-storey reinforced-concrete facility of approximately 70,000 sq ft and approximately 3 MW IT load, with an availability SLA up to 99.999, TIA-942 Rated 4 and listed ISO, PCI DSS, TL 9000, SOC and green-building certifications. [GJ-CORP-2023-001] [GJ-PROJ-2015-001]

The case establishes that enterprise-grade operation at GIFT predates the 2026 policy. It does not establish that the facility qualifies for a policy whose minimum is 150 MW. Current title/lease, GIFT PCL load, redundancy, renewable sourcing, water/cooling, statutory renewals, customers, utilisation and expansion remain to be verified.

### 14.2 Gujarat State Data Centre

**Status:** Established public-sector operation.

DST describes GSDC as India's first state data centre implemented under the National e-Governance Plan, established in 2010 as a central repository for Gujarat government data, applications and services. It provides shared compute, storage, network and security resources, 30 Gbps bandwidth with redundancy and cloud-enabled IaaS for departments and offices. [GJ-PROJ-2010-001]

The case demonstrates public-sector digital-infrastructure continuity and government workload. Current equipment capacity, facilities standard, service availability, contracts and refresh programme were not established.

### 14.3 L&T Vyoma / Dholera

**Status:** MoU signed / feasibility or pre-development.

On 20 February 2026, Gujarat's Science and Technology leadership announced an MoU concerning a proposed 250 MW green AI-ready Dholera campus associated with INR 25,000 crore. The most detailed contemporaneous report quotes a Gujarat government statement saying L&T Vyoma would conduct a detailed feasibility assessment covering land suitability, infrastructure readiness, availability zones and sustainability. The 2028 timing is an aspiration, not a verified COD. [GJ-GOV-2026-003] [GJ-PROJ-2026-001] [GJ-PROJ-2026-002] [GJ-PROJ-2026-003]

L&T's official rebranding material describes Vyoma as its data-centre business, not necessarily a separate legal entity. The signed MoU must identify the contracting entity and any nominated SPV. [GJ-CORP-2025-001]

L&T's FY2025–26 annual report reports 26 MW across Chennai/Panvel and a Mahape development but does not identify Dholera in its Vyoma development discussion. Its May 2026 earnings transcript discusses roughly INR 10,000 crore of data-centre capital outlay and about 200 MW over time, naming Vizag, Bengaluru and Mumbai, not Dholera. The current Vyoma upcoming page lists other cities and omits Dholera. These omissions are dated negative evidence, not proof of abandonment. [GJ-CORP-2026-004] [GJ-CORP-2026-006] [GJ-PROJ-2026-004]

DICDL site searches returned no indexed result for “Vyoma” or “data centre” at the cut-off. This does not prove the absence of non-public or unindexed files. [GJ-PROJ-2026-005] [GJ-PROJ-2026-006]

No signed MoU, completed feasibility report, plot instrument, possession, 250 MW grid sanction, water allocation, development permission, environmental consent, incentive sanction, financing, EPC notice or construction evidence was verified. City-wide Dholera infrastructure cannot fill those gaps.

### 14.4 Reliance–Meta / Jamnagar

**Status:** Announced under primary company agreement statements; execution records not yet verified.

Reliance's 10 June 2026 release says RIL and Meta agreed to develop a 168 MW AI-enabled data centre in Jamnagar, to be delivered within two years with an option to scale. It describes the project as Meta's first built-to-suit data-centre capacity in India, says Meta will lease capacity and assigns RIL end-to-end design, construction, utility, renewable-power, network and managed-service responsibilities. It also says the facility will use renewable power and desalinated-seawater cooling. Meta issued a primary counterpart announcement. [GJ-CORP-2026-001, pp. 1–2] [GJ-CORP-2026-002]

The underlying agreement, exact site/coordinates, phase/load definitions, land right, grid source/sanction, renewable structure, desalination allocation and approvals, building/fire/environmental package, incentive treatment, EPC evidence and actual construction progress were not in the collected record.

### 14.5 Data First / Ahmedabad

**Status:** Company-claimed operating regional facility.

Data First's website says it owns and operates a facility built to Tier-III standards and provides colocation, VPS, cloud, storage/backup, dedicated servers, DR and security. It claims ISO/IEC 27001:2013 and multiple Tier 1 ISP access. [GJ-CORP-2026-003]

Exact rack/IT-load capacity, facility address/title, operating entity, commissioning history, certification scope/validity, power, water, statutory approvals and expansion are not source-qualified.

## 15. Government, Political Economy and Policy Continuity

The 9 July 2026 launch is supported by the official policy booklet, Gujarat Directorate of Information release, Akashvani and the CMO launch video. The government launch narrative includes a 7.5 GW ambition and links the policy to green energy and desalination. The booklet remains the controlling source for clause-level statements. [GJ-POL-2026-001] [GJ-GOV-2026-001] [GJ-GOV-2026-002] [GJ-TRANS-2026-001]

The bilingual launch transcript is a useful searchable aid but is user-supplied, edited rather than official/verbatim and differs in recorded duration from the official player. Use it for discovery and timestamp targeting, not as a substitute for the policy or verified video wording. [GJ-TRANS-2026-002]

The Science and Technology Minister's verified announcement provides official political confirmation of the L&T Vyoma MoU and headline proposal. It does not supply the signed instrument or execution proof. [GJ-GOV-2026-003]

Policy continuity risk is moderated by the booklet's HPC extension power and annual review but increased by the short three-year application window, 20-year disbursement horizon, missing notification metadata, unresolved deadline placeholder and future implementation guidelines. The 2025 renewable-policy index provides an express transition for projects sanctioned under the 2023 renewable policy, showing one example of continuity treatment; it does not answer data-centre-policy grandfathering. [GJ-POL-2026-001, p. 8] [GJ-POW-2026-007]

No systematic record of assembly questions, opposition statements, manifesto commitments, local-government positions, community objections or civil-society views was completed. No political motive should be inferred from that absence.

## 16. Execution Record and Delivery Capacity

### Demonstrated execution

Gujarat has demonstrated operation of public-sector and enterprise facilities through GSDC, STT at GIFT and Data First, though these are much smaller than the 150 MW policy threshold on the evidence held. [GJ-PROJ-2010-001] [GJ-PROJ-2015-001] [GJ-CORP-2026-003]

Dholera records demonstrate planning, land-allotment processes, regional environmental clearance, utility infrastructure and industrial-corridor monitoring. NICDC's June 2026 monitoring report says Dholera Phase I trunk infrastructure is complete and reports 300 MW commissioned in the 1,000 MW solar park. A different sentence in that report concerning completed external road, power and water connectivity belongs to Nangal Chaudhary, Haryana and must not be attributed to Dholera. [GJ-PROJ-2026-007, p. 1 and p. 3]

### Gap between policy and project execution

No source in the package proves a final 2026-policy incentive sanction or disbursement. No public record proves that the 250 MW Dholera proposal progressed beyond feasibility/pre-development. The Reliance–Meta announcement is more specific about capacity, delivery responsibilities and customer structure, but project-specific regulatory and construction evidence is still missing.

### Evidence needed to upgrade project stage

- **Site controlled:** executed registered land right plus possession.
- **Grid/water reserved:** project-specific sanction/allocation and binding agreement.
- **Materially permitted:** valid development, fire and environmental approvals for the phase.
- **Under construction:** commencement/EPC/independent physical evidence.
- **Commissioned:** energisation, completion/occupancy, operating approvals and integrated testing.
- **Operational:** customer/IT-load evidence and continuing compliance.
- **Incentive disbursed:** payment, credit or treasury evidence.

## 17. Risks, Conflicts and Unresolved Questions

### Policy and legal risk

- Notification/GR number, notification date and exact operative expiry are not established.
- Clause 5(h)'s in-principle-approval deadline is an unresolved placeholder.
- Implementation guidelines, application forms, SLAs, appraisal methods and appeals were not held.
- Treatment of legacy 2022–27 applications and anti-duplication across state schemes needs formal clarification.

### Incentive risk

- Eligibility is restricted to at least 150 MW approved installed IT load.
- Disbursement extends across twenty years and is capped annually.
- Reimbursement design exposes the investor to timing, documentation, budget and compliance risk.
- No named project sanction/disbursement record was verified.

### Power risk

- 51% green-energy accounting methodology is unclear.
- Dual-feed and distribution-license language is facilitative, not a guaranteed project right.
- OA costs and surcharges are time-sensitive; the held additional-surcharge order expires 30 September 2026.
- General Dholera capacity is not a project reservation.

### Land, approvals and construction risk

- Dholera's 2012 GDCR needs a current consolidated amendment chain.
- Data-centre use and ancillary utility treatment require plot-specific confirmation.
- Announced projects lack publicly verified complete land and approval stacks.

### Water and environmental risk

- 24x7 water language does not establish source or binding allocation.
- Desalination introduces intake/outfall, energy, coastal and schedule dependencies.
- Coastal, flood, storm-surge, salinity and drainage risk is not resolved at plot level.

### Connectivity and market risk

- Gujarat's cable-landing evidence is at EOI stage.
- Carrier-neutral depth, route diversity, latency and interconnection were not fully mapped.
- Announced capacity can precede actual customer absorption and ecosystem depth.

### Project-stage conflict

Public shorthand sometimes describes L&T Vyoma as building a Dholera campus. The more precise government-quoted record says a feasibility assessment was the contemplated next step. The project must remain MoU/pre-development until higher-stage evidence appears. [GJ-PROJ-2026-003]

## 18. Location-by-Location Assessment

| Location | Verified strengths | Principal gaps/risks | Current fit |
|---|---|---|---|
| GIFT City / Gandhinagar | Operating STT facility; GSDC government workloads; GIFT PCL tariff/order; financial-services/IFSC context. | Current DC1 capacity/approvals/expansion, carrier depth, renewable and water evidence. | Enterprise, regulated financial-services, government and DR use; standalone existing facilities do not meet 150 MW policy threshold. |
| Ahmedabad | Existing Data First operation and proximity to GIFT/Gandhinagar. | Independent capacity/certification/compliance data and quantified market depth. | Regional enterprise, cloud, managed hosting and DR; hyperscale case not established. |
| Dholera SIR | Dholera-only 2.5% EFCI subsidy; planned land/infrastructure environment; TPL-D framework; renewable/industrial-corridor development. | Exact plot/use, 250 MW grid, water, current GDCR, approvals, cable depth and project execution. | Large greenfield hyperscale/AI projects capable of absorbing development risk; not yet proven by Vyoma execution. |
| Jamnagar | Primary Reliance–Meta 168 MW built-to-suit announcement; sponsor claims integrated renewable, fibre and desalination capabilities. | Underlying agreement, site, approvals, connection, water/desalination and construction proof. | Sponsor-led captive/built-to-suit AI infrastructure rather than an independently verified open colocation cluster. |
| Surat | Policy-recognised emerging digital economy. | No source-qualified facility/project, utility or market case in current library. | Not established. |
| Vadodara | Policy-recognised emerging digital economy. | No source-qualified facility/project, utility or market case in current library. | Not established. |

## 19. Investment and Business-Development Judgment

### Best-fit projects

- Greenfield hyperscale or AI campuses at or above 150 MW that can exploit long-duration power/duty support.
- Dholera projects able to capture the location-specific capital subsidy and control the land/grid/water critical path.
- Sponsor-led built-to-suit projects with integrated renewable power, fibre and water capability, as illustrated by the Reliance–Meta announcement.
- Financial-services, government, DR and regulated workloads around GIFT/Gandhinagar, even where the new policy may not apply.

### Poor-fit or conditional projects

- Small/medium standalone colocation projects expecting to qualify under the 2026 policy without an approved aggregation structure.
- Projects relying on generic Dholera utility claims instead of binding capacity and delivery commitments.
- Projects whose economics require prompt incentive cash receipts despite the twenty-year/annual-cap structure.
- Projects assuming a Gujarat cable landing station is operational or contractually committed.

### Conditions before an investment decision

1. Obtain the official policy notification/GR, implementation guidelines and clause 5(h) correction.
2. Secure written eligibility and anti-duplication treatment for the exact legal/project structure.
3. Model gross and net delivered power under the actual licensee/open-access structure.
4. Obtain land, zoning, grid, water, drainage, environmental, fire and building evidence for the exact phase.
5. Stress-test delayed incentives, utility augmentation, cable delays and project phasing.
6. Treat every MoU and company announcement as a starting point for diligence, not execution proof.

### Business-development opportunities

The strongest evidence-backed opportunity areas are policy/application advisory for 150 MW+ projects, project-specific land/grid/water diligence, renewable/open-access structuring, coastal/desalination engineering, Dholera utility and approval coordination, GIFT/financial-services infrastructure and independent construction/compliance verification. Vendor opportunities should be qualified against real projects rather than the 7.5 GW policy target alone.

## 20. State-Specific Additional Context

### Dholera SIR is both an incentive geography and a separate execution system

Dholera is not merely another Gujarat site. It combines the only express capital-subsidy geography in the 2026 policy with DSIRDA/DICDL planning and land processes, a distinct TPL-D distribution area, regional environmental history and planned-city infrastructure. An LLM answer about “Gujarat incentives” must therefore identify whether the project is in Dholera, while an answer about “Dholera readiness” must separate general regional infrastructure from the named project's rights.

### GIFT City combines operating precedent with a distinct regulated environment

GIFT provides the clearest private operating precedent in the current Gujarat record and a separate GIFT PCL tariff/order stack. Its IFSC and enterprise context can create demand that differs from an open hyperscale campus. GIFT-specific land, SEZ/IFSC, utility and building treatment should not be inferred from Dholera or statewide rules.

### The dedicated policy is intentionally not universal

The 150 MW minimum means the 2026 policy should not be described as a general incentive scheme for every data centre in Gujarat. Existing smaller facilities remain important market evidence but may sit outside the dedicated policy unless a future approved aggregation or expansion structure qualifies.

### Essential-service designation

The policy says operation, management, maintenance and support of data centres operating in Gujarat shall be treated as an essential service under the Gujarat Essential Services Maintenance Act, 1972. The implementation and labour-law consequences should be interpreted with legal advice rather than assumed from the booklet alone. [GJ-POL-2026-001, p. 13, sec. 8]

## 21. Source Reference Map

The source register contains full metadata, URLs, local paths, checksums and limitations. This map gives the LLM enough context to interpret citations.

### Policy, law and government

- `GJ-POL-2022-001` — Gujarat IT/ITeS Policy 2022–27; official historical/general framework.
- `GJ-POL-2022-002` — July 2022 official implementation guidelines.
- `GJ-POL-2024-001` — October 2024 government modification/addendum including data-centre treatment.
- `GJ-POL-2024-002` — corresponding implementation-guideline amendment.
- `GJ-POL-2025-001` — January 2025 official EOI for companies seeking data-centre incentives.
- `GJ-POL-2025-002` — January 2025 EOI bid document.
- `GJ-POL-2026-001` — official Viksit Gujarat Data Center Policy 2026–2029 booklet; user-authenticated official copy.
- `GJ-POL-2026-002` — official DST incentive-portal launch/status capture.
- `GJ-POL-2026-003` — official Gujarat DST IT/ITeS policy index.
- `GJ-POL-2026-004` — official Gujarat DST government-resolution index.
- `GJ-GOV-2026-001` — Akashvani policy-launch report.
- `GJ-GOV-2026-002` — official Gujarat Directorate of Information launch release, preserved in JSON and HTML.
- `GJ-GOV-2026-003` — verified ministerial announcement of the L&T Vyoma MoU.
- `GJ-TRANS-2026-001` — official CMO Gujarat policy-launch video record.
- `GJ-TRANS-2026-002` — user-supplied bilingual launch transcript; edited research aid.
- `GJ-TRANS-2026-003` — user-supplied L&T Vyoma deep-research report; discovery aid with non-portable citations.

### Power and renewable energy

- `GJ-POW-2023-001` — Gujarat Renewable Energy Policy 2023.
- `GJ-POW-2023-002` — GEDA executive procedure under the 2023 policy.
- `GJ-POW-2024-001` — GERC Green Energy Open Access Regulations 2024.
- `GJ-POW-2024-002` — first GEOA amendment.
- `GJ-POW-2024-003` — TPL-D Dholera MYT/tariff petition and network evidence.
- `GJ-POW-2024-004` — TPL-D Dholera MYT executive summary.
- `GJ-POW-2025-001` — second GEOA amendment.
- `GJ-POW-2025-002` — third GEOA amendment.
- `GJ-POW-2025-003` — GERC Renewable Purchase Obligation Regulations 2025.
- `GJ-POW-2025-004` — Gujarat Integrated Renewable Energy Policy 2025.
- `GJ-POW-2025-005` — GERC TPL-D Dholera FY2025–26 MYT/tariff order.
- `GJ-POW-2026-001` — GIFT PCL FY2026–27 tariff schedule.
- `GJ-POW-2026-002` — GIFT PCL FY2026–27 tariff order.
- `GJ-POW-2026-003` — fourth GEOA amendment.
- `GJ-POW-2026-004` — fifth GEOA amendment.
- `GJ-POW-2026-005` — additional-surcharge order for April–September 2026.
- `GJ-POW-2026-006` — TPL-D Dholera FY2026–27 tariff order.
- `GJ-POW-2026-007` — official current Gujarat renewable-policy index and transition statement.

### Land, planning, water and environment

- `GJ-LAND-2012-001` — government-hosted sanctioned/effective 2012 Dholera Final DP/GDCR baseline.
- `GJ-LAND-2012-002` — older unofficial draft mirror retained for version comparison.
- `GJ-LAND-2015-001` — DICDL land-allotment policy.
- `GJ-LAND-2021-001` — DICDL draft allotment-letter template.
- `GJ-LAND-2021-002` — DICDL draft lease-deed template.
- `GJ-LAND-2022-001` — DICDL FY2021–22 annual report.
- `GJ-LAND-2023-001` — DSIRDA FY2022–23 annual report.
- `GJ-LAND-2025-001` — DSIRDA Form C development-permission application.
- `GJ-LAND-2026-001` — DICDL completed-infrastructure page with general power/water claims.
- `GJ-LAND-2026-004` — current Dholera planning/forms page.
- `GJ-LAND-2026-005` — Gujarat Fire Safety Compliance Portal.
- `GJ-LAND-2026-006` — Gujarat citizen fire-services portal.
- `GJ-WAT-2026-001` — DICDL water-supply application form.
- `GJ-ENV-2014-001` — DSIR umbrella environmental clearance.
- `GJ-ENV-2016-001` — DSIR environmental-clearance transfer material.
- `GJ-ENV-2021-001` — CRZ EAC minutes for Dholera solar-park context.

### Connectivity and market

- `GJ-CONN-2025-001` — January 2025 cable-landing-station EOI; superseded by July reissue.
- `GJ-CONN-2025-002` — materially revised July 2025 cable-landing-station EOI; not an award.
- `GJ-CONN-2026-001` — March 2026 PIB national capacity and submarine-cable parliamentary-answer release.

### Facilities, projects and companies

- `GJ-PROJ-2010-001` — official Gujarat State Data Centre page.
- `GJ-PROJ-2015-001` — official GIFT page for STT Ahmedabad DC1.
- `GJ-PROJ-2025-001` — NICDC Dholera project page with dated indicative rates/readiness claims.
- `GJ-PROJ-2026-001` — Akashvani L&T Vyoma/Dholera announcement.
- `GJ-PROJ-2026-002` — Angel One secondary L&T Vyoma article.
- `GJ-PROJ-2026-003` — Indian Express report quoting the Gujarat feasibility-assessment statement.
- `GJ-PROJ-2026-004` — L&T Vyoma current upcoming-data-centres page.
- `GJ-PROJ-2026-005` — DICDL site search for “Vyoma”; dated zero-result capture.
- `GJ-PROJ-2026-006` — DICDL site search for “data centre”; dated zero-result capture.
- `GJ-PROJ-2026-007` — NICDC June 2026 industrial-corridor monitoring report.
- `GJ-CORP-2023-001` — STT Ahmedabad DC1 facility factsheet.
- `GJ-CORP-2025-001` — L&T rebranding release for Vyoma.
- `GJ-CORP-2025-002` — L&T annual-review data-centre roadmap page.
- `GJ-CORP-2026-001` — Reliance primary 168 MW Meta/Jamnagar release.
- `GJ-CORP-2026-002` — Meta primary counterpart announcement.
- `GJ-CORP-2026-003` — Data First Ahmedabad website capture.
- `GJ-CORP-2026-004` — L&T FY2025–26 integrated annual report filed with BSE.
- `GJ-CORP-2026-005` — L&T–NVIDIA national AI-factory release; does not establish Dholera participation.
- `GJ-CORP-2026-006` — L&T Q4/FY26 earnings-call transcript.

