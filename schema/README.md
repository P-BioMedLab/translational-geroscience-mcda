# Data schemas

This folder defines the data contracts for all canonical inputs used by the MCDA analysis pipeline and the interactive web tool.

## Canonical domain codes (6)
- lifespan_efficacy
- healthspan_efficacy
- mechanism_conservation
- human_trial_evidence
- safety_tolerability
- cost_accessibility

## Display-name mapping
- Preclinical Efficacy (Lifespan) -> lifespan_efficacy
- Preclinical Efficacy (Healthspan) -> healthspan_efficacy
- Mechanism Conservation -> mechanism_conservation
- Human Trial Evidence -> human_trial_evidence
- Safety & Tolerability / Safety & Tolerability (in Humans) -> safety_tolerability
- Cost & Accessibility -> cost_accessibility

## Validation rules
- All domain scores must be within [1, 5].
- For each weighting scheme row, domain weights must sum to 1.0 (within floating tolerance).
