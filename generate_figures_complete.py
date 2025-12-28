#!/usr/bin/env python3
"""
Complete script to generate all 8 figures
Generates both TIFF and EPS formats at 300 DPI
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')

# Constants for publication-quality figures
W_2COL_IN = 7.2  # 2-column width in inches (183 mm)

# Set publication-quality defaults
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans', 'Liberation Sans'],
    'font.size': 12,
    'axes.linewidth': 1,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

def save_figure(fig, filename):
    """Save figure in both TIFF and EPS formats"""
    # Save as TIFF (300 DPI) with LZW compression
    fig.savefig(f"{filename}.tiff", format='tiff', dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    # Save as EPS (vector format)
    fig.savefig(f"{filename}.eps", format='eps', dpi=300)
    print(f"Saved: {filename}.tiff and {filename}.eps")

def create_figure1():
    """Figure 1: Comparative Mortality Risk Factors"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    risk_factors = ['Age ≥65 vs. <65', 'Heavy Smoking', 'Obesity\n(BMI ≥30)', 
                   'Physical\nInactivity', 'Hypertension\n(per 20 mmHg)', 
                   'Air Pollution\n(PM2.5 +10 μg/m³)']
    risk_ratios = [13.8, 1.8, 1.45, 1.28, 1.28, 1.11]
    colors = ['purple', 'red', 'orange', 'green', 'blue', 'gray']
    
    bars = ax.bar(risk_factors, risk_ratios, color=colors, alpha=0.8, 
                  edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for bar, value in zip(bars, risk_ratios):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value}×', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax.set_ylabel('Relative Risk Ratio (×)', fontweight='bold')
    ax.set_xlabel('Risk Factors', fontweight='bold')
    ax.set_ylim(0, 15)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    save_figure(fig, "Figure1_Mortality_Risk_Factors")
    plt.close()

def create_figure2():
    """Figure 2: Age-Stratified Mortality Rates by Leading Cause of Death"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    causes = ['Heart\ndisease', 'Cancer', 'Stroke', 'COPD', "Alzheimer's", 'Diabetes', 'Kidney\ndisease']
    under_65 = [45.9, 55.1, 7.9, 7.2, 0.5, 9.7, 3.6]
    over_65 = [935.7, 778.7, 237.7, 212.0, 190.0, 115.7, 76.3]
    
    x = np.arange(len(causes))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, under_65, width, label='Age <65', 
                   color='#3498db', alpha=0.85, edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, over_65, width, label='Age ≥65', 
                   color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 20,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Death Rate (per 100,000 population)', fontweight='bold', fontsize=14)
    ax.set_xlabel('Cause of Death', fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(causes)
    ax.set_ylim(0, 1000)
    ax.legend(loc='upper right', frameon=True, fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    save_figure(fig, "Figure2_Age_Stratified_Mortality")
    plt.close()

def create_figure3():
    """Figure 3: US Mortality Rates by Age Group"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    age_groups = ['5-14', '15-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75-84', '85+']
    death_rates = [15, 77, 148, 237, 412, 899, 1809, 4345, 14286]
    
    # Color gradient from blue to red
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(age_groups)))
    
    bars = ax.bar(age_groups, death_rates, color=colors, edgecolor='black', linewidth=1)
    
    # Add value labels
    for bar, value in zip(bars, death_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 200,
                f'{value:,}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_ylabel('Death Rate per 100,000 Population', fontweight='bold')
    ax.set_xlabel('Age Group (years)', fontweight='bold')
    ax.set_ylim(0, 16000)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Format y-axis with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.tight_layout()
    save_figure(fig, "Figure3_US_Mortality_by_Age")
    plt.close()

def create_figure4(excel_data):
    """Figure 4: Translational Readiness vs Potential Impact - Exact Format Match"""
    
    # Extract data from Excel file
    df = excel_data.copy()
    
    # Define categories based on intervention characteristics
    def categorize_intervention(name):
        pharmacological = ['Rapamycin', 'Metformin', 'Acarbose', 'GLP-1 agonists', 
                          'SGLT2 inhibitors', 'Alpha-ketoglutarate', 'Senolytics (D+Q)',
                          'Fisetin', 'NAD+ Restoration (NMN/NR)', 'Mitochondria (Urolithin A)',
                          'Elamipretide', 'Spermidine', 'Chloroquine', 'Glutathione Precursors',
                          'L-deprenyl', '17α-estradiol']
        
        genetic = ['Epigenetic reprogramming', 'Gene therapy',
                  'Proteostasis & Nucleolus', 'Telomere extension']
        
        cellular = ['Stem cell therapy', 'Exosome therapy', 'Chemical reprogramming',
                   'Synthetic organs','Immunotherapy senolytics', 'Xenotransplantation']
        
        systemic = ['Gut Microbiome Modulation','Anti-inflammatory','Plasma dilution/apheresis', 'Young blood plasma']
        
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
    
    df['Category'] = df['Intervention'].apply(categorize_intervention)
    
    # Create figure with exact dimensions
    fig, ax = plt.subplots(figsize=(12, 9))
    
    category_colors = {
        'Pharmacological': '#1f77b4',
        'Cellular & Regenerative': '#2ca02c',
        'Genetic & Epigenetic': '#d62728',
        'Systemic & Other': '#ff7f0e'
    }
    
    # Plot points and collect text labels
    texts = []
    for _, row in df.iterrows():
        color = category_colors.get(row['Category'], 'gray')
        ax.plot(
            row['Translational_Readiness'],
            row['Aging_Impact'],
            marker='o',
            markersize=8,
            linestyle='',
            color=color,
        )
        # Add text label with initial position offset to the right
        t = ax.text(
            row['Translational_Readiness'] + 0.06,
            row['Aging_Impact'],
            row['Intervention'],
            fontsize=12,
            va='center',
            ha='left',
        )
        texts.append(t)
    
    # Set exact axis limits
    ax.set_xlim(1, 5.5)
    ax.set_ylim(2, 5)
    
    # Set exact tick positions
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(2, 6))
    
    # Add grid
    ax.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5, alpha=0.7)
    
    # Set title 
    ax.set_title('30 Aging Interventions: Readiness vs Potential (1–5)', 
                 fontsize=16, weight='bold', pad=15)
    
    # Set axis labels 
    ax.set_xlabel('Translational Readiness (1 = Low, 5 = High)', fontsize=14)
    ax.set_ylabel('Potential for Aging Impact (1 = Low, 5 = High)', fontsize=14)
    
    # Create legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', 
                         markerfacecolor=c, markersize=8, label=cat)
               for cat, c in category_colors.items()]
    # Position legend
    ax.legend(handles=handles, loc='upper right', bbox_to_anchor=(1.0, 0.94), 
              title='', frameon=True, fontsize=14)
    
    # Smart collision-avoidance with bounds checking
    fig.canvas.draw()
    ymin, ymax = 2, 5.5
    for iteration in range(400):
        moved = False
        renderer = fig.canvas.get_renderer()
        bboxes = [txt.get_window_extent(renderer).expanded(1.02, 1.05) for txt in texts]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                if bboxes[i].overlaps(bboxes[j]):
                    _, dy = ax.transData.inverted().transform((0, 2)) - ax.transData.inverted().transform((0, 0))
                    yi = texts[i].get_position()[1]
                    yj = texts[j].get_position()[1]
                    if yi <= yj:
                        new_yi, new_yj = yi - dy, yj + dy
                    else:
                        new_yi, new_yj = yi + dy, yj - dy
                    # Keep within bounds
                    new_yi = min(max(new_yi, ymin), ymax)
                    new_yj = min(max(new_yj, ymin), ymax)
                    texts[i].set_position((texts[i].get_position()[0], new_yi))
                    texts[j].set_position((texts[j].get_position()[0], new_yj))
                    moved = True
        if not moved:
            break
        fig.canvas.draw()

    # Force Chemical reprogramming and Exosome therapy to align with their bullets
    for txt in texts:
        intervention_name, original_y = text_to_intervention[txt]
        if intervention_name in ['Chemical reprogramming', 'Exosome therapy']:
            current_x = txt.get_position()[0]
            txt.set_position((current_x, original_y))

    plt.tight_layout()
    save_figure(fig, "Figure4_Readiness_vs_Impact")
    plt.close()

def create_figure5(intervals_data):
    """Figure 5: Rank Stability Analysis"""
    
    # Load data and get top 15 interventions
    df = intervals_data.copy()
    df = df.head(15)  # Top 15 interventions
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    interventions = df['Intervention'].values
    baseline_scores = df['WeightedScore_Mean'].values
    ci_lower = df['WeightedScore_P2_5'].values
    ci_upper = df['WeightedScore_P97_5'].values
    
    x_pos = range(len(interventions))
    ax.scatter(x_pos, baseline_scores, color='steelblue', s=100, zorder=3, 
              edgecolors='black', linewidth=1.5)
    ax.errorbar(x_pos, baseline_scores, 
                yerr=[baseline_scores - ci_lower, ci_upper - baseline_scores],
                fmt='none', color='steelblue', capsize=5, capthick=2, linewidth=2, zorder=2)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(interventions, rotation=45, ha='right')
    ax.set_ylabel('Weighted Score', fontweight='bold', fontsize=14)
    ax.set_xlabel('Geroscience Interventions (ranked by weighted score)', fontweight='bold', fontsize=14)
    ax.set_ylim(2.6, 4.0)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    save_figure(fig, "Figure5_Rank_Stability")
    plt.close()

def create_figure6(excel_data):
    """Figure 6: Domain-wise Contribution Profiles"""
    
    # Get top 15 interventions by weighted score
    df = excel_data.copy()
    df = df.sort_values('Weighted score', ascending=False).head(15)
    
    interventions = df['Intervention'].values
    
    # Extract domain contributions (normalized to weighted contributions)
    domains = {
        'Preclinical Lifespan (30%)': df['Lifespan (30%)'].values * 0.3,
        'Preclinical Healthspan (10%)': df['Healthspan (10%)'].values * 0.1,
        'Mechanism Conservation (10%)': df['Conservation (10%)'].values * 0.1,
        'Human Trial Evidence (20%)': df['Human Trials (20%)'].values * 0.2,
        'Safety & Tolerability (20%)': df['Safety & Tolerability (20%)'].values * 0.2,
        'Cost & Accessibility (10%)': df['Cost/Access (10%)'].values * 0.1
    }
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    bottom = np.zeros(len(interventions))
    colors = ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
    
    for i, (domain, values) in enumerate(domains.items()):
        ax.bar(interventions, values, bottom=bottom, label=domain, 
               color=colors[i], alpha=0.85, edgecolor='black', linewidth=0.5)
        bottom += values
    
    ax.set_ylabel('Weighted Score Contribution', fontweight='bold', fontsize=14)
    ax.set_xlabel('Geroscience Interventions (ranked by total weighted score)', 
                 fontweight='bold', fontsize=14)
    ax.set_ylim(0, 4.0)
    plt.xticks(rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    save_figure(fig, "Figure6_Domain_Contributions")
    plt.close()

def create_figure7(excel_data):
    """Figure 7: Stakeholder Sensitivity Analysis"""
    
    # Select interventions that show most variation across stakeholder perspectives
    df = excel_data.copy()
    
    # Calculate variation in ranks across stakeholder perspectives
    df['rank_variance'] = df[['Regulator rank', 'Investor rank', 'Patient rank']].var(axis=1)
    
    # Select top 12 interventions with highest variation
    df_selected = df.nlargest(12, 'rank_variance')
    
    # Sort by baseline rank for display
    df_selected = df_selected.sort_values('Baseline rank')
    
    interventions = df_selected['Intervention'].values
    
    stakeholder_data = {
        'Baseline': df_selected['Weighted score'].values,
        'Regulator-Focused': df_selected['Regulator-Focused'].values,
        'Investor-Focused': df_selected['Investor-Focused'].values,
        'Patient-Focused': df_selected['Patient-Focused'].values
    }
    
    x = np.arange(len(interventions))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    colors = ['steelblue', 'forestgreen', 'darkorange', 'crimson']
    
    for i, (stakeholder, scores) in enumerate(stakeholder_data.items()):
        bars = ax.bar(x + i*width, scores, width, label=stakeholder, 
                     color=colors[i], alpha=0.85, edgecolor='black', linewidth=0.5)
    
    ax.set_ylabel('Weighted Score', fontweight='bold', fontsize=14)
    ax.set_xlabel('Geroscience Interventions (ordered by stakeholder sensitivity)', 
                 fontweight='bold', fontsize=14)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(interventions, rotation=45, ha='right', fontsize=13)
    ax.set_ylim(1.5, 4.5)
    ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=13)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    save_figure(fig, "Figure7_Stakeholder_Sensitivity")
    plt.close()

def create_figure8():
    """Figure 8: MCDA Framework Flowchart"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Define colors for different box types
    colors = {
        'input': '#e1f5ff',
        'framework': '#fff4e1',
        'calculation': '#ffe1e1',
        'results': '#e1ffe1',
        'validation': '#f0e1ff',
        'output': '#ffe1f5'
    }
    
    def add_box(x, y, width, height, text, color, fontsize=10, bold=False):
        """Add a rounded rectangle box with text"""
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                            boxstyle="round,pad=0.05", 
                            edgecolor='black', facecolor=color, linewidth=1.5)
        ax.add_patch(box)
        weight = 'bold' if bold else 'normal'
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, 
               fontweight=weight, wrap=True)
    
    def add_arrow(x1, y1, x2, y2):
        """Add a straight arrow between boxes"""
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=15, 
                               linewidth=1.5, color='black')
        ax.add_patch(arrow)
    
    # Add title
    ax.text(5, 15.3, 'Multi-Criteria Decision Analysis Framework', 
           ha='center', fontsize=16, fontweight='bold', color='#2c3e50')
    ax.text(5, 15, 'Ranking Geroscience Interventions for Translational Potential',
           ha='center', fontsize=10, color='#7f8c8d')
    
    # Add legend
    legend_y = 14.5
    legend_items = [
        ('Input', colors['input'], 0.8),
        ('Framework', colors['framework'], 1.9),
        ('Calculation', colors['calculation'], 3.2),
        ('Results', colors['results'], 4.4),
        ('Validation', colors['validation'], 5.5),
        ('Output', colors['output'], 6.6)
    ]
    
    for label, color, x_pos in legend_items:
        # Small color box
        box = Rectangle((x_pos, legend_y - 0.1), 0.3, 0.2, 
                       facecolor=color, edgecolor='#ccc', linewidth=1)
        ax.add_patch(box)
        # Label text
        ax.text(x_pos + 0.4, legend_y, label, ha='left', va='center', fontsize=8)
    
    # Top: Input
    add_box(5, 13.3, 1.8, 0.6, '30 Geroscience\nInterventions', colors['input'], 9)
    
    # MCDA Framework
    add_box(5, 12.2, 2, 0.6, 'Multi-Criteria\nDecision Analysis', colors['framework'], 9)
    add_arrow(5, 13, 5, 12.5)
    
    # Six criteria boxes - all in one horizontal row
    criteria_y = 10.8
    criteria_x = [0.9, 2.3, 3.7, 5.1, 6.5, 7.9]
    criteria_labels = [
        'Preclinical Lifespan\n30% - Score: 1-5',
        'Human Trials\n20% - Score: 1-5',
        'Safety\n20% - Score: 1-5',
        'Preclinical Healthspan\n10% - Score: 1-5',
        'Mechanism\n10% - Score: 1-5',
        'Cost/Access\n10% - Score: 1-5'
    ]
    
    # Draw criteria boxes
    for i, x in enumerate(criteria_x):
        add_box(x, criteria_y, 1.3, 0.7, criteria_labels[i], colors['framework'], 7)
    
    # Straight arrows from MCDA to criteria
    mcda_bottom = 11.9
    criteria_top = criteria_y + 0.35
    
    for x in criteria_x:
        add_arrow(5, mcda_bottom, x, criteria_top)
    
    # Aggregation box
    add_box(5, 9.5, 1.8, 0.6, 'Weighted Sum\nAggregation', colors['calculation'], 9)
    
    # Straight arrows from criteria back to aggregation
    criteria_bottom = criteria_y - 0.35
    agg_top = 9.8
    
    for x in criteria_x:
        add_arrow(x, criteria_bottom, 5, agg_top)
    
    # Formula box
    add_box(5, 8.5, 2.2, 0.6, 'Weighted Score =\nΣ Score × Weight', colors['calculation'], 9)
    add_arrow(5, 9.2, 5, 8.8)
    
    # Baseline Rankings
    add_box(5, 7.5, 1.8, 0.6, 'Baseline\nRankings 1-30', colors['results'], 9)
    add_arrow(5, 8.2, 5, 7.8)
    
    # Robustness Testing
    add_box(5, 6.5, 1.8, 0.6, 'Robustness\nTesting', colors['validation'], 9)
    add_arrow(5, 7.2, 5, 6.8)
    
    # Two validation methods
    add_box(3, 5.3, 1.6, 0.8, 'Monte Carlo\n10,000 iterations\n95% CI', colors['validation'], 8)
    add_box(7, 5.3, 1.8, 0.8, 'Sensitivity Analysis\n3 Stakeholder\nWeighting Schemes', colors['validation'], 8)
    add_arrow(5, 6.2, 3, 5.7)
    add_arrow(5, 6.2, 7, 5.7)
    
    # Validated Rankings
    add_box(5, 4.2, 1.8, 0.6, 'Validated\nRankings', colors['results'], 9)
    add_arrow(3, 4.9, 5, 4.5)
    add_arrow(7, 4.9, 5, 4.5)
    
    # Final Output
    add_box(5, 3.2, 1.6, 0.6, 'Interactive\nWeb Tool', colors['output'], 9)
    add_arrow(5, 3.9, 5, 3.5)
    
    # Add methodology box at bottom
    methodology_y = 1.5
    methodology_height = 2
    methodology_box = FancyBboxPatch((0.5, methodology_y - methodology_height/2), 9, methodology_height,
                                    boxstyle="round,pad=0.1", 
                                    edgecolor='#95a5a6', facecolor='#ecf0f1', linewidth=1.5)
    ax.add_patch(methodology_box)
    
    # Methodology title
    ax.text(5, 2.2, 'Methodology Overview', ha='center', fontsize=11, fontweight='bold', color='#34495e')
    
    # Methodology bullets
    methodology_text = [
        '• Input: 30 candidate geroscience interventions (pharmacological, cellular, regenerative, and systemic)',
        '• Evaluation Domains: Six criteria scored 1-5, with higher weighting on Lifespan (30%), Human Trials (20%), and Safety (20%)',
        '• Aggregation: Weighted sum formula combines domain scores into final translational potential scores',
        '• Validation: Monte Carlo simulation (n=10,000) and multi-stakeholder sensitivity analysis ensure ranking robustness'
    ]
    
    for i, text in enumerate(methodology_text):
        ax.text(0.7, 1.85 - i * 0.35, text, ha='left', va='top', fontsize=7, color='#555')
    
    plt.tight_layout()
    save_figure(fig, "Figure8_MCDA_Framework")
    plt.close()

def create_multipanel_a_to_h(
    fig_stems=None,
    out_stem="Figure9_Multipanel_a-h",
    layout=(4, 2),  # rows, cols
):
    """
    Combine Figures 1–8 into a single multi-panel layout with panel letters (a–h).
    - Panel letters: 8 pt bold, top-left of each panel.
    - Output: PDF + TIFF (300 dpi) + PNG preview
    """
    import matplotlib.image as mpimg
    from pathlib import Path

    # Resolve working directory (same folder as this script)
    here = Path(__file__).resolve().parent

    # Default stems in intended order (a–h)
    if fig_stems is None:
        fig_stems = [
            "Figure1_Mortality_Risk_Factors",
            "Figure2_Age_Stratified_Mortality",
            "Figure3_US_Mortality_by_Age",
            "Figure4_Readiness_vs_Impact",
            "Figure5_Rank_Stability",
            "Figure6_Domain_Contributions",
            "Figure7_Stakeholder_Sensitivity",
            "Figure8_MCDA_Framework",
        ]

    # Load panel images (TIFF preferred)
    imgs = []
    missing = []
    for stem in fig_stems:
        p = here / f"{stem}.tiff"
        if not p.exists():
            # allow running from elsewhere (e.g., /mnt/data)
            alt = Path("/mnt/data") / f"{stem}.tiff"
            if alt.exists():
                p = alt
            else:
                missing.append(stem)
                continue
        imgs.append(mpimg.imread(str(p)))

    if missing:
        raise FileNotFoundError(
            "Missing required TIFFs for multipanel: " + ", ".join(missing) +
            ". Generate individual figures first."
        )

    rows, cols = layout
    assert rows * cols >= len(imgs), "Layout grid too small for number of panels."

    # Width: 2-column (183 mm). Height chosen to keep panels readable.
    fig_w = W_2COL_IN
    fig_h = 11.5  # inches; increased to accommodate caption

    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = fig.add_gridspec(rows, cols, left=0.02, right=0.98, top=0.90, bottom=0.12, wspace=0.04, hspace=0.08)

    letters = list("abcdefgh")
    for i, img in enumerate(imgs):
        r = i // cols
        c = i % cols
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(img)
        ax.set_axis_off()

        # Panel letter: 8 pt bold
        ax.text(
            0.01, 0.98, letters[i],
            transform=ax.transAxes,
            ha="left", va="top",
            fontsize=8, fontweight="bold",
            color="black"
        )

    # Add figure caption at bottom
    caption_text = (
        "Figure X | Evidence-weighted prioritization and robustness assessment for geroscience interventions. "
        "a, Comparative mortality risk contribution of chronological aging (≥65 vs <65) relative to major modifiable risk factors (relative risk ratios shown). "
        "b, Age-stratified mortality rates (deaths per 100,000) for leading causes of death for <65 versus ≥65. "
        "c, All-cause mortality rate by age group (deaths per 100,000), highlighting the non-linear increase in late life. "
        "d, Evidence map of 30 interventions positioned by translational readiness (x-axis) and potential aging impact (y-axis), both scored on a 1–5 scale; points are color-coded by intervention class. "
        "e, Rank stability under uncertainty analysis, shown as mean weighted score with 2.5th–97.5th percentile intervals for top-ranked interventions. "
        "f, Domain-wise decomposition of weighted scores for leading interventions, illustrating relative contributions from preclinical efficacy, mechanism conservation, human evidence, safety/tolerability, and access. "
        "Domain weights are: lifespan (30%), healthspan (10%), mechanism conservation (10%), human trial evidence (20%), safety & tolerability (20%), and cost & access (10%). "
        "g, Stakeholder sensitivity analysis showing how weighted scores shift under alternative weighting perspectives (baseline versus regulator-, investor-, and patient-focused). "
        "h, Overview of the multi-criteria decision analysis (MCDA) workflow used to generate the baseline ranking and perform robustness testing."
    )
    
    fig.text(0.02, 0.08, caption_text, ha='left', va='top', fontsize=7, wrap=True, family='sans-serif')

    # Save outputs
    pdf_path = here / f"{out_stem}.pdf"
    tiff_path = here / f"{out_stem}.tiff"
    png_path = here / f"{out_stem}_preview.png"

    fig.savefig(str(pdf_path), format="pdf")
    fig.savefig(str(tiff_path), format="tiff", dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(str(png_path), format="png", dpi=200)

    plt.close(fig)
    print(f"Saved multipanel: {pdf_path.name}, {tiff_path.name}, {png_path.name}")


def main():
    """Generate all figures for publication"""
    print("Loading data files...")
    print("=" * 60)
    
    # Load data files
    try:
        # Load Excel data
        excel_data = pd.read_excel('/mnt/user-data/uploads/Intervention_list_&_scores.xlsx', sheet_name='Sheet1')
        print("✓ Loaded Excel data (Intervention_list_&_scores.xlsx)")
        
        # Load CSV data
        intervals_data = pd.read_csv('/mnt/user-data/uploads/weighted_score_intervals.csv')
        print("✓ Loaded weighted score intervals")
        
        robustness_data = pd.read_csv('/mnt/user-data/uploads/ranking_robustness_weights_p5.csv')
        print("✓ Loaded ranking robustness data")
        
    except Exception as e:
        print(f"Error loading data files: {e}")
        print("Please ensure the following files are in /mnt/user-data/uploads/:")
        print("  - Intervention_list_&_scores.xlsx")
        print("  - weighted_score_intervals.csv")
        print("  - ranking_robustness_weights_p5.csv")
        return
    
    print("\nGenerating figures")
    print("=" * 60)
    
    create_figure1()
    create_figure2()
    create_figure3()
    create_figure4(excel_data)
    create_figure5(intervals_data)
    create_figure6(excel_data)
    create_figure7(excel_data)
    create_figure8()

    # Combine Figures 1–8 into multipanel (a–h)
    create_multipanel_a_to_h()

    print("=" * 60)
    print("All figures generated successfully!")
    print("\nIndividual figure files created:")
    print("- Figure1_Mortality_Risk_Factors.tiff/.eps")
    print("- Figure2_Age_Stratified_Mortality.tiff/.eps")
    print("- Figure3_US_Mortality_by_Age.tiff/.eps")
    print("- Figure4_Readiness_vs_Impact.tiff/.eps")
    print("- Figure5_Rank_Stability.tiff/.eps")
    print("- Figure6_Domain_Contributions.tiff/.eps")
    print("- Figure7_Stakeholder_Sensitivity.tiff/.eps")
    print("- Figure8_MCDA_Framework.tiff/.eps")
    print("\nMultipanel figure files created:")
    print("- Figure9_Multipanel_a-h.pdf (vector format)")
    print("- Figure9_Multipanel_a-h.tiff (300 DPI with caption)")
    print("- Figure9_Multipanel_a-h_preview.png (200 DPI preview)")
    print("\nReady")

if __name__ == "__main__":
    main()
