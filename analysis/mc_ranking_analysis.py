#!/usr/bin/env python3
"""
Enhanced Monte Carlo sensitivity analysis with integrated data preparation.

This script combines data preprocessing and Monte Carlo analysis:
1. Reads raw intervention scores from Excel
2. Computes stakeholder-specific weighted scores
3. Derives translational readiness and aging impact metrics
4. Assigns intervention categories
5. Computes rankings for all perspectives
6. Performs Monte Carlo sensitivity analysis
7. Outputs enriched dataset + robustness CSVs

Inputs
------
- Intervention_scores.xlsx (sheet: "Scoring")
  Required columns: Intervention, Lifespan (30%), Healthspan (10%), 
  Conservation (10%), Human Trials (20%), Safety & Tolerability (20%), 
  Cost/Access (10%)

Outputs
-------
- Intervention_list_&_scores.xlsx (enriched dataset with 19 columns)
- weighted_score_intervals.csv (score uncertainty)
- ranking_robustness_weights_p5.csv (rank stability)
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path
import numpy as np
import pandas as pd


WEIGHT_RX = re.compile(r"\((\d+(?:\.\d+)?)\s*%\)")


def categorize_intervention(name: str) -> str:
    """Assign intervention category based on mechanism type"""
    pharmacological = [
        'Rapamycin', 'Metformin', 'Acarbose', 'GLP-1 agonists',
        'SGLT2 inhibitors', 'Alpha-ketoglutarate', 'Senolytics (D+Q)',
        'Fisetin', 'NAD+ Restoration (NMN/NR)', 'Mitochondria (Urolithin A)',
        'Elamipretide', 'Spermidine', 'Chloroquine', 'Glutathione Precursors',
        'L-deprenyl', '17α-estradiol'
    ]
    
    genetic = [
        'Epigenetic reprogramming', 'Gene therapy',
        'Proteostasis & Nucleolus', 'Telomere extension'
    ]
    
    cellular = [
        'Stem cell therapy', 'Exosome therapy', 'Chemical reprogramming',
        'Synthetic organs', 'Immunotherapy senolytics', 'Xenotransplantation'
    ]
    
    systemic = [
        'Gut Microbiome Modulation', 'Anti-inflammatory',
        'Plasma dilution/apheresis', 'Young blood plasma'
    ]
    
    if name in pharmacological:
        return 'Pharmacological'
    elif name in genetic:
        return 'Genetic & Epigenetic'
    elif name in cellular:
        return 'Cellular & Regenerative'
    elif name in systemic:
        return 'Systemic & Other'
    else:
        return 'Other'


def compute_stakeholder_scores(scores: np.ndarray) -> dict[str, np.ndarray]:
    """
    Compute weighted scores for different stakeholder perspectives.
    
    Based on Excel formulas:
    - Regulator: Prioritizes clinical evidence and safety
    - Investor: Prioritizes efficacy outcomes
    - Patient: Balanced across quality of life, safety, and access
    
    Parameters
    ----------
    scores : np.ndarray, shape (n_items, 6)
        Domain scores [Lifespan, Healthspan, Conservation, 
                       HumanTrials, Safety, CostAccess]
    
    Returns
    -------
    dict with keys 'Regulator', 'Investor', 'Patient'
        Each value is np.ndarray of shape (n_items,)
    """
    # Stakeholder weight profiles from Excel formulas
    weights = {
        'Regulator': np.array([0.10, 0.10, 0.00, 0.30, 0.40, 0.10]),
        'Investor': np.array([0.40, 0.20, 0.10, 0.10, 0.10, 0.10]),
        'Patient': np.array([0.15, 0.15, 0.00, 0.25, 0.30, 0.15])
    }
    
    return {
        name: (scores * w).sum(axis=1)
        for name, w in weights.items()
    }


def compute_derived_metrics(scores: np.ndarray) -> dict[str, np.ndarray]:
    """
    Compute translational readiness and aging impact metrics.
    
    Based on Excel formulas:
    - Translational_Readiness: ROUND(AVERAGE(HumanTrials, Safety), 0)
    - Aging_Impact: (Lifespan × 3 + Healthspan + Conservation) / 5
    
    Parameters
    ----------
    scores : np.ndarray, shape (n_items, 6)
        Domain scores [Lifespan, Healthspan, Conservation,
                       HumanTrials, Safety, CostAccess]
    
    Returns
    -------
    dict with keys 'Translational_Readiness', 'Aging_Impact'
    """
    # Translational Readiness: average of Human Trials and Safety (rounded)
    trans_readiness = np.round((scores[:, 3] + scores[:, 4]) / 2, 0)
    
    # Aging Impact: weighted average with Lifespan having 3× weight
    # Excel formula: =(B2*3+C2+D2)/5
    # Lifespan weight: 3, Healthspan weight: 1, Conservation weight: 1
    aging_impact = (scores[:, 0] * 3 + scores[:, 1] + scores[:, 2]) / 5
    
    return {
        'Translational_Readiness': trans_readiness,
        'Aging_Impact': aging_impact
    }


def parse_weights_and_scores(df: pd.DataFrame) -> tuple[list[str], np.ndarray, np.ndarray, list[str]]:
    """Parse domain columns, weights, and scores from DataFrame"""
    if "Intervention" not in df.columns:
        raise ValueError('Required column "Intervention" not found.')

    domain_cols, weights = [], []
    for col in df.columns:
        if isinstance(col, str):
            m = WEIGHT_RX.search(col)
            if m:
                domain_cols.append(col)
                weights.append(float(m.group(1)) / 100.0)

    if not domain_cols:
        raise ValueError("No domain columns found. Expect headers like 'Something (20%)'.")

    # Coerce domain columns to numeric and validate
    score_df = df[domain_cols].apply(pd.to_numeric, errors="coerce")
    if score_df.isna().any().any():
        bad = score_df.columns[score_df.isna().any()].tolist()
        raise ValueError(f"Non-numeric values detected in domain columns: {bad}")

    weights = np.asarray(weights, dtype=float)
    if weights.ndim != 1 or weights.size != len(domain_cols):
        raise ValueError("Weights/columns mismatch.")

    if weights.sum() <= 0:
        raise ValueError("Parsed weights sum to zero; check header percents.")
    weights = weights / weights.sum()

    scores = score_df.to_numpy(dtype=float)  # (n_items, n_domains)
    items = df["Intervention"].astype(str).tolist()
    return domain_cols, weights, scores, items


def prepare_enriched_dataset(df: pd.DataFrame, domain_cols: list[str], 
                            weights: np.ndarray, scores: np.ndarray) -> pd.DataFrame:
    """
    Enrich dataset with computed metrics and stakeholder perspectives.
    
    Adds columns:
    - Regulator-Focused, Investor-Focused, Patient-Focused
    - Baseline rank, Regulator rank, Investor rank, Patient rank
    - Translational_Readiness, Aging_Impact
    - Category
    """
    df_enriched = df.copy()
    
    # Compute baseline weighted score (already in input file)
    # But we'll recalculate to ensure consistency
    baseline_score = (scores * weights).sum(axis=1)
    
    # Compute stakeholder scores
    stakeholder_scores = compute_stakeholder_scores(scores)
    df_enriched['Regulator-Focused'] = stakeholder_scores['Regulator']
    df_enriched['Investor-Focused'] = stakeholder_scores['Investor']
    df_enriched['Patient-Focused'] = stakeholder_scores['Patient']
    
    # Compute rankings (1 = best)
    df_enriched['Baseline rank'] = pd.Series(baseline_score).rank(
        ascending=False, method='min').astype(int)
    df_enriched['Regulator rank'] = pd.Series(stakeholder_scores['Regulator']).rank(
        ascending=False, method='min').astype(int)
    df_enriched['Investor rank'] = pd.Series(stakeholder_scores['Investor']).rank(
        ascending=False, method='min').astype(int)
    df_enriched['Patient rank'] = pd.Series(stakeholder_scores['Patient']).rank(
        ascending=False, method='min').astype(int)
    
    # Compute derived metrics
    derived = compute_derived_metrics(scores)
    df_enriched['Translational_Readiness'] = derived['Translational_Readiness']
    df_enriched['Aging_Impact'] = derived['Aging_Impact']
    
    # Assign categories
    df_enriched['Category'] = df_enriched['Intervention'].apply(categorize_intervention)
    
    return df_enriched


def mc_score_intervals(scores: np.ndarray, weights: np.ndarray, r: int, noise: float, seed: int):
    """Monte Carlo analysis for score uncertainty"""
    rng = np.random.default_rng(seed)
    n_items, n_domains = scores.shape
    # shape: (r, n_items, n_domains)
    noise_cube = rng.uniform(-noise, noise, size=(r, n_items, n_domains))
    sampled = np.clip(scores[None, :, :] + noise_cube, 1.0, 5.0)
    ws = (sampled * weights.reshape(1, 1, -1)).sum(axis=2)
    mean = ws.mean(axis=0)
    lo = np.percentile(ws, 2.5, axis=0)
    hi = np.percentile(ws, 97.5, axis=0)
    return mean, lo, hi


def robustness_weights(scores: np.ndarray, weights: np.ndarray, r: int, wpert: float, seed: int):
    """Monte Carlo analysis for weight sensitivity"""
    rng = np.random.default_rng(seed)
    n_items, n_domains = scores.shape
    pert = rng.uniform(1 - wpert, 1 + wpert, size=(r, n_domains)) * weights.reshape(1, -1)
    pert /= pert.sum(axis=1, keepdims=True)
    ws = pert @ scores.T  # (r, n_items)
    order = ws.argsort(axis=1)[:, ::-1]  # descending scores
    ranks = np.empty_like(order)
    for i in range(r):
        perm = order[i]
        inv = np.empty_like(perm)
        inv[perm] = np.arange(1, n_items + 1)  # 1 = best
        ranks[i] = inv
    return {
        "base_score": (scores * weights).sum(axis=1),
        "rank_mean": ranks.mean(axis=0),
        "rank_lo": np.percentile(ranks, 2.5, axis=0),
        "rank_hi": np.percentile(ranks, 97.5, axis=0),
        "p_top1": (ranks == 1).mean(axis=0),
        "p_top3": (ranks <= 3).mean(axis=0),
    }


def main():
    ap = argparse.ArgumentParser(
        description='Enhanced MC analysis with integrated data preparation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Standard run (10,000 iterations)
    python mc_ranking_analysis_enhanced.py
    
    # Custom input and output
    python mc_ranking_analysis_enhanced.py -i data/scores.xlsx -o results/
    
    # Quick test (1,000 iterations)
    python mc_ranking_analysis_enhanced.py -r 1000 -o test_output/
    
    # High-precision run (50,000 iterations)
    python mc_ranking_analysis_enhanced.py -r 50000
        """
    )
    ap.add_argument("-i", "--input", type=Path, default=Path("Intervention_scores.xlsx"),
                   help="Input Excel file (default: Intervention_scores.xlsx)")
    ap.add_argument("-s", "--sheet", default="Scoring",
                   help="Sheet name in input file (default: Scoring)")
    ap.add_argument("-r", "--replicates", type=int, default=10_000,
                   help="Monte Carlo iterations (default: 10,000)")
    ap.add_argument("--noise", type=float, default=0.5,
                   help="Domain score jitter ±value (default: 0.5)")
    ap.add_argument("--wpert", type=float, default=0.05,
                   help="Weight perturbation ±value (default: 0.05 = ±5%%)")
    ap.add_argument("--seed_scores", type=int, default=42,
                   help="Random seed for score jitter (default: 42)")
    ap.add_argument("--seed_weights", type=int, default=123,
                   help="Random seed for weight perturbation (default: 123)")
    ap.add_argument("-o", "--outdir", type=Path, default=Path("."),
                   help="Output directory (default: current directory)")
    args = ap.parse_args()

    print("\n" + "=" * 70)
    print("ENHANCED MC ANALYSIS WITH DATA PREPARATION")
    print("=" * 70)
    print(f"\nInput file:      {args.input}")
    print(f"Sheet name:      {args.sheet}")
    print(f"MC iterations:   {args.replicates:,}")
    print(f"Score noise:     ±{args.noise}")
    print(f"Weight perturb:  ±{args.wpert * 100}%")
    print(f"Output dir:      {args.outdir}")
    
    # Create output directory
    args.outdir.mkdir(parents=True, exist_ok=True)

    # STEP 1: Load and parse input data
    print("\n" + "=" * 70)
    print("STEP 1: Loading and parsing input data")
    print("=" * 70)
    
    df = pd.read_excel(args.input, sheet_name=args.sheet)
    print(f"✓ Loaded {len(df)} interventions from {args.input}")
    
    domain_cols, weights, scores, items = parse_weights_and_scores(df)
    print(f"✓ Parsed {len(domain_cols)} domain columns with weights")
    print(f"  Domains: {', '.join([col.split('(')[0].strip() for col in domain_cols])}")
    print(f"  Weights: {', '.join([f'{w*100:.0f}%' for w in weights])}")

    # STEP 2: Enrich dataset with computed metrics
    print("\n" + "=" * 70)
    print("STEP 2: Computing derived metrics and stakeholder scores")
    print("=" * 70)
    
    df_enriched = prepare_enriched_dataset(df, domain_cols, weights, scores)
    
    # Display computed columns
    new_cols = ['Regulator-Focused', 'Investor-Focused', 'Patient-Focused',
                'Baseline rank', 'Regulator rank', 'Investor rank', 'Patient rank',
                'Translational_Readiness', 'Aging_Impact', 'Category']
    print(f"✓ Added {len(new_cols)} computed columns:")
    for col in new_cols:
        print(f"  - {col}")
    
    # Show category distribution
    category_counts = df_enriched['Category'].value_counts()
    print(f"\n✓ Intervention categories:")
    for cat, count in category_counts.items():
        print(f"  - {cat}: {count}")
    
    # Save enriched dataset
    enriched_path = args.outdir / 'Intervention_list_&_scores.xlsx'
    df_enriched.to_excel(enriched_path, sheet_name='Sheet1', index=False)
    print(f"\n✓ Saved enriched dataset: {enriched_path}")
    print(f"  {len(df_enriched)} rows × {len(df_enriched.columns)} columns")

    # STEP 3: Monte Carlo score intervals
    print("\n" + "=" * 70)
    print("STEP 3: Monte Carlo analysis - Score uncertainty")
    print("=" * 70)
    print(f"Running {args.replicates:,} iterations with ±{args.noise} noise...")
    
    mean, lo, hi = mc_score_intervals(scores, weights, args.replicates, args.noise, args.seed_scores)
    score_ci = (
        pd.DataFrame({
            "Intervention": items,
            "WeightedScore_Mean": mean,
            "WeightedScore_P2_5": lo,
            "WeightedScore_P97_5": hi,
        })
        .sort_values("WeightedScore_Mean", ascending=False)
        .reset_index(drop=True)
    )
    
    intervals_path = args.outdir / "weighted_score_intervals.csv"
    intervals_path.write_text(score_ci.to_csv(index=False), encoding="utf-8")
    print(f"✓ Saved score intervals: {intervals_path}")
    
    # Show top 5
    print(f"\nTop 5 interventions (mean weighted score):")
    for i, row in score_ci.head(5).iterrows():
        print(f"  {i+1}. {row['Intervention']}: "
              f"{row['WeightedScore_Mean']:.2f} "
              f"[{row['WeightedScore_P2_5']:.2f}, {row['WeightedScore_P97_5']:.2f}]")

    # STEP 4: Weight robustness analysis
    print("\n" + "=" * 70)
    print("STEP 4: Monte Carlo analysis - Weight robustness")
    print("=" * 70)
    print(f"Running {args.replicates:,} iterations with ±{args.wpert*100}% weight perturbation...")
    
    rb = robustness_weights(scores, weights, args.replicates, args.wpert, args.seed_weights)
    rank_robust = (
        pd.DataFrame({
            "Intervention": items,
            "BaseWeightedScore": rb["base_score"],
            "MeanRank_Weights_p5": rb["rank_mean"],
            "Rank_P2_5": rb["rank_lo"],
            "Rank_P97_5": rb["rank_hi"],
            "P_Top1": rb["p_top1"],
            "P_Top3": rb["p_top3"],
        })
        .sort_values(["MeanRank_Weights_p5", "BaseWeightedScore"], ascending=[True, False])
        .reset_index(drop=True)
    )
    
    robustness_path = args.outdir / "ranking_robustness_weights_p5.csv"
    robustness_path.write_text(rank_robust.to_csv(index=False), encoding="utf-8")
    print(f"✓ Saved ranking robustness: {robustness_path}")
    
    # Show top 5 most stable rankings
    print(f"\nTop 5 most stable rankings:")
    for i, row in rank_robust.head(5).iterrows():
        print(f"  {i+1}. {row['Intervention']}: "
              f"rank {row['MeanRank_Weights_p5']:.1f} "
              f"[{row['Rank_P2_5']:.0f}, {row['Rank_P97_5']:.0f}], "
              f"P(top-1)={row['P_Top1']:.1%}, P(top-3)={row['P_Top3']:.1%}")

    # Summary
    print("\n" + "=" * 70)
    print("✓ ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nGenerated files in {args.outdir}:")
    print(f"  1. Intervention_list_&_scores.xlsx")
    print(f"  2. weighted_score_intervals.csv")
    print(f"  3. ranking_robustness_weights_p5.csv")
    print(f"\nReady for figure generation!")
    print()


if __name__ == "__main__":
    main()
