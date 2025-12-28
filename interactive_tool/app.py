import streamlit as st
import pandas as pd
import numpy as np

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

# Evidence database
EVIDENCE_DATABASE = {
    "Acarbose": {
        "cost": {"score": 5, "evidence": "Highly accessible as a low-cost, widely available generic drug. [References: DiNicolantonio JJ, et al, 2015, Open Heart, doi:10.1136/openhrt-2015-000327]"},
        "human": {"score": 3, "evidence": "Vast evidence from decades of use for diabetes/prediabetes; trials show it can prevent diabetes progression and reduce cardiovascular events. [References: DiNicolantonio JJ, et al., 2015, Open Heart, doi:10.1136/openhrt-2015-000327]"},
        "conservation": {"score": 4, "evidence": "Primary mechanism (inhibition of alpha-glucosidase) and downstream effects on aging pathways (GLP-1, IGF-I) are highly conserved across mammals. [References: Harrison DE et al., 2019, Aging Cell, doi:10.1111/acel.12898]"},
        "healthspan": {"score": 4, "evidence": "Notable benefits in mice including improved metabolic health, diminished liver degeneration, and beneficial modulation of gut microbiota. [References: Harrison DE et al., 2019, Aging Cell, doi:10.1111/acel.12898]"},
        "lifespan": {"score": 3, "evidence": "Powerful and rigorously validated; NIA ITP found it extended median lifespan of male mice by 16-22% but 5% in females. [References: Harrison DE et al., 2014, Aging Cell, 10.1111/acel.12170\nHarrison DE et al., 2019, Aging Cell, doi:10.1111/acel.12898]"},
        "safety": {"score": 3, "evidence": "Most common side effects are mild, transient GI issues.\nStandard dosing of 25-100 mg three times daily with meals causes gastrointestinal side effects, with 74% of patients reporting flatulence in a US trial [References: Chiasson J, et al., 2003, JAMA,  doi:10.1001/jama.290.4.486\nSTOP-NIDDM trial., 2003, JAMA, doi:10.1001/jama.290.4.486]"}
    },
    "Alpha-ketoglutarate (AKG)": {
        "cost": {"score": 4, "evidence": "Highly accessible; widely available as a low-cost over-the-counter supplement. [References: Demidenko O, et al., 2021, Aging (Albany NY), doi:10.18632/aging.203736.]"},
        "human": {"score": 2, "evidence": "No human trial data for geroscience; a human trial assessing AKG's effect on biological age is in progress. [References: Sandalova E et al., 2023, Geroscience, doi:10.1007/s11357-023-00813-6,]"},
        "conservation": {"score": 4, "evidence": "Highly conserved as a fundamental metabolite in the TCA cycle, contributing to metabolism, collagen synthesis, and epigenetic regulation. [References: Wu N et al., 2016, Biomolecules & Therapeutics, doi:10.4062/biomolther.2015.078.]"},
        "healthspan": {"score": 3, "evidence": "Compresses morbidity in aged mice, improving frailty index by over 40% and enhancing physical function. [References: Asadi Shahmirzadi A, et al., 2020, Cell Metab, doi:10.1016/j.cmet.2020.08.004.]"},
        "lifespan": {"score": 2, "evidence": "Consistently extends lifespan in invertebrates; key mouse study showed 12% median lifespan extension, more pronounced in females.\nFollowing ITP study did not find any significant lifespan benefit in either sex [References: Asadi Shahmirzadi A, et al., 2020, Cell Metab, doi:10.1016/j.cmet.2020.08.004\nMiller et al., 2024, Geroscience, doi: 10.1007/s11357-024-01176-2]"},
        "safety": {"score": 4, "evidence": "Considered Generally Recognized as Safe (GRAS) by the FDA; preclinical study in mice found no significant adverse effects. [References: Asadi Shahmirzadi A, et al., 2020, Cell Metab, doi:10.1016/j.cmet.2020.08.004.]"}
    },
    "Anti-Inflammatory Therapy": {
        "cost": {"score": 4, "evidence": "Highly accessible; many drugs are available over-the-counter and are very low cost. [References: Grootendorst et al., 2005, Health Services Research, 10.1111/j.1475-6773.2005.00420.x]"},
        "human": {"score": 3, "evidence": "A large trial (ASPREE) found daily low-dose aspirin did not prolong healthy living in older adults and increased bleeding risk. [References: McNeil et al., 2018, New England Journal of Medicine, 10.1056/NEJMoa1800722]"},
        "conservation": {"score": 4, "evidence": "The inflammatory response is a deeply conserved biological mechanism. [References: Medzhitov, 2008, Nature, 10.1038/nature07201]"},
        "healthspan": {"score": 3, "evidence": "Reducing inflammation would have broad benefits; drugs like NSAIDs also activate NRF2, a master regulator of cellular homeostasis. [References: Eisenstein et al., 2022, Immunity, 10.1016/j.immuni.2022.04.015]"},
        "lifespan": {"score": 3, "evidence": "The NIA ITP study found no increase for aspirin in mice. But inhibition of IL-11 signalling extended mice lifespan by average 24.9% [References: Strong et al., 2008, Aging Cell, doi: 10.1111/j.1474-9726.2008.00414.x\nWidjaja et al., 2024, Nature, doi: 10.1038/s41586-024-07701-9]"},
        "safety": {"score": 3, "evidence": "Significant risks of side effects, including gastrointestinal bleeding and kidney problems. [References: Harirforoosh et al., 2013, Journal of Pharmacy & Pharmaceutical Sciences, 10.18433/J3VW2F]"}
    },
    "Autophagy Inducers (Spermidine)": {
        "cost": {"score": 4, "evidence": "Highly accessible due to low cost and widespread availability as an over-the-counter supplement. [References: Madeo et al., 2018, Autophagy Reviews (Perspective), doi: 10.1126/science.aan2788]"},
        "human": {"score": 2, "evidence": "Early phases; small studies suggest improved cognitive skills in older adults, but larger trials are needed. [References: Wirth et al., 2018, Cortex, doi:10.1016/j.cortex.2018.09.014]"},
        "conservation": {"score": 5, "evidence": "Highly conserved; induces autophagy, a fundamental cellular cleanup process, by inhibiting the acetyltransferase EP300. [References: Pietrocola et al., 2015, Cell Death & Differentiation, doi:10.1038/cdd.2014.215]"},
        "healthspan": {"score": 4, "evidence": "Strong effects, particularly on cardiac and brain function; higher dietary intake correlated with lower incidence of cardiovascular diseases in humans. [References: LaRocca et al., 2013, Mechanisms of Ageing and Development, doi:10.1016/j.mad.2013.04.004]"},
        "lifespan": {"score": 4, "evidence": "Prolongs lifespan in a wide array of organisms including yeast, flies, worms, and average of 11% in mice in on study.\nLifelong oral administration of spermidine extended the lifespan of mice by up to 25% in another study on diseased model. [References: Eisenberg et al., 2016, Nature Medicine, doi:10.1038/nm.4222\nYue et al., 2017, Cancer Res., doi: 10.1158/0008-5472.CAN-16-3462]"},
        "safety": {"score": 4, "evidence": "Favorable safety profile as a natural polyamine found in food; well-tolerated. [References: Schwarz et al., 2018, Aging (Albany NY), doi:10.18632/aging.101354]"}
    },
    "Chemical Reprogramming": {
        "cost": {"score": 2, "evidence": "Likely to be high-cost and require specialist administration, though potentially cheaper than viral vectors. [References: Kim Y et al., 2020, Experimental & Molecular Medicine, doi:10.1038/s12276-020-0383-3]"},
        "human": {"score": 1, "evidence": "No human trial data for geroscience indication. [References: Wang J et al., 2023, Cell Stem Cell, doi:10.1016/j.stem.2023.08.001]"},
        "conservation": {"score": 4, "evidence": "Strong theoretical basis; targets highly conserved fundamental mechanisms like DNA methylation and histone modification. [References: Allis CD et al., 2016, Nature Reviews Genetics, doi:10.1038/nrg.2016.59]"},
        "healthspan": {"score": 2, "evidence": "Lacks direct healthspan data for mammalian models, but reverses cellular aging markers in human cells. [References: Yang JH et al., 2023, Aging (Albany NY), doi:10.18632/aging.204896]"},
        "lifespan": {"score": 2, "evidence": "No direct evidence in mammals; one study showed lifespan extension in C. elegans.by 42% [References: Schoenfeldt L et al., 2025, EMBO Molecular Medicine, doi:10.1038/s44321-025-00265-9]"},
        "safety": {"score": 2, "evidence": "Unproven for systemic use; small molecules are safer than transgenic methods as they don't integrate into the genome, but systemic use requires thorough testing. [References: Kim Y et al., 2020, Experimental & Molecular Medicine, doi:10.1038/s12276-020-0383-3]"}
    },
    "Chloroquine": {
        "cost": {"score": 4, "evidence": "Low cost as a generic drug, but this is irrelevant given its detrimental effects. [References: Kamat S et al., 2021, Frontiers in Pharmacology, doi:10.3389/fphar.2021.576093]"},
        "human": {"score": 2, "evidence": "Large body of data from malaria/autoimmune use, but none for a geroscience indication. [References: Nirk EL et al., 2020, EMBO Molecular Medicine, doi:10.15252/emmm.202012476]"},
        "conservation": {"score": 4, "evidence": "Conserved across eukaryotes; inhibits autophagy by preventing autophagosome-lysosome fusion. [References: Mauthe M et al., 2018, Autophagy, doi:10.1080/15548627.2018.1474314]"},
        "healthspan": {"score": 2, "evidence": "Detrimental; emulates aging on the neuromuscular system, causing denervation and decreased muscle force in mice. [References: Saldarriaga CA et al., 2023, Journal of Applied Physiology, doi:10.1152/japplphysiol.00365.2023]"},
        "lifespan": {"score": 3, "evidence": "Chloroquine extended median by 11–12% in mice (Doeppner) and by 6% in rats (Li). [References: Doeppner TR et al., 2022, Aging (Albany NY), doi:10.18632/aging.204069\nLi et al., 2022, Protein Cell, doi: 10.1007/s13238-021-00903-1]"},
        "safety": {"score": 2, "evidence": "Major barrier; substantial side effect profile including potential neuromyopathy, retinopathy, and serious heart rhythm problems. [References: Bansal P et al., 2021, Annals of Medicine, doi:10.1080/07853890.2020.1839959]"}
    },
    "Epigenetic Reprogramming": {
        "cost": {"score": 1, "evidence": "Prohibitively high; current delivery via viral vectors can cost over $1 million per dose. [References: Johnson et al., 2023, Nature Biotechnology, doi:10.1038/s41587-023-01760-5]"},
        "human": {"score": 1, "evidence": "Entirely preclinical; first-in-human trials are beginning for specific indications like vision loss. [References: Yücel et al., 2024, Nature Communications, doi:10.1038/s41467-024-46020-5]"},
        "conservation": {"score": 4, "evidence": "Based on the highly conserved nature of epigenetic regulation across all eukaryotic life. [References: Allis et al., 2016, Nature Reviews Genetics, doi:10.1038/nrg.2016.59]"},
        "healthspan": {"score": 3, "evidence": "Significant improvement in frailty index and functional rejuvenation in specific tissues. [References: Cano Macip et al., 2024, Cellular Reprogramming, doi:10.1089/cell.2023.0072]"},
        "lifespan": {"score": 2, "evidence": "A 2024 study showed a 109% extension of remaining median lifespan in very old mice. Partial cellular reprogramming via Yamanaka factors (OSKM) ameliorated age-associated hallmarks and extended the lifespan of progeroid mice by 30%. [References: Cano Macip et al., 2024, Cellular Reprogramming, doi:10.1089/cell.2023.0072\nOcampo, 2016, Cell, doi: 10.1016/j.cell.2016.11.052]"},
        "safety": {"score": 2, "evidence": "Greatest concern; continuous expression can lead to teratoma formation/cancer; delivery via viral vectors carries risks. [References: Abad et al., 2013, Nature, doi:10.1038/nature12586]"}
    },
    "Exosome Therapy": {
        "cost": {"score": 2, "evidence": "Prohibitive cost, making it a highly restricted therapy. [References: Wang et al., 2024, Clinical and Translational Science, doi:10.1111/cts.13904]"},
        "human": {"score": 2, "evidence": "Limited and largely focused on aesthetic applications; no large-scale human data for systemic anti-aging effects. [References: Gupta et al., 2023, Journal of Cosmetic Dermatology, doi:10.1111/jocd.15869]"},
        "conservation": {"score": 3, "evidence": "Based on intercellular communication, a fundamental and conserved biological process. [References: Kalluri et al., 2020, Science, doi:10.1126/science.aau6977]"},
        "healthspan": {"score": 2, "evidence": "Possess regenerative, immunomodulatory, and anti-inflammatory properties; can stimulate collagen synthesis and promote muscle regeneration. [References: Sanz-Ros et al., 2022, Science Advances, doi:10.1126/sciadv.abq2226]"},
        "lifespan": {"score": 2, "evidence": "Exosomal miR-302b rejuvenated aging mice and extended lifespan by average 18.5% by reversing the proliferative arrest of senescent cells. Another study reported ~12% median lifespan extension in aged mice treated with young plasma sEVs [References: Bi et al., 2025, Cell Metab., doi: https://doi.org/10.1016/j.cmet.2024.11.013\nChen et al., 2024, Nature Aging, doi:10.1038/s43587-024-00612-4]"},
        "safety": {"score": 3, "evidence": "Advantage over stem cells as they are acellular, reducing risks like embolism; generally well-tolerated, but long-term systemic safety is unknown. [References: Xu et al., 2025, Signal Transduction and Targeted Therapy, doi:10.1038/s41392-025-02312-w]"}
    },
    "GLP-1 Receptor Agonists": {
        "cost": {"score": 2, "evidence": "High cost (~$12,000/year) and inaccessible for many. [References: Lin T, et al., 2024, Ann Intern Med, doi:10.7326/M23-2736.]"},
        "human": {"score": 4, "evidence": "FDA-approved for diabetes/obesity. Large trials show reduced cardiovascular events. Semaglutide shown to reduce epigenetic age. [References: Marso SP, et al., 2016, N Engl J Med, doi:10.1056/NEJMoa1607141\nCorley MJ, et al., 2024, Nat Commun, doi:10.1038/s41467-024-51772-5]"},
        "conservation": {"score": 4, "evidence": "Highly conserved pathway in metabolic control (brain, heart, pancreas); mimics endogenous hormone GLP-1. [References: Drucker DJ, 2018, Cell Metab, doi:10.1016/j.cmet.2018.03.001]"},
        "healthspan": {"score": 4, "evidence": "Broad benefits: improved cardiovascular health, reduced hepatic fat, and potential neuroprotective effects. [References: Zheng Z et al., 2024, Signal Transduction and Targeted Therapy, doi:10.1038/s41392-024-01931-z.\nSomineni HK, 2014, J Endocrinol, doi:10.1530/JOE-13-0532.]"},
        "lifespan": {"score": 1, "evidence": "Protective Effects of Liraglutide and Linagliptin \nin C. elegans with lifespan extension ~10%\nNo study available on rodents [References: Wongchai et al., 2016, Horm Metab Res., doi: 10.1055/s-0035-1549876]"},
        "safety": {"score": 3, "evidence": "Well-characterized profile, but side effects like nausea and vomiting can be significant. [References: Nauck MA, et al., 2021, Lancet, doi:10.1016/S0140-6736(21)00214-7.]"}
    },
    "Gene Therapy": {
        "cost": {"score": 1, "evidence": "Prohibitively inaccessible; among the most expensive medical interventions, with prices in the millions of dollars per dose. [References: Naddaf, 2022, Nature (news feature), doi:10.1038/d41586-022-04327-7]"},
        "human": {"score": 1, "evidence": "Entirely preclinical for a geroscience indication. [References: Kroemer et al., 2025, Cell, doi:10.1016/j.cell.2025.03.011]"},
        "conservation": {"score": 4, "evidence": "Based on the fundamental principle of gene regulation; the Klotho gene is a conserved aging-suppressing gene in mammals. [References: Xu et al., 2015, Endocrine Reviews, doi:10.1210/er.2013-1079]"},
        "healthspan": {"score": 3, "evidence": "Consistent benefits including improved physical and cognitive function, larger muscle fibers, better bone density, and stimulated neurogenesis. [References: Roig-Soriano et al., 2025, Molecular Therapy, doi:10.1016/j.ymthe.2025.02.030]"},
        "lifespan": {"score": 3, "evidence": "The starvation hormone, fibroblast growth factor-21, extended lifespan in transgenic mice by 36% in one study. Another study showed elevating Klotho protein levels via gene therapy extended mouse lifespan by up to 20%. [References: Zhang et al., 2012, Elife, doi: 10.7554/eLife.00065\nRoig-Soriano J et al., 2025, Molecular Therapy, doi:10.1016/j.ymthe.2025.02.030]"},
        "safety": {"score": 2, "evidence": "Most significant barrier; use of viral vectors (AAVs) carries risks of off-target effects and life-threatening immune reactions. [References: Ronzitti et al., 2020, Frontiers in Immunology, doi:10.3389/fimmu.2020.00670]"}
    },
    "Glutathione Precursors": {
        "cost": {"score": 4, "evidence": "Highly accessible as a low-cost nutritional supplement. [References: Sekhar RV et al., 2022, Antioxidants, doi:10.3390/antiox11010154]"},
        "human": {"score": 3, "evidence": "Promising but preliminary; a small, placebo-controlled trial found it was safe and improved a suite of age-associated abnormalities. [References: Kumar P et al., 2023, Journals of Gerontology Series A, doi:10.1093/gerona/glac135]"},
        "conservation": {"score": 4, "evidence": "Based on a fundamental and highly conserved biochemical process: replenishing glutathione to protect mitochondria from oxidative stress. [References: Marí M et al., 2020, Antioxidants, doi:10.3390/antiox9100909]"},
        "healthspan": {"score": 3, "evidence": "Improves a range of age-related defects in mice (oxidative stress, mitochondrial function, insulin resistance); also improved physical function in a human trial. [References: Kumar P et al., 2021, Clinical and Translational Medicine, doi:10.1002/ctm2.372]"},
        "lifespan": {"score": 3, "evidence": "Limited direct studies, but individual components (glycine) have extended lifespan in mice. GlyNAC (Glycine and N-Acetylcysteine) Supplementation in Mice Increased mouse lifespan by 24% [References: Miller RA et al., 2019, Aging Cell, doi:10.1111/acel.12953\nKumar P et al., 2022, Nutrients, doi:10.3390/nu14051114]"},
        "safety": {"score": 4, "evidence": "Human trial reported it was \"safe and well-tolerated\" with \"no adverse events\". [References: Lizzo G et al., 2022, Frontiers in Aging, doi:10.3389/fragi.2022.852569]"}
    },
    "Gut Microbiome Modulation": {
        "cost": {"score": 4, "evidence": "Lifestyle changes and many probiotics are low-cost; however, therapies like FMT can be very expensive. [References: Wynn et al., 2023, Cureus, doi:10.7759/cureus.35116]"},
        "human": {"score": 3, "evidence": "Probiotics show moderate effects on immune function in older adults; one pilot trial of a symbiotic reversed biological age. [References: Fitzgerald et al., 2021, Aging (Albany NY), doi:10.18632/aging.202913]"},
        "conservation": {"score": 4, "evidence": "The interaction between a host and its microbial ecosystem is a highly conserved biological mechanism. [References: Wilde et al., 2024, Science, doi:10.1126/science.adi3338]"},
        "healthspan": {"score": 3, "evidence": "Can reduce chronic inflammation (\"inflammaging\"), improve metabolic health, and alleviate depression/anxiety-like behaviors in aged mice. [References: Parker et al., 2022, Microbiome, doi:10.1186/s40168-022-01243-w]"},
        "lifespan": {"score": 3, "evidence": "Fecal microbiota transplantation (FMT) from young to old mice extends lifespan and improves healthspan. Several studies testing probiotics effect on C. Elegans demonstrated lifespan increase between 17 to 30% [References: Bárcena et al., 2019, Nature Medicine, doi:10.1038/s41591-019-0504-5\nKumaree et al., 2023, Sci Rep., doi: 10.1038/s41598-023-43846-9\nZhang et al., 2022, Commun Biol., doi: 10.1038/s42003-022-04031-2\nSaito et al., 2023, Biosci Microbiota Food Health, doi: 10.12938/bmfh.2022-057]"},
        "safety": {"score": 4, "evidence": "Favorable safety for diet-based modulation and many probiotics; FMT carries risks of complications and pathogen transmission. [References: DeFilipp et al., 2019, New England Journal of Medicine, doi:10.1056/NEJMoa1910437]"}
    },
    "Immunotherapy for Senescent Cells": {
        "cost": {"score": 1, "evidence": "Expected to be prohibitively high; similar therapies (CAR T-cell) can cost over $500,000 per dose. [References: Hernandez et al., 2018, JAMA Oncology, doi:10.1001/jamaoncol.2018.0977]"},
        "human": {"score": 1, "evidence": "Purely preclinical for geroscience, with no human trials underway. [References: Lelarge et al., 2024, npj Aging, doi:10.1038/s41514-024-00138-4]"},
        "conservation": {"score": 4, "evidence": "Based on the conserved processes of cellular senescence and the adaptive immune system. [References: Ogrodnik et al., 2024, Cell, doi:10.1016/j.cell.2024.05.059]"},
        "healthspan": {"score": 2, "evidence": "Shown to be effective in ameliorating age-associated pathologies like liver fibrosis and metabolic dysfunction in mice. [References: Amor et al., 2020, Nature, doi:10.1038/s41586-020-2403-9]"},
        "lifespan": {"score": 1, "evidence": "Preclinical studies show a senolytic CAR-T cell therapy can improve aging phenotypes. Genetic clearance of p16^Ink4a-positive (senescent) cells in otherwise wild-type mice extended median lifespan by 24% and improved multiple organ functions [References: Amor et al., 2024, Nature Aging, doi:10.1038/s43587-023-00560-5\nBaker et al., 2016, Nature, doi: 10.1038/nature16932]"},
        "safety": {"score": 2, "evidence": "Entirely unknown; risk of off-target effects and autoimmune reactions is a major concern. [References: Lelarge et al., 2024, npj Aging, doi:10.1038/s41514-024-00138-4]"}
    },
    "L-deprenyl": {
        "cost": {"score": 3, "evidence": "Low-cost and widely accessible as an approved, generic drug. [References: Dorsey ER et al., 2009, Neurology, doi:10.1212/WNL.0b013e3181ae7b04]"},
        "human": {"score": 3, "evidence": "Vast indirect evidence from long-term use for Parkinson's disease; no clinical study on healthy human aging. [References: Jost WH et al., 2022, Journal of Neural Transmission, doi:10.1007/s00702-022-02465-w]"},
        "conservation": {"score": 4, "evidence": "Conserved mechanism of irreversible inhibition of monoamine oxidase B (MAO-B), an enzyme in dopamine metabolism. [References: Tan YY et al., 2022, Journal of Parkinson's Disease, doi:10.3233/JPD-212976]"},
        "healthspan": {"score": 3, "evidence": "Neuroprotective effects; improves aspects of age-related hearing loss in mice; has antioxidant and anti-apoptotic effects. [References: Szepesy J et al., 2021, International Journal of Molecular Sciences, doi:10.3390/ijms22062853]"},
        "lifespan": {"score": 3, "evidence": "L-deprenyl treatment in aged mice increased lifespan by average 8%, and greatly reduced fecundity by aged males.\nOther studies on rats achieved similar or higher increases [References: Archer, Harrison, 1996, J Gerontol A Biol Sci Med Sci., doi: 10.1093/gerona/51a.6.b448\nKitani et al., 2005, Biogerontology, doi: 10.1007/s10522-005-4804-4]"},
        "safety": {"score": 4, "evidence": "Generally well-tolerated at low doses used for Parkinson's; high doses carry risk of interactions. [References: Wang K et al., 2023, Frontiers in Aging Neuroscience, doi:10.3389/fnagi.2023.1134472]"}
    },
    "Metformin": {
        "cost": {"score": 5, "evidence": "Highly accessible; available as a generic drug for pennies a day. [References: Soukas AA, et al., 2019, Annu Rev Med, doi:10.1146/annurev-med-050217-054734.]"},
        "human": {"score": 3, "evidence": "Vast indirect evidence from 60+ years of use; retrospective studies show lower all-cause mortality; prospective TAME trial is pending. [References: Barzilai N, et al., 2016, Cell Metab, doi:10.1016/j.cmet.2016.05.011.]"},
        "conservation": {"score": 4, "evidence": "Primary target, AMPK, is an exceptionally conserved central regulator of cellular energy metabolism across all eukaryotes. [References: Hardie DG, et al., 2012, Nat Rev Mol Cell Biol, doi:10.1038/nrm3368.]"},
        "healthspan": {"score": 4, "evidence": "More consistent than lifespan; improves physical performance, insulin sensitivity, and cognitive function in non-human primates. [References: Kodali, M., et al., 2021, Aging Cell, doi:10.1111/acel.13277]"},
        "lifespan": {"score": 2, "evidence": "Inconsistent; extends invertebrate lifespan, but multiple rodent studies (including NIA ITP) failed to show a significant/reproducible effect. [References: Strong, R., et al., 2016, Aging Cell, doi: 10.1111/acel.12496\nSmith DL Jr et al., 2010, J Gerontol A Biol Sci Med Sci., doi: 10.1093/gerona/glq033]"},
        "safety": {"score": 5, "evidence": "Unparalleled safety; on WHO Essential Medicines list, used by >150M people. Lactic acidosis is extremely rare. [References: Flory JH & Lipska K, 2019, JAMA, doi:10.1001/jama.2019.11708.]"}
    },
    "Mitochondria (Elamipretide/SS-31)": {
        "cost": {"score": 1, "evidence": "Expected to be prohibitively high as an investigational drug requiring injection. [References: Sabbah, 2022, Cardiovascular Drugs and Therapy, doi:10.1007/s10741-021-10177-8]"},
        "human": {"score": 2, "evidence": "Limited to specific rare diseases (e.g., Barth syndrome); primary endpoints have not always been met. [References: Thompson et al., 2021, Genetics in Medicine, doi:10.1038/s41436-020-01006-8]"},
        "conservation": {"score": 4, "evidence": "Highly conserved; targets cardiolipin in the inner mitochondrial membrane to stabilize cristae, reduce oxidative stress, and enhance ATP production. [References: Szeto, 2014, British Journal of Pharmacology, doi:10.1111/bph.12461]"},
        "healthspan": {"score": 3, "evidence": "Strong benefits in preclinical models, including improved cardiac and skeletal muscle function and rescued muscle force in aging mice. [References: Campbell et al., 2019, Free Radical Biology and Medicine, doi:10.1016/j.freeradbiomed.2018.12.031]"},
        "lifespan": {"score": 2, "evidence": "Lack of explicit lifespan data, but improves physiological function in aging mouse models. [References: Chiao et al., 2020, eLife, doi:10.7554/eLife.55513]"},
        "safety": {"score": 3, "evidence": "Strength; well-tolerated in trials, with the most common side effects being mild injection-site reactions. [References: Karaa et al., 2023, Neurology, doi:10.1212/WNL.0000000000207402]"}
    },
    "Mitochondria (Urolithin A)": {
        "cost": {"score": 3, "evidence": "Barrier; branded, clinically-tested formulations are often expensive. [References: Kuerec et al., 2024, Ageing Research Reviews, doi:10.1016/j.arr.2024.102406]"},
        "human": {"score": 3, "evidence": "Promising but preliminary; human trials report positive outcomes in muscle strength and endurance. [References: Liu et al., 2022, JAMA Network Open, doi:10.1001/jamanetworkopen.2021.44279]"},
        "conservation": {"score": 4, "evidence": "Based on activating mitophagy, a highly conserved cellular cleanup process for removing damaged mitochondria. [References: Faitg et al., 2023, Calcified Tissue International, doi:10.1007/s00223-023-01145-5]"},
        "healthspan": {"score": 4, "evidence": "Broad benefits including anti-inflammatory, antioxidant, and anti-aging properties; improves muscle function and delays fatigue in animal models. [References: D'Amico et al., 2021, Trends in Molecular Medicine, doi:10.1016/j.molmed.2021.04.009]"},
        "lifespan": {"score": 2, "evidence": "Urolithin A reduced amyloid-beta load and improved cognitive deficits in a mouse model of Alzheimer's disease with 18.75% lifespan increase. One study found a 35% average lifespan increase in C. elegans and improved rodent healthspan. [References: Ballesteros-Álvarez et al., 2023, Geroscience, doi: 10.1007/s11357-022-00708-y\nRyu et al., 2016, Nature Medicine, doi:10.1038/nm.4132]"},
        "safety": {"score": 4, "evidence": "Strong safety profile; no serious adverse events reported in human trials. [References: Andreux et al., 2019, Nature Metabolism, doi:10.1038/s42255-019-0073-4]"}
    },
    "NAD+ Restoration (NMN/NR)": {
        "cost": {"score": 3, "evidence": "Available as over-the-counter supplements at a moderate cost. [References: McDermott et al., 2024, Nature Communications, doi:10.1038/s41467-024-49092-5]"},
        "human": {"score": 3, "evidence": "Growing evidence from small trials confirms safety and efficacy in increasing blood NAD+ levels; reported benefits in muscle insulin sensitivity and walking endurance. [References: Yoshino M, et al., 2021, Science, doi:10.1126/science.abe9985.]"},
        "conservation": {"score": 5, "evidence": "Major strength; NAD+ metabolism is a fundamental and ancient biochemical process conserved across all domains of life. [References: Belenky et al., 2007, Trends in Biochemical Sciences]"},
        "healthspan": {"score": 3, "evidence": "Stronger evidence than for lifespan; numerous rodent studies show amelioration of age-associated declines in insulin sensitivity, vascular health, and physical endurance. [References: Rajman et al., 2018, Cell Metabolism, doi:10.1016/j.cmet.2018.01.008]"},
        "lifespan": {"score": 1, "evidence": "Nicotinamide riboside (NR) did not extend lifespan in NIA ITP mouse studies. Nicotinamide mononucleotide (NMN) extended median lifespan by 0%, in one study and 20% in progeroid mice in another study. [References: Mitchell et al., 2018, Cell Metab., doi: 10.1016/j.cmet.2018.02.001\nHarrison et al., 2021, Aging Cell, doi:10.1111/acel.13328\nGu et al., 2024, Food Funct., doi: 10.1039/d3fo05221d]"},
        "safety": {"score": 4, "evidence": "Favorable safety profile; multiple human trials found supplements to be safe and well-tolerated with no significant adverse events. [References: Berven et al., 2023, Nature Communications, doi:10.1038/s41467-023-43514-6]"}
    },
    "Natural Senolytics (Fisetin)": {
        "cost": {"score": 4, "evidence": "Highly accessible due to low cost and widespread availability as an over-the-counter supplement. [References: Yousefzadeh MJ, et al., 2018, EBioMedicine, doi:10.1016/j.ebiom.2018.09.015.]"},
        "human": {"score": 2, "evidence": "Early stages; trials are underway for frailty, but no definitive results for an anti-aging indication exist. [References: Yousefzadeh MJ et al., 2018, eBioMedicine, doi:10.1016/j.ebiom.2018.09.015]"},
        "conservation": {"score": 4, "evidence": "Acts as a senolytic by clearing senescent cells and inhibiting SASP; also modulates highly conserved PI3K/AKT/mTOR and SIRT1 pathways. [References: Tavenier et al., 2024, Mechanisms of Ageing and Development, 10.1016/j.mad.2024.111995]"},
        "healthspan": {"score": 3, "evidence": "Benefits are broad-acting; studies show it can prevent cognitive decline, reduce inflammation, and improve metabolic health in animal models. [References: Pal HC et al., 2016, Advances in Experimental Medicine and Biology, doi:10.1007/978-3-319-41334-1_10]"},
        "lifespan": {"score": 2, "evidence": "Extended mouse lifespan by ~10% in one study, but contested by NIA ITP testing which found no effect. [References: Yousefzadeh MJ, et al., 2018, EBioMedicine, doi:10.1016/j.ebiom.2018.09.015\nHarrison et al., 2024, Geroscience, doi: 10.1007/s11357-023-01011-0]"},
        "safety": {"score": 4, "evidence": "Major advantage; as a natural compound in food, it is generally considered safe for human use. [References: Yousefzadeh MJ et al., 2018, eBioMedicine, doi:10.1016/j.ebiom.2018.09.015]"}
    },
    "Plasma Dilution/Apheresis": {
        "cost": {"score": 2, "evidence": "Significant barrier; cost is high, making it highly inaccessible for broad preventative use. [References: Winters et al., 2011, BMC Health Services Research, 10.1186/1472-6963-11-101]"},
        "human": {"score": 3, "evidence": "A single human trial showed therapeutic plasma exchange (TPE) lowered biological age by 2.6 years [References: Kim et al., 2022, GeroScience, 10.1007/s11357-022-00645-w]"},
        "conservation": {"score": 4, "evidence": "Based on the conserved concept that aging is driven by an accumulation of detrimental molecular factors in the blood. [References: Lagunas-Rangel et al., 2024, npj Aging Mechanisms of Disease, 10.1038/s41514-024-00166-0]"},
        "healthspan": {"score": 3, "evidence": "Benefits include rejuvenation of muscle and liver, and promotion of better hippocampal neurogenesis in mice. [References: Mehdipour et al., 2020, Aging (Albany NY), 10.18632/aging.103418]"},
        "lifespan": {"score": 3, "evidence": "A preclinical study showed that diluting old plasma was more effective than adding young plasma at rejuvenating multiple tissues in mice. [References: Mehdipour et al., 2020, Aging (Albany NY), 10.18632/aging.103418]"},
        "safety": {"score": 3, "evidence": "TPE is an FDA-approved procedure with a known and generally well-managed safety profile; most side effects are mild-to-moderate. [References: Shemin et al., 2007, Journal of Clinical Apheresis, 10.1002/jca.20143]"}
    },
    "Proteostasis & Nucleolar Function": {
        "cost": {"score": 2, "evidence": "Early translational stage. Few pharmacologic tools exist to selectively modulate these pathways in humans. [References: Klaips et al., 2018, Journal of Cell Biology, doi:10.1083/jcb.201709072]"},
        "human": {"score": 1, "evidence": "Non-existent for a geroscience indication. [References: Rolland et al., 2023, Nature Communications, doi:10.1038/s41467-023-39786-7]"},
        "conservation": {"score": 5, "evidence": "Nucleolar size/activity and protein clearance pathways (UPS, autophagy) are evolutionarily conserved across species. [References: Finley et al., 2012, Genetics, doi:10.1534/genetics.112.140467]"},
        "healthspan": {"score": 3, "evidence": "Enhanced protein clearance improves age-linked functional decline in model organisms. rDNA stability gains reduce proteotoxic burden. [References: Yu et al., 2024, Autophagy, doi:10.1080/15548627.2024.2389607]"},
        "lifespan": {"score": 1, "evidence": "Experimental reduction of nucleolar output extended lifespan by 33% in S. cerevisiae and 25% in C. Elegans. USP14 inhibition extended lifespan in Drosophila melanogaster. [References: Gutierrez et al., 2024, Nature Aging, doi: 10.1038/s43587-024-00754-5\nTiku et al., 2017, Nature Communications, doi:10.1038/ncomms16083\nLim et al., 2024, Autophagy, doi: 10.1080/15548627.2024.2389607]"},
        "safety": {"score": 2, "evidence": "Overt suppression of ribosome production could impair immunity or hematopoiesis [References: Tubío-Santamaría et al., 2021, Cells, doi:10.3390/cells10071577]"}
    },
    "Rapamycin/mTOR Inhibitors": {
        "cost": {"score": 3, "evidence": "Moderate cost as a generic prescription drug. [References: Taber, D. J., et al., 2015, Current Opinion in Organ Transplantation, doi:10.1007/s40472-015-0052-y]"},
        "human": {"score": 3, "evidence": "Limited to small-scale studies; FDA-approved for transplant/cancer but early stage for geroscience. [References: Mannick JB, et al., 2014, Sci Transl Med, doi:10.1126/scitranslmed.3009892]"},
        "conservation": {"score": 5, "evidence": "mTOR pathway is a master regulator of metabolism, ubiquitously and highly conserved from yeast to humans. [References: Saxton RA et al., 2017, Cell, doi:10.1016/j.cell.2017.02.004]"},
        "healthspan": {"score": 4, "evidence": "Broad and potent benefits; delays cognitive decline, cardiac dysfunction, and immune senescence. [References: Bitto, A., et al., 2016, eLife, doi:10.7554/eLife.16351]"},
        "lifespan": {"score": 4, "evidence": "NIA ITP confirmed significant median and maximal lifespan extension (up to 28%) in mice, even when started late in life, but on high dosing unreplicated in humans [References: Miller RA, Harrison, et al., 2014, Aging Cell, doi:10.1111/acel.12194\nHarrison, D. E., et al., 2009, Nature, doi:10.1038/nature08221]"},
        "safety": {"score": 3, "evidence": "FDA-approved but chronic use has moderate risks; high doses cause side effects like metabolic disturbances, stomatitis, and impaired wound healing. [References: Kaeberlein M, 2014, J Genet Genomics, doi:10.1016/j.jgg.2014.06.009]"}
    },
    "SGLT2 inhibitors (Canagliflozin)": {
        "cost": {"score": 3, "evidence": "Moderate cost as branded prescription drugs. [References: Aggarwal R et al., 2022, Circulation: Heart Failure, doi:10.1161/CIRCHEARTFAILURE.121.009099]"},
        "human": {"score": 4, "evidence": "Exceptionally strong evidence; FDA-approved for heart failure and chronic kidney disease, preventing major age-related diseases. [References: Packer M, et al., 2020, N Engl J Med, doi:10.1056/NEJMoa2024816.]"},
        "conservation": {"score": 4, "evidence": "Pleiotropic and highly conserved mechanisms, including modulation of mTOR/AMPK and the NLRP3 inflammasome. [References: Yesilyurt-Dirican Z et al., 2025, npj Aging and Mechanisms of Disease, doi:10.1038/s41514-025-00227-y]"},
        "healthspan": {"score": 4, "evidence": "Broad benefits in animal models: reduced visceral fat, preserved lean mass, and mitigation of cardiomyopathy and kidney disease. [References: Snyder, J.M., et al., 2023, GeroScience, doi:10.1007/s11357-022-00641-0]"},
        "lifespan": {"score": 3, "evidence": "NIA ITP found a 14% median lifespan extension in male mice, but benefits appear confined to males. [References: Snyder JM, et al., 2023, Geroscience, doi:10.1007/s11357-022-00641-0.]"},
        "safety": {"score": 4, "evidence": "Favorable safety profile; side effects (increased urination, genital infections) are manageable and often transient. [References: Neal B, et al., 2017, N Engl J Med, doi:10.1056/NEJMoa1611925]"}
    },
    "Senolytics (D+Q)": {
        "cost": {"score": 2, "evidence": "Likely to be high cost due to the inclusion of Dasatinib, a chemotherapy drug. [References: Rad AN et al., 2024, Current Drug Metabolism, doi:10.1016/j.mad.2023.111888]"},
        "human": {"score": 3, "evidence": "Preliminary; early-phase trials show reduced senescent cell burden and improved physical function in patients with specific diseases. [References: Hickson LJ et al., 2019, EBioMedicine, doi:10.1016/j.ebiom.2019.08.069.]"},
        "conservation": {"score": 4, "evidence": "Cellular senescence is a highly conserved biological process in vertebrates. [References: Davaapil H et al., 2017, Development, doi:10.1242/dev.138222]"},
        "healthspan": {"score": 4, "evidence": "Primary strength; broad and impressive effects, improving cardiovascular function, osteoporosis, physical, and cognitive performance. [References: Wyatt AW et al., 2021, Annual Review of Pharmacology and Toxicology,  doi:10.1146/annurev-pharmtox-050120-105018]"},
        "lifespan": {"score": 1, "evidence": "Positive but modest; pharmacological clearance with D+Q increased median lifespan in mice by ~6.3% in one 2018 study.\nA following study argues that this modest extension is likely due to off-target mTOR inhibition rather than elimination of senescent cells. [References: Xu et al., 2018, Nat. Med, doi: 10.1038/s41591-018-0092-9\nBlagosklonny MV, 2021, Oncotarget, doi:10.18632/oncotarget.28049]"},
        "safety": {"score": 3, "evidence": "Key concern as Dasatinib is a powerful chemotherapy drug; long-term effects of intermittent dosing are unknown. [References: Rad AN et al., 2024, Current Drug Metabolism, doi:10.1016/j.mad.2023.111888]"}
    },
    "Stem Cell Therapy": {
        "cost": {"score": 1, "evidence": "Prohibitively high due to specialized collection, processing, and administration. [References: Preussler et al., 2012, Biology of Blood and Marrow Transplantation (now Transplantation and Cellular Therapy), doi:10.1016/j.bbmt.2012.04.001]"},
        "human": {"score": 3, "evidence": "Well-established for hematopoietic disorders, but lacks evidence for a broad anti-aging indication. Some early trials show promise for frailty. [References: Tompkins et al., 2017, The Journals of Gerontology Series A: Biological Sciences and Medical Sciences, doi:10.1093/gerona/glx137]"},
        "conservation": {"score": 4, "evidence": "Highly conserved; stem cells play a fundamental role in tissue repair and regeneration across all complex life forms. [References: Bideau et al., 2021, Cellular and Molecular Life Sciences, doi:10.1007/s00018-021-03760-7]"},
        "healthspan": {"score": 4, "evidence": "Broad benefits; can regenerate damaged tissue, modulate the immune system, and reduce inflammation. [References: Montserrat-Vazquez et al., 2022, npj Regenerative Medicine]"},
        "lifespan": {"score": 4, "evidence": "Multiple studies collectively demonstrated that transplanting or rejuvenating stem cells (hypothalamic, hematopoietic, and mesenchymal) significantly extends lifespan. Interventions utilizing young-donor cells, senescence-resistant progenitors, or stem-cell-derived exosomes increased rodent survival by 12–28% and ameliorated physiological aging hallmarks in primates. [References: Lei et al., 2025, Cell, doi:10.1016/j.cell.2025.05.021 \nMansilla et al., 2016, Rejuvenation Research, doi:10.1089/rej.2015.1777 \nMontserrat-Vazquez et al., 2022, npj Regenerative Medicine, doi:10.1038/s41536-022-00275-y \nGuderyon et al., 2020, Aging Cell, doi:10.1111/acel.13110 \nZhang et al., 2017, Nature, doi:10.1038/nature23282 \nKovina et al., 2019, Frontiers in Genetics, doi:10.3389/fgene.2019.00310]"},
        "safety": {"score": 3, "evidence": "Key consideration; autologous cells reduce rejection risk, but the procedure still carries risks of infection and other complications. [References: Waszczuk-Gajda et al., 2022, Journal of Clinical Medicine, doi:10.3390/jcm11123541]"}
    },
    "Steroids (17α-estradiol)": {
        "cost": {"score": 3, "evidence": "Likely inexpensive to produce, but would require a prescription and monitoring. [References: Ramos et al., 2023, Anais Brasileiros de Dermatologia, doi:10.1016/j.abd.2022.09.006]"},
        "human": {"score": 1, "evidence": "Non-existent for a longevity intervention. [References: Stout et al., 2023, GeroScience, doi:10.1007/s11357-023-00767-9]"},
        "conservation": {"score": 4, "evidence": "Unique non-genomic anti-aging mechanism via membrane estrogen receptors, activating protein kinase cascades and producing epigenetic effects. [References: Arnal et al., 2017, Physiological Reviews, doi:10.1152/physrev.00024.2016]"},
        "healthspan": {"score": 3, "evidence": "Prevented age-associated sarcopenia and fat gain in male mice without feminizing side effects; improved late-life physical function. [References: Garratt et al., 2019, Aging Cell, doi:10.1111/acel.12920]"},
        "lifespan": {"score": 4, "evidence": "19% median lifespan extension in male mice in an NIA ITP study; effect was highly sex-specific. [References: Harrison et al., 2021, Aging Cell, doi:10.1111/acel.13328]"},
        "safety": {"score": 3, "evidence": "Limited safety context from topical use for hair loss; long-term systemic safety in healthy humans is largely unknown. [References: Kim et al., 2012, Annals of Dermatology, doi:10.5021/ad.2012.24.3.295]"}
    },
    "Synthetic Tissues/Organs": {
        "cost": {"score": 1, "evidence": "Prohibitively high due to complex, custom manufacturing and surgical procedures. [References: Jessop et al., 2015, Frontiers in Surgery, doi:10.3389/fsurg.2015.00052]"},
        "human": {"score": 2, "evidence": "Field is in its infancy; evidence is limited to specific applications like skin grafts and bladder augmentation. [References: Atala et al., 2006, The Lancet, doi:10.1016/S0140-6736(06)68438-9]"},
        "conservation": {"score": 3, "evidence": "Based on fundamental, conserved biological and cellular mechanisms of tissue engineering. [References: Langer et al., 1993, Science, doi:10.1126/science.8493529]"},
        "healthspan": {"score": 2, "evidence": "Potentially immense benefit, as a new organ can restore function completely lost due to disease or aging. [References: Gallico et al., 1984, The New England Journal of Medicine, doi:10.1056/NEJM198408163110706]"},
        "lifespan": {"score": 2, "evidence": "Not a preventative intervention; a therapeutic approach to restore function, so lifespan extension is not a direct endpoint. [References: Mao et al., 2015, Proceedings of the National Academy of Sciences, doi:10.1073/pnas.1508520112]"},
        "safety": {"score": 2, "evidence": "Major concern; involves complex surgery with risks of infection and rejection. [References: Kuijer et al., 2007, Biomaterials, doi:10.1016/j.biomaterials.2007.06.003]"}
    },
    "Telomere Extension Therapy": {
        "cost": {"score": 1, "evidence": "Prohibitively high; early gene therapy trials were exceptionally expensive. [References: Naddaf M, 2022, Nature (News Feature), doi:10.1038/d41586-022-04327-7]"},
        "human": {"score": 2, "evidence": "A gene therapy trial for telomere biology disorders showed sustained telomere elongation without major safety concerns. [References: Myers KC et al., 2025, NEJM Evidence, doi:10.1056/EVIDoa2400252]"},
        "conservation": {"score": 4, "evidence": "Based on a fundamental and conserved biological process involving telomeres and telomerase ensuring chromosome integrity. [References: Blackburn EH et al., 2006, Nature Medicine, doi:10.1038/nm1006-1133]"},
        "healthspan": {"score": 3, "evidence": "Modified RNA therapy increased proliferation of cultured human muscle and skin cells, \"turning back the clock\" on a cellular level. [References: Ramunas J et al., 2015, FASEB Journal, doi:10.1096/fj.14-259531]"},
        "lifespan": {"score": 2, "evidence": "Telomerase gene therapy in adult and old mice delayed aging and increased longevity by 18.5% without increasing cancer [References: Bernardes de Jesus et al., 2012, EMBO Mol Med, doi: 10.1002/emmm.201200245]"},
        "safety": {"score": 2, "evidence": "Primary concern is cancer risk, as uncontrolled telomerase expression can immortalize cells; transient modified RNA technique mitigates this risk. [References: Ramunas J et al., 2015, FASEB Journal, doi:10.1096/fj.14-259531]"}
    },
    "Xenotransplantation": {
        "cost": {"score": 1, "evidence": "Prohibitively high; a last-resort procedure requiring lifelong surveillance. [References: Anderson & Locke, 2024, Current Transplantation Reports, doi:10.1007/s40472-024-00455-3]"},
        "human": {"score": 2, "evidence": "Earliest stages; the first successful transplants of genetically modified pig kidneys into living human patients occurred in 2024. [References: Kawai et al., 2025, New England Journal of Medicine, doi:10.1056/NEJMoa2412747]"},
        "conservation": {"score": 3, "evidence": "Underlying mechanisms of organ function and immune response are conserved, but significant physiological differences exist between pigs and humans. [References: Sykes & Sachs, 2022, Nature Reviews Nephrology, doi:10.1038/s41581-022-00624-6]"},
        "healthspan": {"score": 2, "evidence": "Benefit is absolute for a person with a failing organ, potentially saving or extending a person's life. [References: Kawai et al., 2025, New England Journal of Medicine, doi:10.1056/NEJMoa2412747]"},
        "lifespan": {"score": 2, "evidence": "Not a preventative anti-aging intervention, but high potential to extend life by restoring organ function. [References: Riella, 2025, Journal of the American Society of Nephrology, doi:10.1681/ASN.0000000581]"},
        "safety": {"score": 1, "evidence": "Sizable concerns, including risk of hyperacute rejection and transmission of unknown zoonotic pathogens. [References: Fishman & Mueller, 2024, Emerging Infectious Diseases, doi:10.3201/eid3007.240273]"}
    },
    "Young Blood Plasma/Parabiosis": {
        "cost": {"score": 1, "evidence": "Expensive with questionable benefits; limited availability and regulatory restrictions. [References: Hofmann, 2018, Transfusion Medicine and Hemotherapy, doi:10.1159/000481828]"},
        "human": {"score": 2, "evidence": "A small trial in Alzheimer's patients showed some functional but no cognitive benefits; FDA cautioned against it as \"unproven\". [References: Sha et al., 2019, JAMA Neurology, doi:10.1001/jamaneurol.2018.3288]"},
        "conservation": {"score": 3, "evidence": "Age-related changes in the blood and their effects on tissues are conserved across mammals. [References: Lagunas-Rangel, 2024, npj Aging and Mechanisms of Disease, doi:10.1038/s41514-024-00166-0]"},
        "healthspan": {"score": 3, "evidence": "Early experiments suggested rejuvenation of aged tissues, but later studies showed old blood was more detrimental than young blood was beneficial. [References: Rebo et al., 2016, Nature Communications, doi:10.1038/ncomms13363]"},
        "lifespan": {"score": 3, "evidence": "Young blood exposure extended lifespan in aged rodents through plasma infusions in rats and heterochronic parabiosis in mice, with persistent epigenetic rejuvenation. [References: Chiavellini et al., 2024, The Journals of Gerontology: Series A, doi:10.1093/gerona/glae071 \nZhang et al., 2023, Nature Aging, doi:10.1038/s43587-023-00451-9]"},
        "safety": {"score": 2, "evidence": "Significant concerns, including the risk of infection and adverse immune reactions. [References: Pandey et al., 2012, Transfusion, doi:10.1111/j.1537-2995.2012.03663.x]"}
    }
}

# Interventions list
INTERVENTIONS = [
    {"name": "Autophagy Inducers (Spermidine)", "lifespan": 4, "healthspan": 4, "conservation": 5, "human": 2, "safety": 4, "cost": 4},
    {"name": "Rapamycin/mTOR Inhibitors", "lifespan": 4, "healthspan": 4, "conservation": 5, "human": 3, "safety": 3, "cost": 3},
    {"name": "SGLT2 inhibitors (Canagliflozin)", "lifespan": 3, "healthspan": 4, "conservation": 4, "human": 4, "safety": 4, "cost": 3},
    {"name": "Acarbose", "lifespan": 3, "healthspan": 4, "conservation": 4, "human": 3, "safety": 3, "cost": 5},
    {"name": "Metformin", "lifespan": 2, "healthspan": 4, "conservation": 4, "human": 3, "safety": 5, "cost": 5},
    {"name": "NAD+ Restoration (NMN/NR)", "lifespan": 1, "healthspan": 3, "conservation": 5, "human": 3, "safety": 4, "cost": 3},
    {"name": "Glutathione Precursors", "lifespan": 3, "healthspan": 3, "conservation": 4, "human": 3, "safety": 4, "cost": 4},
    {"name": "Mitochondria (Urolithin A)", "lifespan": 2, "healthspan": 4, "conservation": 4, "human": 3, "safety": 4, "cost": 3},
    {"name": "GLP-1 Receptor Agonists", "lifespan": 1, "healthspan": 4, "conservation": 4, "human": 4, "safety": 3, "cost": 2},
    {"name": "Anti-Inflammatory Therapy", "lifespan": 3, "healthspan": 3, "conservation": 4, "human": 3, "safety": 3, "cost": 4},
    {"name": "Senolytics (D+Q)", "lifespan": 1, "healthspan": 4, "conservation": 4, "human": 3, "safety": 3, "cost": 2},
    {"name": "Natural Senolytics (Fisetin)", "lifespan": 2, "healthspan": 3, "conservation": 4, "human": 2, "safety": 4, "cost": 4},
    {"name": "Gut Microbiome Modulation", "lifespan": 3, "healthspan": 3, "conservation": 4, "human": 3, "safety": 4, "cost": 4},
    {"name": "L-deprenyl", "lifespan": 3, "healthspan": 3, "conservation": 4, "human": 3, "safety": 4, "cost": 3},
    {"name": "Alpha-ketoglutarate (AKG)", "lifespan": 2, "healthspan": 3, "conservation": 4, "human": 2, "safety": 4, "cost": 4},
    {"name": "Steroids (17α-estradiol)", "lifespan": 4, "healthspan": 3, "conservation": 4, "human": 1, "safety": 3, "cost": 3},
    {"name": "Chloroquine", "lifespan": 3, "healthspan": 2, "conservation": 4, "human": 2, "safety": 2, "cost": 4},
    {"name": "Stem Cell Therapy", "lifespan": 4, "healthspan": 4, "conservation": 4, "human": 3, "safety": 3, "cost": 1},
    {"name": "Gene Therapy", "lifespan": 3, "healthspan": 3, "conservation": 4, "human": 1, "safety": 2, "cost": 1},
    {"name": "Epigenetic Reprogramming", "lifespan": 2, "healthspan": 3, "conservation": 4, "human": 1, "safety": 2, "cost": 1},
    {"name": "Chemical Reprogramming", "lifespan": 2, "healthspan": 2, "conservation": 4, "human": 1, "safety": 2, "cost": 2},
    {"name": "Telomere Extension Therapy", "lifespan": 2, "healthspan": 3, "conservation": 4, "human": 2, "safety": 2, "cost": 1},
    {"name": "Exosome Therapy", "lifespan": 2, "healthspan": 2, "conservation": 3, "human": 2, "safety": 3, "cost": 2},
    {"name": "Young Blood Plasma/Parabiosis", "lifespan": 3, "healthspan": 3, "conservation": 3, "human": 2, "safety": 2, "cost": 1},
    {"name": "Plasma Dilution/Apheresis", "lifespan": 3, "healthspan": 3, "conservation": 4, "human": 3, "safety": 3, "cost": 2},
    {"name": "Immunotherapy for Senescent Cells", "lifespan": 1, "healthspan": 2, "conservation": 4, "human": 1, "safety": 2, "cost": 1},
    {"name": "Mitochondria (Elamipretide/SS-31)", "lifespan": 2, "healthspan": 3, "conservation": 4, "human": 2, "safety": 3, "cost": 1},
    {"name": "Proteostasis & Nucleolar Function", "lifespan": 1, "healthspan": 3, "conservation": 5, "human": 1, "safety": 2, "cost": 2},
    {"name": "Xenotransplantation", "lifespan": 2, "healthspan": 2, "conservation": 3, "human": 2, "safety": 1, "cost": 1},
    {"name": "Synthetic Tissues/Organs", "lifespan": 2, "healthspan": 2, "conservation": 3, "human": 2, "safety": 2, "cost": 1}
]

# Domain names
DOMAIN_NAMES = {
    "lifespan": "Preclinical Efficacy (Lifespan)",
    "healthspan": "Preclinical Efficacy (Healthspan)",
    "conservation": "Mechanism Conservation",
    "human": "Human Trial Evidence",
    "safety": "Safety & Tolerability",
    "cost": "Cost & Accessibility"
}

# Header
st.markdown('<div class="main-header"><h1>🧬 Translational Geroscience MCDA Ranking</h1><p>Evidence-based prioritization of longevity interventions for clinical translation</p></div>', unsafe_allow_html=True)

# Instructions
st.markdown("""
### 📊 How to Use This Tool
This interactive tool ranks 30 longevity interventions across 6 key domains using Multi-Criteria Decision Analysis (MCDA).

**Adjust the weights** below to reflect different stakeholder perspectives:
- **Regulator**: High weight on safety and human evidence
- **Investor/Industry**: High weight on clinical readiness and market accessibility
- **Patient**: High weight on safety, accessibility, and proven human benefits
- **Researcher**: High weight on preclinical efficacy and mechanistic understanding
""")

# Sidebar for weights
st.sidebar.header("⚖️ Adjust Domain Weights")
st.sidebar.markdown("Modify weights to reflect different priorities (higher = more important)")

weights = {
    "lifespan": st.sidebar.slider("Lifespan Extension", 0, 10, 5, help="Impact on maximum and median lifespan in animal models"),
    "healthspan": st.sidebar.slider("Healthspan Benefits", 0, 10, 5, help="Impact on physical function, disease prevention, and quality of life"),
    "conservation": st.sidebar.slider("Mechanism Conservation", 0, 10, 4, help="How well the mechanism is conserved across species"),
    "human": st.sidebar.slider("Human Trial Evidence", 0, 10, 7, help="Quality and extent of human clinical data"),
    "safety": st.sidebar.slider("Safety & Tolerability", 0, 10, 8, help="Safety profile and side effect burden"),
    "cost": st.sidebar.slider("Cost & Accessibility", 0, 10, 6, help="Affordability and accessibility for widespread use")
}

# Preset profiles
st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Presets:**")
col1, col2 = st.sidebar.columns(2)
if col1.button("Regulator", use_container_width=True):
    weights.update({"lifespan": 3, "healthspan": 4, "conservation": 3, "human": 9, "safety": 10, "cost": 4})
if col2.button("Investor", use_container_width=True):
    weights.update({"lifespan": 4, "healthspan": 5, "conservation": 3, "human": 8, "safety": 7, "cost": 8})

col3, col4 = st.sidebar.columns(2)
if col3.button("Patient", use_container_width=True):
    weights.update({"lifespan": 5, "healthspan": 7, "conservation": 2, "human": 8, "safety": 9, "cost": 9})
if col4.button("Researcher", use_container_width=True):
    weights.update({"lifespan": 8, "healthspan": 7, "conservation": 6, "human": 5, "safety": 6, "cost": 3})

# Display current weights
st.sidebar.markdown("---")
st.sidebar.markdown("**Current Weights:**")
for domain, weight in weights.items():
    st.sidebar.metric(DOMAIN_NAMES[domain], weight)

# Main content
with st.container():
    def calculate_rankings():
        results = []
        for intervention in INTERVENTIONS:
            weighted_score = sum(intervention[domain] * weights[domain] for domain in weights.keys())
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
        
        # Calculate rank with ties
        df['Rank_Num'] = df['Weighted Score'].rank(method='min', ascending=False).astype(int)
        
        # Identify tied scores
        score_counts = df['Weighted Score'].value_counts()
        tied_scores = score_counts[score_counts > 1].index
        df['Rank'] = df['Rank_Num'].astype(str)
        df.loc[df['Weighted Score'].isin(tied_scores), 'Rank'] = df.loc[df['Weighted Score'].isin(tied_scores), 'Rank']
        
        # Reorder columns
        df = df[['Rank', 'Intervention', 'Lifespan', 'Healthspan', 'Conservation', 'Human', 'Safety', 'Cost', 'Weighted Score']]
        df = df.drop(columns=['Rank_Num'], errors='ignore')
        
        return df
    
    df_rankings = calculate_rankings()
    
    # Display table
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

# Evidence viewer in sidebar
st.sidebar.header("🔍 View Evidence")
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Click on individual scores in the table to view detailed evidence and references.</p>
    <p>Adjust weights to match your stakeholder perspective (regulator, investor, patient, or researcher).</p>
</div>
""", unsafe_allow_html=True)
