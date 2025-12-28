[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18075835.svg)](https://doi.org/10.5281/zenodo.18075835)

# Geroscience Interventions Ranking Framework

## Overview

This repository contains the computational framework, scoring matrices, and interactive tools supporting the multi-criteria decision analysis (MCDA) of 30 geroscience interventions. The framework evaluates translational readiness across six domains: preclinical efficacy (lifespan and healthspan), mechanism conservation, human trial evidence, safety and tolerability, biomarker availability, and cost-accessibility.

## Key Features

- **Quantitative ranking** of 30 interventions from repurposed drugs (metformin, rapamycin, acarbose) to frontier modalities (senolytics, epigenetic reprogramming, CAR-T therapies)
- **Weighted scoring system** prioritizing human safety and clinical evidence while preserving preclinical impact
- **Monte Carlo uncertainty analysis** with 95% credible intervals and sensitivity testing across stakeholder perspectives (regulators, investors, patients)
- **Interactive web calculator** allowing custom weighting schemes and real-time ranking updates
- **Fully reproducible pipeline** that generates all analyses and figures from raw input data

## Repository Structure

```
translational-geroscience-mcda/
├── analysis/
│   └── mc_ranking_analysis.py    # All-in-one analysis script
│
├── data/
│   ├── Intervention_scores.xlsx           # Raw domain scores (input)
│   ├── scoring_matrix.csv                 # Scoring rubric (1-5)
│   ├── weighting_schemes.csv              # Stakeholder weight profiles
│   ├── evidence_map.csv                   # Links between scores and primary sources
│   └── lifespan_data.xlsx                 # Raw lifespan data
│
├── output/                                 # Generated outputs
│   ├── Intervention_list_&_scores.xlsx    # Enriched dataset with computed metrics
│   ├── weighted_score_intervals.csv       # Score uncertainty (95% CI)
│   ├── ranking_robustness_weights_±5%.csv # Rank stability analysis
│   └── Figure*.tiff, *.eps                # Publication figures (if generated)
│
├── interactive_tool/
│   ├── app.py                             # Web application backend
│   └── Interactive Geroscience Interventions Ranking.html # Web tool
│
├── docs/                                   # Documentation
│
├── run_pipeline.py                        # One-command pipeline orchestrator
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/P-BioMedLab/translational-geroscience-mcda.git
cd translational-geroscience-mcda

# Install dependencies
pip install numpy pandas matplotlib openpyxl scipy
```

### Run Complete Analysis

**Option 1: One Command (Recommended)**
```bash
python run_pipeline.py
```
This runs the complete pipeline in ~2-5 minutes and generates all outputs in the `output/` directory.

**Option 2: Run Analysis Script Directly**
```bash
python analysis/mc_ranking_analysis.py \
    -i data/Intervention_scores.xlsx \
    -r 10000 \
    -o output/
```

**Quick Test Run**
```bash
python run_pipeline.py --mc-runs 1000 -o test_output/
```

## Requirements

- Python 3.8 or higher
- NumPy 1.20+
- Pandas 1.3+
- Matplotlib 3.4+
- openpyxl 3.0+
- SciPy 1.10+ (for web tool only)
- Streamlit 1.28+ (for interactive tool only)

All dependencies are specified in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Launch interactive web tool

Open the HTML file directly in your browser:

[Access Live Demo](https://htmlpreview.github.io/?https://github.com/P-BioMedLab/translational-geroscience-mcda/blob/main/interactive_tool/Interactive%20Geroscience%20Interventions%20Ranking.html)

Or run the deployed version at: https://translational-geroscience-mcda-ranking.streamlit.app/

## Scoring Methodology

Each intervention receives scores from 1-5 across six domains according to predefined rubrics. Final weighted scores are calculated as:

```
Weighted Score = Σ(Domain_Score_i × Weight_i)
```

### Domain weights (baseline)

- **Preclinical Efficacy (Lifespan):** 30%
- **Preclinical Efficacy (Healthspan):** 10%
- **Mechanism Conservation:** 10%
- **Human Trial Evidence:** 20%
- **Safety & Tolerability:** 20%
- **Cost & Accessibility:** 10%

### Stakeholder Perspectives

The framework computes rankings for four stakeholder perspectives:

**Regulator-Focused** (prioritizes clinical evidence and safety):
- Lifespan: 10%, Healthspan: 10%, Conservation: 0%
- Human Trials: 30%, Safety: 40%, Cost/Access: 10%

**Investor-Focused** (prioritizes efficacy outcomes):
- Lifespan: 40%, Healthspan: 20%, Conservation: 10%
- Human Trials: 10%, Safety: 10%, Cost/Access: 10%

**Patient-Focused** (balanced across quality of life, safety, and access):
- Lifespan: 15%, Healthspan: 15%, Conservation: 0%
- Human Trials: 25%, Safety: 30%, Cost/Access: 15%

## Uncertainty Quantification

Monte Carlo simulations sample domain scores from uniform distributions (±0.5 around assigned values) to generate 95% credible intervals. Sensitivity analysis tests ranking stability under ±5% weight perturbations.

## Interactive Tool Features

- Adjustable domain weights with real-time recalculation
- Stakeholder perspective presets (regulator, investor, patient)
- Hyperlinked evidence justifications for each score
- Comparative visualization across interventions

## Output Files

### Analysis Outputs

**1. Intervention_list_&_scores.xlsx** (21 columns)
- Original domain scores (6 columns)
- Total score and baseline weighted score
- Stakeholder scores (Regulator, Investor, Patient)
- Rankings (4 perspectives: Baseline, Regulator, Investor, Patient)
- Derived metrics (Translational_Readiness, Aging_Impact)
- Category assignment (Pharmacological, Cellular & Regenerative, etc.)

**2. weighted_score_intervals.csv**
```
Intervention | WeightedScore_Mean | WeightedScore_P2_5 | WeightedScore_P97_5
```
Mean weighted score and 95% confidence bounds across MC simulations.

**3. ranking_robustness_weights_±5%.csv**
```
Intervention | BaseWeightedScore | MeanRank | Rank_P2_5 | Rank_P97_5 | P_Top1 | P_Top3
```
Ranking stability under weight perturbations.

## Data Sources

All scores are derived from peer-reviewed literature, clinical trial databases, and regulatory documents. Complete evidence mapping with DOI links is provided in `data/evidence_map.xlsx`.

### Input Data Format

The primary input file (`Intervention_scores.xlsx`) requires:

**Sheet name**: "Scoring"

**Required columns**:
- `Intervention` (text): Name of intervention
- `Lifespan (30%)` (1-5): Preclinical lifespan data
- `Healthspan (10%)` (1-5): Preclinical healthspan/biomarkers
- `Conservation (10%)` (1-5): Mechanism conservation across species
- `Human Trials (20%)` (1-5): Clinical trial evidence
- `Safety & Tolerability (20%)` (1-5): Safety profile
- `Cost/Access (10%)` (1-5): Economic feasibility

All scores must be numeric values from 1 (lowest) to 5 (highest).

## Reproducibility

All analyses use fixed random seeds to ensure reproducibility:
- Score jitter: seed = 42
- Weight jitter: seed = 123

To reproduce published results exactly:

```bash
python analysis/mc_ranking_analysis.py \
    --seed_scores 42 \
    --seed_weights 123 \
    -r 10000 \
    -i data/Intervention_scores.xlsx \
    -o output/
```

### Reproducibility Checklist

- [ ] Fixed random seeds (42, 123)
- [ ] Document Python version: `python --version`
- [ ] Document package versions: `pip freeze > requirements_frozen.txt`
- [ ] Archive input data: `md5sum data/Intervention_scores.xlsx`
- [ ] ≥10,000 MC iterations for publication-quality results

## License

- **Code:** AGPL-3.0-or-later
- **Documentation:** CC BY 4.0
- **Data:** CC BY 4.0

## Citation

If you use this framework, analysis pipeline, or the interactive web tool, please cite:

```bibtex
@software{geroscience_mcda_2025,
  title = {Translational Geroscience MCDA: An evidence-weighted decision framework and interactive tool},
  author = {{P-BioMedLab}},
  year = {2025},
  version = {1.0.1},
  doi = {10.5281/zenodo.18075835},
  url = {https://github.com/P-BioMedLab/translational-geroscience-mcda}
}
```

## Contact

For questions regarding the framework or implementation, please open an issue in this repository.

## Disclaimer

This framework provides a structured approach to comparing geroscience interventions based on current evidence. Rankings reflect translational readiness rather than absolute scientific merit or long-term promise. Users should interpret results in conjunction with domain expertise and emerging evidence.

---

**Repository**: https://github.com/P-BioMedLab/translational-geroscience-mcda  
**Interactive Tool**: https://htmlpreview.github.io/?https://github.com/P-BioMedLab/translational-geroscience-mcda/blob/main/interactive_tool/Interactive%20Geroscience%20Interventions%20Ranking.html 
**DOI**: 10.5281/zenodo.18075835  
**License**: AGPL-3.0 (code), CC BY 4.0 (documentation & data)
