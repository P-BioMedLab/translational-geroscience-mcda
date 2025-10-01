#!/usr/bin/env python3
"""
Monte Carlo sensitivity bands for weighted domain scores + weight-robustness check.

- Score jitter: uniform ±noise around each domain score (clipped to [1, 5]).
- Weight robustness: multiply each weight by U(1 - wpert, 1 + wpert), renormalize, repeat.

Inputs
------
Excel file Book 1

Outputs
-------
- weighted_score_intervals.csv
- ranking_robustness_weights_p5.csv
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path
import numpy as np
import pandas as pd


WEIGHT_RX = re.compile(r"\((\d+(?:\.\d+)?)\s*%\)") 


def parse_weights_and_scores(df: pd.DataFrame) -> tuple[list[str], np.ndarray, np.ndarray, list[str]]:
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


def mc_score_intervals(scores: np.ndarray, weights: np.ndarray, r: int, noise: float, seed: int):
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
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=Path, default=Path("Book1.xlsx"))
    ap.add_argument("-s", "--sheet", default="Scoring")
    ap.add_argument("-r", "--replicates", type=int, default=10_000)
    ap.add_argument("--noise", type=float, default=0.5)   # domain score jitter
    ap.add_argument("--wpert", type=float, default=0.05)  # ±5% weight perturbation
    ap.add_argument("--seed_scores", type=int, default=42)
    ap.add_argument("--seed_weights", type=int, default=123)
    ap.add_argument("-o", "--outdir", type=Path, default=Path("."))
    args = ap.parse_args()

    df = pd.read_excel(args.input, sheet_name=args.sheet)
    domain_cols, weights, scores, items = parse_weights_and_scores(df)

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
    (args.outdir / "weighted_score_intervals.csv").write_text(
        score_ci.to_csv(index=False), encoding="utf-8"
    )  # ASCII filename

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
    (args.outdir / "ranking_robustness_weights_p5.csv").write_text(
        rank_robust.to_csv(index=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
