import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io
import math

st.set_page_config(page_title="3D Fashion Stylist Pro", page_icon="🧸", layout="wide")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }
.main-header {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
padding: 3rem; border-radius: 20px; color: white;
text-align: center; margin-bottom: 2rem;
}
.body-type-card {
background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
padding: 2rem; border-radius: 15px;
border: 3px solid #2196f3; margin: 1rem 0;
}
.measurement-grid {
display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
gap: 1rem; margin: 1.5rem 0;
}
.measure-item {
background: white; padding: 1.2rem; border-radius: 10px;
border-left: 4px solid #667eea; text-align: center;
}
.fit-analysis {
background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
padding: 2rem; border-radius: 15px;
border: 3px solid #ffc107; margin: 1.5rem 0;
}
.product-card {
background: white; border: 3px solid #e0e0e0;
border-radius: 15px; padding: 1.5rem; text-align: center;
transition: all 0.4s; cursor: pointer; height: 100%;
}
.product-card:hover {
transform: translateY(-10px);
box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
}
.stButton>button {
width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white; border-radius: 12px; padding: 0.9rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🧸 3D Fashion Stylist Pro</h1><p style="font-size: 1.3rem;">Body Type Analysis • Fit Prediction • 3D Try-On</p></div>', unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
for key in ['selected_dress', 'user_category', 'size', 'skin_tone', 'toy_mannequin',
            'ref_points', 'rotation_angle', 'measurements', 'body_type', 'fit_prediction']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.rotation_angle is None:
    st.session_state.rotation_angle = 0

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("✨ Features")
    st.success("""
📊 Body Type Analysis  
📏 Complete Measurements  
✅ Fit Prediction  
🛍️ Smart Recommendations  
""")

# ---------------- UPLOAD ----------------
st.markdown("## 📤 Upload Photo")
uploaded = st.file_uploader("Upload full-body photo", type=["jpg", "jpeg", "png"])

if not uploaded:
    st.info("👆 Upload photo to analyze body type!")
    st.stop()

# ---------------- CATEGORY ----------------
st.markdown("---")
st.markdown("## 🎯 Select Category")

cat_cols = st.columns(3)
with cat_cols[0]:
    if st.button("👶 KIDS", use_container_width=True):
        st.session_state.user_category = "Kids"
        st.rerun()
with cat_cols[1]:
    if st.button("👨 MEN", use_container_width=True):
        st.session_state.user_category = "Men"
        st.rerun()
with cat_cols[2]:
    if st.button("👩 WOMEN", use_container_width=True):
        st.session_state.user_category = "Women"
        st.rerun()

if not st.session_state.user_category:
    st.warning("⚠️ Select category!")
    st.stop()

category = st.session_state.user_category

# ---------------- ANALYSIS ----------------
original = Image.open(uploaded).convert("RGB")
img_array = np.array(original)
img_w, img_h = original.size

gray = np.mean(img_array, axis=2)
threshold = np.percentile(gray, 25)
body_mask = gray > threshold

rows = np.any(body_mask, axis=1)
cols = np.any(body_mask, axis=0)

rmin, rmax = np.where(rows)[0][[0, -1]]
cmin, cmax = np.where(cols)[0][[0, -1]]

body_h = rmax - rmin
body_w = cmax - cmin

avg_height_cm = 162 if category == "Women" else (175 if category == "Men" else 120)
px_to_cm = avg_height_cm / body_h

measurements = {
    "height_cm": round(body_h * px_to_cm, 1),
    "shoulder_cm": round(body_w * 0.42 * px_to_cm, 1),
    "waist_cm": round(body_w * 0.38 * px_to_cm, 1),
    "hip_cm": round(body_w * 0.44 * px_to_cm, 1),
    "shoulder_hip_ratio": 0.42 / 0.44,
    "waist_hip_ratio": 0.38 / 0.44
}

st.session_state.measurements = measurements

# ---------------- SIZE ----------------
if category == "Kids":
    size = "4-6Y" if body_h < img_h * 0.5 else "7-9Y"
elif category == "Men":
    size = "M" if body_w < img_w * 0.45 else "L"
else:
    size = "S" if body_w < img_w * 0.4 else "M"

st.session_state.size = size

# ---------------- SKIN TONE ----------------
brightness = np.mean(img_array[rmin:rmin+int(body_h*0.25), cmin:cmax])
skin_tone = "Fair" if brightness > 210 else "Medium" if brightness > 150 else "Deep"
st.session_state.skin_tone = skin_tone

# ==========================================================
# 🔥 ADDED SECTION — PRODUCT RECOMMENDATIONS (ONLY NEW CODE)
# ==========================================================

st.markdown("---")
st.markdown("## 🛍️ Recommended Dresses For You")

SKIN_COLORS = {
    "Fair": ["Pastel Pink", "Lavender", "Mint"],
    "Medium": ["Royal Blue", "Emerald", "Mustard"],
    "Deep": ["White", "Gold", "Cobalt"]
}

PRODUCTS = [
    {"title": "A-Line Dress", "category": "Women", "color": "Royal Blue",
     "sizes": ["S", "M", "L"], "platform": "Amazon",
     "image": "https://m.media-amazon.com/images/I/71vXK0p9nFL.jpg",
     "link": "https://www.amazon.in/"},
    {"title": "Wrap Dress", "category": "Women", "color": "Emerald",
     "sizes": ["M", "L"], "platform": "Flipkart",
     "image": "https://rukminim2.flixcart.com/image/832/832/xif0q/dress.jpeg",
     "link": "https://www.flipkart.com/"},
    {"title": "Casual Shirt", "category": "Men", "color": "Cobalt",
     "sizes": ["M", "L"], "platform": "Amazon",
     "image": "https://m.media-amazon.com/images/I/61lH1Yv4ZEL.jpg",
     "link": "https://www.amazon.in/"}
]

allowed = SKIN_COLORS.get(st.session_state.skin_tone, [])
recommendations = [
    p for p in PRODUCTS
    if p["category"] == category
    and size in p["sizes"]
    and p["color"] in allowed
]

if recommendations:
    cols = st.columns(3)
    for i, p in enumerate(recommendations):
        with cols[i % 3]:
            st.image(p["image"], use_container_width=True)
            st.markdown(f"**{p['title']}**")
            st.markdown(f"🎨 {p['color']}")
            st.markdown(f"📏 Size: {size}")
            st.markdown(f"🛒 {p['platform']}")
            st.link_button("🔗 View Product", p["link"])
else:
    st.info("No exact matches found. Try another style.")

# ==========================================================
# 🔥 END OF ADDED SECTION
# ==========================================================

# ---------------- UPLOAD DRESS ----------------
st.markdown("---")
st.markdown("## 👗 Upload Dress Image")

uploaded_dress = st.file_uploader("Upload dress to try on", type=["jpg", "jpeg", "png"])

if uploaded_dress:
    st.image(uploaded_dress, use_container_width=True)
    st.success("✅ Dress uploaded successfully!")

st.markdown("---")
st.markdown('<div style="text-align:center;padding:2rem;background:#667eea;color:white;border-radius:15px;">'
            '<h2>🧸 3D Fashion Stylist Pro</h2>'
            '<p>Body Type Analysis • Fit Prediction • Virtual Try-On</p></div>',
            unsafe_allow_html=True)
