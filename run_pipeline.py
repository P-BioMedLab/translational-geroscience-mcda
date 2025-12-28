#!/usr/bin/env python3
"""
Simplified pipeline to generate all figures from raw input data.

This script orchestrates a 2-step workflow:
1. Run MC analysis (includes data preparation)
2. Generate all publication figures

Usage:
    python run_pipeline.py --input Intervention_scores.xlsx
    
    # Or with custom parameters:
    python run_pipeline.py -i data/Intervention_scores.xlsx \
                           -o output/ \
                           --mc-runs 10000
"""

import subprocess
import sys
from pathlib import Path
import argparse
import shutil


def run_command(cmd, description):
    """Run a command and handle errors"""
    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)
    print(f"Running: {' '.join(str(x) for x in cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ ERROR: {description} failed with exit code {result.returncode}")
        sys.exit(1)
    
    print(f"\n✓ {description} completed successfully")
    return result


def verify_file(filepath, description):
    """Verify that a file exists"""
    if not filepath.exists():
        print(f"\n❌ ERROR: Required file not found: {filepath}")
        print(f"   Description: {description}")
        sys.exit(1)
    print(f"✓ Found: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='Simplified reproducible pipeline for geroscience MCDA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with defaults (10,000 MC iterations)
    python run_pipeline.py
    
    # Custom output directory
    python run_pipeline.py -o results/
    
    # Quick test with fewer iterations
    python run_pipeline.py --mc-runs 1000 -o test_output/
    
    # Full publication run
    python run_pipeline.py --mc-runs 50000 -o publication_figures/
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=Path,
        default=Path('Intervention_scores.xlsx'),
        help='Input Excel file with intervention scores (default: Intervention_scores.xlsx)'
    )
    parser.add_argument(
        '-s', '--sheet',
        default='Scoring',
        help='Sheet name in input file (default: Scoring)'
    )
    parser.add_argument(
        '-o', '--outdir',
        type=Path,
        default=Path('output'),
        help='Output directory for all results (default: output/)'
    )
    parser.add_argument(
        '--mc-runs',
        type=int,
        default=10000,
        help='Number of Monte Carlo iterations (default: 10000)'
    )
    parser.add_argument(
        '--mc-noise',
        type=float,
        default=0.5,
        help='Score perturbation noise level (default: 0.5)'
    )
    parser.add_argument(
        '--mc-wpert',
        type=float,
        default=0.05,
        help='Weight perturbation level (default: 0.05 = ±5%%)'
    )
    parser.add_argument(
        '--skip-mc',
        action='store_true',
        help='Skip MC analysis (use existing outputs)'
    )
    parser.add_argument(
        '--figures-only',
        action='store_true',
        help='Only generate figures (skip analysis)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("GEROSCIENCE MCDA - SIMPLIFIED REPRODUCIBLE PIPELINE")
    print("=" * 70)
    print(f"\nInput file:          {args.input}")
    print(f"Sheet name:          {args.sheet}")
    print(f"Output directory:    {args.outdir}")
    print(f"MC iterations:       {args.mc_runs:,}")
    print(f"MC noise level:      ±{args.mc_noise}")
    print(f"Weight perturbation: ±{args.mc_wpert * 100}%")
    
    # Create output directory
    args.outdir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory created: {args.outdir}")
    
    # Verify input file exists
    print("\n" + "=" * 70)
    print("VERIFICATION: Checking required files")
    print("=" * 70)
    verify_file(args.input, "Input intervention scores")
    
    # Define expected output files
    intervention_list = args.outdir / 'Intervention_list_&_scores.xlsx'
    intervals_csv = args.outdir / 'weighted_score_intervals.csv'
    robustness_csv = args.outdir / 'ranking_robustness_weights_p5.csv'
    
    # STEP 1: MC Analysis (includes data preparation)
    if not args.figures_only and not args.skip_mc:
        run_command(
            [
                sys.executable, 'mc_ranking_analysis.py',
                '-i', str(args.input),
                '-s', args.sheet,
                '-r', str(args.mc_runs),
                '--noise', str(args.mc_noise),
                '--wpert', str(args.mc_wpert),
                '-o', str(args.outdir)
            ],
            "MC Analysis (data prep + Monte Carlo)"
        )
    else:
        print("\n⊙ Skipping MC analysis")
        verify_file(intervention_list, "Intervention list with scores")
        verify_file(intervals_csv, "Weighted score intervals")
        verify_file(robustness_csv, "Ranking robustness")
    
    # Verify all required files exist
    print("\n" + "=" * 70)
    print("VERIFICATION: Checking analysis outputs")
    print("=" * 70)
    verify_file(intervention_list, "Intervention list with scores")
    verify_file(intervals_csv, "Weighted score intervals")
    verify_file(robustness_csv, "Ranking robustness")
    
    # STEP 2: Generate figures
    print("\n" + "=" * 70)
    print("SETUP: Preparing files for figure generation")
    print("=" * 70)
    
    # Create a temporary directory with expected file locations
    fig_input_dir = args.outdir / 'figure_inputs'
    fig_input_dir.mkdir(exist_ok=True)
    
    # Copy files to expected names
    shutil.copy2(intervention_list, fig_input_dir / 'Intervention_list_&_scores.xlsx')
    shutil.copy2(intervals_csv, fig_input_dir / 'weighted_score_intervals.csv')
    shutil.copy2(robustness_csv, fig_input_dir / 'ranking_robustness_weights_p5.csv')
    
    print(f"✓ Prepared figure inputs in: {fig_input_dir}")
    
    # Create modified figure generation script that uses our output directory
    print("\n" + "=" * 70)
    print("GENERATING: Creating figures")
    print("=" * 70)
    
    # Read the original script
    with open('generate_figures_complete.py', 'r') as f:
        fig_script = f.read()
    
    # Modify paths to use our output directory
    fig_script_modified = fig_script.replace(
        "'/mnt/user-data/uploads/",
        f"'{fig_input_dir}/"
    )
    
    # Write modified script
    modified_script_path = args.outdir / 'generate_figures_temp.py'
    with open(modified_script_path, 'w') as f:
        f.write(fig_script_modified)
    
    # Run figure generation from output directory
    run_command(
        [sys.executable, str(modified_script_path)],
        "Figure Generation (all 8 figures + multipanel)"
    )
    
    # Move generated figures to output directory
    for pattern in ['Figure*.tiff', 'Figure*.eps', 'Figure*.pdf', 'Figure*.png']:
        for fig_file in Path('.').glob(pattern):
            dest = args.outdir / fig_file.name
            shutil.move(str(fig_file), str(dest))
            print(f"  → Moved {fig_file.name} to {args.outdir}/")
    
    # Clean up temporary files
    modified_script_path.unlink()
    
    # Final summary
    print("\n" + "=" * 70)
    print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    print(f"\nAll outputs saved to: {args.outdir}/")
    print("\nGenerated files:")
    print("\n1. Analysis outputs:")
    print(f"   - {intervention_list.name}")
    print(f"   - {intervals_csv.name}")
    print(f"   - {robustness_csv.name}")
    
    print("\n2. Individual figures (TIFF + EPS):")
    for i in range(1, 9):
        print(f"   - Figure{i}_*.tiff/.eps")
    
    print("\n3. Multipanel figure:")
    print("   - Figure9_Multipanel_a-h.pdf (vector format)")
    print("   - Figure9_Multipanel_a-h.tiff (300 DPI with caption)")
    print("   - Figure9_Multipanel_a-h_preview.png (preview)")
    
    print("\n" + "=" * 70)
    print("Ready for publication submission!")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
