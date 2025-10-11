# Geroscience Interventions Ranking Framework

## Overview

This repository contains the computational framework, scoring matrices, and interactive tools supporting the multi-criteria decision analysis (MCDA) of 30 geroscience interventions. The framework evaluates translational readiness across seven domains: preclinical efficacy (lifespan and healthspan), mechanism conservation, human trial evidence, safety and tolerability, biomarker availability, and cost-accessibility.

## Key Features

- Quantitative ranking of 30 interventions from repurposed drugs (metformin, rapamycin, acarbose) to frontier modalities (senolytics, epigenetic reprogramming, CAR-T therapies)
- Weighted scoring system prioritizing human safety and clinical evidence while preserving preclinical impact
- Monte Carlo uncertainty analysis with 95% credible intervals and sensitivity testing across stakeholder perspectives (regulators, investors, patients)
- Interactive web calculator allowing custom weighting schemes and real-time ranking updates

## Repository Structure

```
data/
    scoring_matrix.csv              - Raw domain scores for all interventions
    weighting_schemes.csv           - Domain weights for different stakeholders
    evidence_map.csv                - Links between scores and primary sources

analysis/
    mcda_framework.html             - Framework documentation and methodology
    mc_ranking_analysis.py          - Uncertainty quantification (n=10,000)
    sensitivity_analysis.py         - Weight perturbation testing
    visualization.html              - Rank stability analysis and domain-wise contribution profiles

interactive_tool/
    app.py                          - Web application backend
    Interactive Geroscience Interventions Ranking - HTML template

output/
    mcda_scoring-ranking.xlsx                       - Final ranked interventions
    ranking_robustness_weights_±5pct.xlsx           - Sensitivity analysis results
    sensitivity_analysis.xlsx                       - Weight perturbation testing
    supplementary_table_weighted_scores.xlsx        - Scoring breakdown
requirements.txt                    - Python dependencies for analysis scripts
```

### Install dependencies

```bash
pip install -r requirements.txt
```

For the interactive web tool:

```bash
cd interactive_tool
pip install -r requirements.txt
```

## Requirements

- Python 3.9 or higher
- NumPy 1.24+
- Pandas 2.0+
- Matplotlib 3.7+
- SciPy 1.10+
- Streamlit 1.28+ (for interactive tool)

All dependencies are specified in `requirements.txt` for installation.

## Usage

### Run Monte Carlo uncertainty analysis

```bash
python analysis/mc_ranking_analysis.py --iterations 10000 --seed 42
```

### Perform sensitivity analysis

```bash
python analysis/mc_ranking_analysis.py --perturbation 0.05
```

### Launch interactive web tool

** [Access Live Demo](https://htmlpreview.github.io/?https://github.com/P-BioMedLab/translational-geroscience-mcda/blob/main/interactive_tool/Interactive%20Geroscience%20Interventions%20Ranking.html)**

Or access the deployed version at: https://translational-geroscience-mcda-ranking.streamlit.app/

## Scoring Methodology

Each intervention receives scores from 1-5 across seven domains according to predefined rubrics. Final weighted scores are calculated as:

```
Weighted Score = Σ(Domain_Score_i × Weight_i)
```

### Domain weights (baseline)

- **Preclinical Efficacy (Lifespan):** 20%
- **Preclinical Efficacy (Healthspan):** 10%
- **Mechanism Conservation:** 10%
- **Human Trial Evidence:** 20%
- **Safety & Tolerability:** 20%
- **Biomarker Availability:** 10%
- **Cost & Accessibility:** 10%

## Uncertainty Quantification

Monte Carlo simulations sample domain scores from uniform distributions (±0.5 around assigned values) to generate 95% credible intervals. Sensitivity analysis tests ranking stability under ±5% weight perturbations.

## Interactive Tool Features

- Adjustable domain weights with real-time recalculation
- Stakeholder perspective presets (regulator, investor, patient)
- Hyperlinked evidence justifications for each score
- Comparative visualization across interventions

## Data Sources

All scores are derived from peer-reviewed literature, clinical trial databases, and regulatory documents. Complete evidence mapping with DOI links is provided in `data/evidence_map.csv`.

## Reproducibility

All analyses use fixed random seeds. To reproduce published results exactly:

```bash
python analysis/mc_ranking_analysis.py --seed 42 --iterations 10000
```

## License

- **Code:** AGPL-3.0-or-later
- **Documentation:** CC BY 4.0
- **Data:** CC BY 4.0

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{geroscience_mcda_2025,
  title = {Geroscience Interventions Ranking Framework},
  author = {{P-BioMedLab}},
  year = {2025},
  url = {https://github.com/P-BioMedLab/translational-geroscience-mcda}
}
```
## Contact

For questions regarding the framework or implementation, please open an issue in this repository.

## Disclaimer

This framework provides a structured approach to comparing geroscience interventions based on current evidence. Rankings reflect translational readiness rather than absolute scientific merit or long-term promise. Users should interpret results in conjunction with domain expertise and emerging evidence.
