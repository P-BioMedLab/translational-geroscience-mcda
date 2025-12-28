import os
import subprocess
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd, cwd=REPO_ROOT):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    assert p.returncode == 0, f"Command failed:\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
    return p.stdout


def test_pipeline_smoke(tmp_path):
    out_dir = REPO_ROOT / "test_output"
    if out_dir.exists():
        # Keep it simple: clean prior runs
        for root, dirs, files in os.walk(out_dir, topdown=False):
            for f in files:
                Path(root, f).unlink()
            for d in dirs:
                Path(root, d).rmdir()
        out_dir.rmdir()

    # Run pipeline quickly
    run(["python", "run_pipeline.py", "-i", "analysis/Intervention_scores.xlsx", "--mc-runs", "200", "-o", "test_output"])

    # Assert key outputs exist (per README contract)
    expected = [
        out_dir / "Intervention_list_&_scores.xlsx",
        out_dir / "weighted_score_intervals.csv",
        out_dir / "ranking_robustness_weights_p5.csv",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    assert not missing, f"Missing expected outputs: {missing}"

    # Basic sanity checks on intervals CSV
    df = pd.read_csv(out_dir / "weighted_score_intervals.csv")
    # Check for actual column names produced by the pipeline
    for col in ["WeightedScore_Mean", "WeightedScore_P2_5", "WeightedScore_P97_5"]:
        assert col in df.columns, f"Expected column '{col}' not found in weighted_score_intervals.csv"

    assert (df["WeightedScore_P2_5"] <= df["WeightedScore_Mean"]).all()
    assert (df["WeightedScore_Mean"] <= df["WeightedScore_P97_5"]).all()
