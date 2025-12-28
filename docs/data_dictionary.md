# Data dictionary

This repository uses four canonical input files located in `data/`. Schemas for each file are defined in `schema/`.

## 1) scoring_matrix.csv
**Purpose:** Defines the rubric for converting evidence into domain scores (1–5) for each of the six domains.

**Columns**
- `Score` (int, 1–5): rubric score level.
- `Preclinical Efficacy (Lifespan)` (text): definition for lifespan efficacy at each score.
- `Preclinical Efficacy (Healthspan)` (text): definition for healthspan efficacy at each score.
- `Human Trial Evidence` (text): definition for human evidence at each score.
- `Mechanism Conservation` (text): definition for mechanism conservation at each score.
- `Safety & Tolerability (in Humans)` (text): definition for human safety at each score.
- `Cost & Accessibility` (text): definition for accessibility at each score.

## 2) weighting_schemes.csv
**Purpose:** Specifies domain weight vectors used for baseline MCDA and stakeholder perspectives.

**Columns**
- `weighting_scheme` (string): scheme identifier (e.g., `baseline`, `regulator_focused`).
- Six domain weight columns: `lifespan_efficacy`, `healthspan_efficacy`, `mechanism_conservation`, `human_trial_evidence`, `safety_tolerability`, `cost_accessibility` (float 0–1).
- `description` (text): human-readable rationale.

**Rule:** Weights must sum to 1.0 for each row (within floating tolerance).

## 3) evidence_map.xlsx (sheet: evidence_map)
**Purpose:** Provides transparent justifications for each intervention’s domain score along with supporting references.

**Columns**
- `Intervention` (string): intervention label as used in the manuscript/tool.
- `Domain` (string): domain display label.
- `Score` (float 1–5): assigned score for that intervention-domain cell.
- `Evidence` (text): short justification for the assigned score.
- `Reference` (text): supporting citation string (often includes DOI and/or full citation).

## 4) lifespan_data.xlsx (sheet: All)
**Purpose:** Study-level extraction of lifespan effects plus derived scoring fields contributing to the Net Lifespan Score.

**Key columns**
- `Category` (string): intervention category label.
- `species`, `Strain`, `Delivery mode` (strings): experimental context.
- `Average Lifespan change` (float): extracted effect size (as recorded).
- `Transgenic/progeroid/diseased` (string): indicates special models where applicable.
- `ITP` (Yes/No): indicates whether evidence comes from the Interventions Testing Program.
- Derived scoring fields: `Lifespan score`, `Model score`, `Studies Count`, `Reproduced study score`, `Net Lifespan Score`.
- Citation fields: `Pubmed ID`, `DOI`, `Year`, `Main author`.
- Exclusions: `Excluded` (Yes/No) and `Limitation` (text).
