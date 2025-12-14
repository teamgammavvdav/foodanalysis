import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import zxingcpp
from streamlit_lottie import st_lottie

# --- 1. APP CONFIGURATION & "NEON GLASS" UI ---
st.set_page_config(page_title="BioScan Ultra", layout="wide", page_icon="🧬")

st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        color: #e0e0e0;
    }
    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    /* Text Highlights */
    .highlight-red { color: #ff4b4b; font-weight: bold; text-shadow: 0 0 10px rgba(255, 75, 75, 0.5); }
    .highlight-green { color: #00ff7f; font-weight: bold; text-shadow: 0 0 10px rgba(0, 255, 127, 0.5); }
    .big-stat { font-size: 2rem; font-weight: 800; margin: 0; }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. EXPANDED TOXIC DATABASE ---
RISKY_ADDITIVES = {
    'e250': {'name': 'Sodium Nitrite', 'risk': 'Critical', 'desc': 'Carcinogenic link (colon cancer). Used in bacon/ham.'},
    'e251': {'name': 'Sodium Nitrate', 'risk': 'Critical', 'desc': 'Damages blood vessels; heart disease risk.'},
    'e211': {'name': 'Sodium Benzoate', 'risk': 'High', 'desc': 'Can damage DNA mitochondria; hyperactivity.'},
    'e621': {'name': 'MSG', 'risk': 'Moderate', 'desc': 'Excitotoxin; overstimulates brain cells.'},
    'e951': {'name': 'Aspartame', 'risk': 'High', 'desc': 'Breakdown products (methanol) are toxic; debated carcinogen.'},
    'e133': {'name': 'Blue 1', 'risk': 'Moderate', 'desc': 'Banned in Norway/Finland/France; hypersensitivity.'},
    'e171': {'name': 'Titanium Dioxide', 'risk': 'Critical', 'desc': 'Nanoparticles accumulate in organs; DNA damage.'},
    'e102': {'name': 'Yellow 5 (Tartrazine)', 'risk': 'High', 'desc': 'Genotoxic; thyroid tumors in animals.'},
    'e320': {'name': 'BHA', 'risk': 'Critical', 'desc': 'Endocrine disruptor; specifically targets hormones.'},
    'e150d': {'name': 'Caramel IV', 'risk': 'High', 'desc': 'Contains 4-MEI (Carcinogen).'},
    'e924': {'name': 'Potassium Bromate', 'risk': 'Critical', 'desc': 'Banned in EU/Canada; Kidney damage & Cancer.'},
    'e950': {'name': 'Acesulfame K', 'risk': 'Moderate', 'desc': 'Contains Methylene Chloride (carcinogen) residues.'}
}

# --- 3. HELPER FUNCTIONS ---

def load_lottie(url):
    try:
        return requests.get(url).json()
    except:
        return None

lottie_dna = load_lottie("https://lottie.host/5a8b2746-6019-470a-995a-049d53cb1639/F0w4z4td6u.json")

def fetch_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        data = requests.get(url, headers={"User-Agent": "BioScanUltra/3.0"}).json()
        return data.get('product') if data.get('status') == 1 else None
    except:
        return None

def create_gauge(value, title, max_val, color_steps):
    """Creates a visually stunning gauge chart."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 24, 'color': "white"}},
        number = {'suffix': "g", 'font': {'color': "white"}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "white", 'thickness': 0.2},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': color_steps
        }
    ))
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Arial"}, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- 4. MAIN APP LOGIC ---

c1, c2 = st.columns([1, 5])
with c1:
    if lottie_dna: st_lottie(lottie_dna, height=100, key="dna")
with c2:
    st.title("BioScan ULTRA")
    st.markdown("*Advanced Food Toxicology & Nutrient Analysis*")

# --- INPUT TABS ---
tab1, tab2 = st.tabs(["📸 LIVE SCAN", "#️⃣ MANUAL ID"])
barcode = None

with tab1:
    col_cam, col_info = st.columns([2, 1])
    with col_cam:
        img_input = st.camera_input("Scan Barcode")
    with col_info:
        st.info("💡 **Pro Tip:** Ensure the barcode is flat and well-lit. Works best on mobile.")

    if img_input:
        try:
            results = zxingcpp.read_barcodes(Image.open(img_input))
            if results:
                barcode = results[0].text
                st.success(f"ID Locked: {barcode}")
        except:
            st.warning("Scan failed. Try Manual ID.")

with tab2:
    manual = st.text_input("Enter Digits:", value="5449000000996")
    if st.button("Search Database"):
        barcode = manual

# --- 5. RESULTS DASHBOARD ---

if barcode:
    with st.spinner("⚠️ Analyzing molecular structure..."):
        data = fetch_data(barcode)

    if data:
        nutriments = data.get('nutriments', {})
        st.markdown("---")

        # --- HERO SECTION ---
        hero1, hero2 = st.columns([1, 2])
        with hero1:
            if 'image_front_url' in data:
                st.image(data['image_front_url'], width=200)
                st.caption(f"Brand: {data.get('brands','Unknown')}")
        
        with hero2:
            st.markdown(f"## {data.get('product_name', 'Unknown')}")
            
            # Score Cards
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                score = data.get('nutriscore_grade', '?').upper()
                color = "green" if score in ['A','B'] else "red"
                st.markdown(f"Nutri-Score<br><span class='big-stat' style='color:{color}'>{score}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with sc2:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                nova = data.get('nova_group', '?')
                st.markdown(f"Processing (NOVA)<br><span class='big-stat'>{nova}</span>/4", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with sc3:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                cal = nutriments.get('energy-kcal_100g', 0)
                st.markdown(f"Calories<br><span class='big-stat'>{cal}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # --- GRAPHICS ROW 1: THE DANGER GAUGES ---
        st.subheader("⚠️ Toxicity & Overdose Meters")
        g1, g2, g3 = st.columns(3)
        
        with g1:
            # Sugar Gauge (Max 50g)
            fig_sugar = create_gauge(nutriments.get('sugars_100g', 0), "Sugar", 50, 
                [{'range': [0, 5], 'color': "#00ff7f"}, {'range': [5, 22], 'color': "#ffa500"}, {'range': [22, 50], 'color': "#ff4b4b"}])
            st.plotly_chart(fig_sugar, use_container_width=True)
            
        with g2:
            # Salt Gauge (Max 3g)
            fig_salt = create_gauge(nutriments.get('salt_100g', 0), "Salt", 3, 
                [{'range': [0, 0.5], 'color': "#00ff7f"}, {'range': [0.5, 1.5], 'color': "#ffa500"}, {'range': [1.5, 3], 'color': "#ff4b4b"}])
            st.plotly_chart(fig_salt, use_container_width=True)

        with g3:
            # Fat Gauge (Max 20g Sat Fat)
            fig_fat = create_gauge(nutriments.get('saturated-fat_100g', 0), "Sat. Fat", 20, 
                [{'range': [0, 1.5], 'color': "#00ff7f"}, {'range': [1.5, 5], 'color': "#ffa500"}, {'range': [5, 20], 'color': "#ff4b4b"}])
            st.plotly_chart(fig_fat, use_container_width=True)

        # --- GRAPHICS ROW 2: MACRO SUNBURST ---
        st.subheader("📊 Caloric Breakdown")
        
        # Prepare Data for Sunburst
        labels = ['Carbs', 'Sugars', 'Starches', 'Fat', 'Saturated', 'Unsaturated', 'Protein', 'Salt']
        parents = ['', 'Carbs', 'Carbs', '', 'Fat', 'Fat', '', '']
        values = [
            nutriments.get('carbohydrates_100g', 0), nutriments.get('sugars_100g', 0), 
            nutriments.get('carbohydrates_100g', 0) - nutriments.get('sugars_100g', 0),
            nutriments.get('fat_100g', 0), nutriments.get('saturated-fat_100g', 0),
            nutriments.get('fat_100g', 0) - nutriments.get('saturated-fat_100g', 0),
            nutriments.get('proteins_100g', 0), nutriments.get('salt_100g', 0)
        ]
        
        # Fix negative values if data is missing
        values = [v if v > 0 else 0 for v in values]

        fig_sun = go.Figure(go.Sunburst(
            labels=labels, parents=parents, values=values, branchvalues="total",
            marker=dict(colors=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"])
        ))
        fig_sun.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sun, use_container_width=True)

        # --- DEEP INGREDIENT ANALYSIS ---
        st.subheader("🧬 Chemical Inspection")
        
        col_tox, col_list = st.columns([1, 1])
        
        with col_tox:
            st.markdown("#### 🚫 Detected Contaminants")
            additives = [t.split(':')[-1] for t in data.get('additives_tags', [])]
            found_risks = []
            
            for tag in additives:
                if tag in RISKY_ADDITIVES:
                    found_risks.append(RISKY_ADDITIVES[tag])
            
            if found_risks:
                for risk in found_risks:
                    st.markdown(f"""
                    <div class='glass-card' style='border-left: 5px solid #ff4b4b;'>
                        <h4 style='color: #ff4b4b;'>{risk['name']} ({risk['risk']} Risk)</h4>
                        <p>{risk['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No High-Risk Industrial Additives Detected.")
                
            # Palm Oil Check
            if data.get('ingredients_from_palm_oil_n', 0) > 0:
                st.warning("⚠️ Contains Palm Oil (Environmental & Heart Health Risk)")

        with col_list:
            st.markdown("#### 📝 Full Ingredient List")
            text = data.get('ingredients_text', 'Not Available').replace('_', '')
            st.text_area("Scroll to read:", value=text, height=300)
            
            # Allergens
            allergens = data.get('allergens', '').replace('en:', '')
            if allergens:
                st.markdown(f"**🤧 Allergens:** <span style='color:#ffa500'>{allergens}</span>", unsafe_allow_html=True)

    else:
        st.error("Product not found in global database.")