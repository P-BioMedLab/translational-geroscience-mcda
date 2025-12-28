import streamlit as st
import pandas as pd
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Translational Geroscience MCDA Ranking",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stDataFrame {
        font-size: 0.9em;
    }
    .top-3-row {
        background-color: #fff3cd !important;
    }
</style>
""", unsafe_allow_html=True)

# Domain mapping from Excel to app keys
DOMAIN_MAP = {
    'Human Trial Evidence': 'human',
    'Safety & Tolerability': 'safety',
    'Preclinical Efficacy (Lifespan)': 'lifespan',
    'Preclinical Efficacy (Healthspan)': 'healthspan',
    'Mechanism Conservation': 'conservation',
    'Cost & Accessibility': 'cost'
}

DOMAIN_NAMES = {
    "human": "Human Trial Evidence",
    "safety": "Safety & Tolerability",
    "lifespan": "Preclinical Efficacy (Lifespan)",
    "healthspan": "Preclinical Efficacy (Healthspan)",
    "conservation": "Mechanism Conservation",
    "cost": "Cost & Accessibility"
}

@st.cache_data
def load_evidence_from_excel(filepath='evidence_map.xlsx', uploaded_file=None):
    """Load evidence data from Excel file and build the evidence database."""
    
    df = None
    
    # First, try to load from uploaded file if provided
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            return {}, []
    
    # If no uploaded file, try to find the file in different locations
    if df is None:
        # Get the absolute path of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        
        # Assuming app.py is in interactive_tool and evidence_map.xlsx is in data folder
        possible_paths = [
            filepath,  # Current directory
            os.path.join(script_dir, filepath),  # Same directory as script
            os.path.join(script_dir, '..', 'data', filepath),  # ../data/ from script location
            os.path.join(os.getcwd(), '..', 'data', filepath),  # ../data/ from working directory
            os.path.join(os.getcwd(), 'data', filepath),  # data/ subdirectory
            os.path.join('..', 'data', filepath),  # ../data/ relative
            os.path.join('data', filepath),  # data/ relative
            '/mnt/user-data/uploads/' + filepath  # Container deployment
        ]
        
        # Try each path
        for path in possible_paths:
            try:
                # Normalize the path
                normalized_path = os.path.normpath(path)
                if os.path.exists(normalized_path):
                    df = pd.read_excel(normalized_path)
                    break
            except Exception:
                continue
        
        if df is None:
            st.error(f"⚠️ Could not find {filepath}")
            st.info("**Please upload the evidence_map.xlsx file using the uploader below.**")
            with st.expander("🔍 Debug Info - Searched Locations"):
                st.write("**Script directory:**", script_dir if 'script_dir' in locals() else "Unknown")
                st.write("**Working directory:**", os.getcwd())
                st.write("**Searched paths:**")
                for p in possible_paths:
                    exists = os.path.exists(os.path.normpath(p))
                    st.write(f"- {os.path.normpath(p)} {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
            return {}, []
    
    # Clean intervention names (remove numbering)
    df['Intervention_Clean'] = df['Intervention'].str.replace(r'^\d+\.\s*', '', regex=True).str.strip()
    
    # Build evidence database
    evidence_db = {}
    interventions_list = []
    
    for intervention in df['Intervention_Clean'].unique():
        intervention_data = df[df['Intervention_Clean'] == intervention]
        evidence_db[intervention] = {}
        
        for _, row in intervention_data.iterrows():
            domain_key = DOMAIN_MAP.get(row['Domain'])
            if domain_key:
                # Combine evidence and reference
                combined_evidence = f"{row['Evidence']} [References: {row['Reference']}]"
                evidence_db[intervention][domain_key] = {
                    'score': int(row['Score']),
                    'evidence': combined_evidence
                }
        
        # Build intervention object for INTERVENTIONS list
        intervention_obj = {'name': intervention}
        for domain_key in ['human', 'safety', 'lifespan', 'healthspan', 'conservation', 'cost']:
            if domain_key in evidence_db[intervention]:
                intervention_obj[domain_key] = evidence_db[intervention][domain_key]['score']
            else:
                intervention_obj[domain_key] = 0  # Default to 0 if missing
        
        interventions_list.append(intervention_obj)
    
    return evidence_db, interventions_list

# Load data from Excel
uploaded_file = None

# Check if file exists in expected location, if not show upload widget
if not any(os.path.exists(os.path.normpath(p)) for p in [
    'evidence_map.xlsx',
    '../data/evidence_map.xlsx',
    'data/evidence_map.xlsx',
    os.path.join(os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd(), '..', 'data', 'evidence_map.xlsx')
]):
    st.warning("⚠️ Evidence file not found in expected location. Please upload evidence_map.xlsx:")
    uploaded_file = st.file_uploader("Upload evidence_map.xlsx", type=['xlsx'], key='evidence_upload')
    if uploaded_file is None:
        st.info("The app is looking for the file at: ../data/evidence_map.xlsx")
        st.stop()

EVIDENCE_DATABASE, INTERVENTIONS = load_evidence_from_excel(uploaded_file=uploaded_file)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧬 Translational Geroscience Evidence Map & MCDA Ranking Tool</h1>
    <p>Multi-Criteria Decision Analysis of Longevity Interventions</p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
This interactive tool ranks 30 longevity interventions across 6 evidence domains using Multi-Criteria Decision Analysis (MCDA). 
Adjust domain weights to match your stakeholder perspective, then explore the detailed evidence supporting each score.
""")

# Main content area
tab1, tab2 = st.tabs(["📊 Rankings", "ℹ️ About"])

with tab1:
    st.header("Adjust Domain Weights")
    st.markdown("**Weights determine how much each domain contributes to the final ranking. Default weights are equal (1.0 each).**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weight_human = st.slider(
            "Human Trial Evidence",
            min_value=0.0, max_value=2.0, value=1.0, step=0.1,
            help="Clinical trials and human studies"
        )
        weight_safety = st.slider(
            "Safety & Tolerability",
            min_value=0.0, max_value=2.0, value=1.0, step=0.1,
            help="Known risks and side effects"
        )
    
    with col2:
        weight_lifespan = st.slider(
            "Preclinical Efficacy (Lifespan)",
            min_value=0.0, max_value=2.0, value=1.0, step=0.1,
            help="Effects on maximum lifespan in animal models"
        )
        weight_healthspan = st.slider(
            "Preclinical Efficacy (Healthspan)",
            min_value=0.0, max_value=2.0, value=1.0, step=0.1,
            help="Effects on health during aging"
        )
    
    with col3:
        weight_conservation = st.slider(
            "Mechanism Conservation",
            min_value=0.0, max_value=2.0, value=1.0, step=0.1,
            help="Evolutionary conservation of mechanism"
        )
        weight_cost = st.slider(
            "Cost & Accessibility",
            min_value=0.0, max_value=2.0, value=1.0, step=0.1,
            help="Economic feasibility and availability"
        )
    
    weights = {
        "human": weight_human,
        "safety": weight_safety,
        "lifespan": weight_lifespan,
        "healthspan": weight_healthspan,
        "conservation": weight_conservation,
        "cost": weight_cost
    }
    
    # Preset weight profiles
    st.markdown("---")
    st.markdown("**Quick Presets:**")
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
    
    with preset_col1:
        if st.button("⚖️ Equal Weights", use_container_width=True):
            st.rerun()
    
    with preset_col2:
        if st.button("🔬 Researcher Focus", use_container_width=True):
            weights["lifespan"] = 2.0
            weights["healthspan"] = 2.0
            weights["conservation"] = 1.5
    
    with preset_col3:
        if st.button("🏥 Clinical Focus", use_container_width=True):
            weights["human"] = 2.0
            weights["safety"] = 2.0
            weights["cost"] = 1.5
    
    with preset_col4:
        if st.button("💊 Drug Developer", use_container_width=True):
            weights["safety"] = 2.0
            weights["lifespan"] = 1.5
            weights["healthspan"] = 1.5
            weights["cost"] = 1.5
    
    st.markdown("---")
    
    # Calculate and display rankings
    st.header("📊 Intervention Rankings")
    
    def calculate_rankings():
        results = []
        for intervention in INTERVENTIONS:
            weighted_score = (
                intervention["human"] * weights["human"] +
                intervention["safety"] * weights["safety"] +
                intervention["lifespan"] * weights["lifespan"] +
                intervention["healthspan"] * weights["healthspan"] +
                intervention["conservation"] * weights["conservation"] +
                intervention["cost"] * weights["cost"]
            )
            
            results.append({
                "Intervention": intervention["name"],
                "Lifespan": intervention["lifespan"],
                "Healthspan": intervention["healthspan"],
                "Conservation": intervention["conservation"],
                "Human": intervention["human"],
                "Safety": intervention["safety"],
                "Cost": intervention["cost"],
                "Weighted Score": round(weighted_score, 2)
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values("Weighted Score", ascending=False).reset_index(drop=True)
        
        # Calculate rank with ties (method='min' gives tied items the same rank)
        df['Rank_Num'] = df['Weighted Score'].rank(method='min', ascending=False).astype(int)
        
        # Identify tied scores
        score_counts = df['Weighted Score'].value_counts()
        tied_scores = score_counts[score_counts > 1].index
        df['Rank'] = df['Rank_Num'].astype(str)
        df.loc[df['Weighted Score'].isin(tied_scores), 'Rank'] = df.loc[df['Weighted Score'].isin(tied_scores), 'Rank']
        
        # Reorder columns to put Rank first
        df = df[['Rank', 'Intervention', 'Lifespan', 'Healthspan', 'Conservation', 'Human', 'Safety', 'Cost', 'Weighted Score']]
        df = df.drop(columns=['Rank_Num'], errors='ignore')
        
        return df
    
    df_rankings = calculate_rankings()
    
    # Display table with styling
    st.dataframe(
        df_rankings.style.background_gradient(subset=["Weighted Score"], cmap="RdYlGn"),
        width='stretch',
        height=600,
        hide_index=True
    )

    # Download button
    csv = df_rankings.to_csv(index=False)
    st.download_button(
        label="📥 Download Rankings as CSV",
        data=csv,
        file_name="geroscience_rankings.csv",
        mime="text/csv"
    )

with tab2:
    st.header("About This Tool")
    
    st.markdown("""
    ### Overview
    This Multi-Criteria Decision Analysis (MCDA) tool systematically evaluates 30 longevity interventions 
    across 6 critical evidence domains.
    
    ### Evidence Domains
    
    **1. Human Trial Evidence (1-5 scale)**
    - Evaluates the quality and breadth of clinical evidence
    - Considers FDA approval status, trial phases, and human study results
    
    **2. Safety & Tolerability (1-5 scale)**
    - Assesses known risks, side effects, and contraindications
    - Considers both acute and chronic safety profiles
    
    **3. Preclinical Efficacy - Lifespan (1-5 scale)**
    - Based primarily on NIA Interventions Testing Program (ITP) results
    - Measures effects on maximum and median lifespan in animal models
    
    **4. Preclinical Efficacy - Healthspan (1-5 scale)**
    - Evaluates impact on age-related functional decline
    - Considers multi-organ/system benefits
    
    **5. Mechanism Conservation (1-5 scale)**
    - Assesses evolutionary conservation of the biological target
    - Higher scores indicate mechanisms conserved from invertebrates to mammals
    
    **6. Cost & Accessibility (1-5 scale)**
    - Evaluates economic feasibility and availability
    - Considers both current and projected costs
    
    ### How to Use
    1. **Adjust weights** based on your stakeholder perspective
    2. **Review rankings** to identify top interventions for your criteria
    3. **Explore evidence** using the sidebar viewer
    4. **Download results** for further analysis
    
    ### Methodology
    - Each intervention receives a score of 1-5 for each domain
    - Weighted scores are calculated based on user-defined weights
    - Rankings are updated in real-time as weights change
    - Detailed evidence and references support each score
    
    ### Data Source
    Evidence is compiled from peer-reviewed literature, clinical trials databases, 
    and the NIA Interventions Testing Program (ITP).
    """)

# Evidence viewer in sidebar
st.sidebar.header("🔍 View Evidence")

if INTERVENTIONS:
    selected_intervention = st.sidebar.selectbox(
        "Select Intervention:",
        options=[i["name"] for i in INTERVENTIONS],
        key="evidence_intervention"
    )

    selected_domain = st.sidebar.selectbox(
        "Select Domain:",
        options=list(DOMAIN_NAMES.keys()),
        format_func=lambda x: DOMAIN_NAMES[x],
        key="evidence_domain"
    )

    if st.sidebar.button("Show Evidence", use_container_width=True):
        if selected_intervention in EVIDENCE_DATABASE and selected_domain in EVIDENCE_DATABASE[selected_intervention]:
            evidence_data = EVIDENCE_DATABASE[selected_intervention][selected_domain]
            
            st.sidebar.markdown(f"### {selected_intervention}")
            st.sidebar.markdown(f"**{DOMAIN_NAMES[selected_domain]}**")
            st.sidebar.markdown(f"**Score: {evidence_data['score']}/5**")
            st.sidebar.markdown("---")
            
            # Split evidence and references
            evidence_text = evidence_data['evidence']
            if '[References:' in evidence_text:
                parts = evidence_text.split('[References:')
                main_evidence = parts[0].strip()
                references = parts[1].replace(']', '').strip()
                
                st.sidebar.markdown("**Evidence & Rationale:**")
                st.sidebar.markdown(main_evidence)
                st.sidebar.markdown("**References:**")
                st.sidebar.markdown(references, unsafe_allow_html=True)
            else:
                st.sidebar.markdown(evidence_text)
        else:
            st.sidebar.info(f"Detailed evidence for {selected_intervention} - {DOMAIN_NAMES[selected_domain]} is being compiled.")
else:
    st.sidebar.warning("No intervention data loaded. Please check that evidence_map.xlsx is available.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Click on individual scores in the table to view detailed evidence and references.</p>
    <p>Adjust weights to match your stakeholder perspective (regulator, investor, patient, or researcher).</p>
</div>
""", unsafe_allow_html=True)
