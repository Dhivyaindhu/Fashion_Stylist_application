import streamlit as st
import numpy as np
from PIL import Image

# --------------------------------------------------
# SAFE IMPORTS (Prevents Cloud Crash)
# --------------------------------------------------
try:
    import cv2
except Exception as e:
    st.error("OpenCV not available. Check requirements.txt")
    st.stop()

# ---- Internal Modules ----
from core.pose import detect_pose
from core.measurements import extract_body_measurements
from core.classifier import classify_person
from core.avatar import generate_avatar
from core.tryon import apply_tryon
from utils.recommendations import recommend_clothes

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("👗 AI Virtual Fashion Stylist")
st.caption("Automatic body-size detection & multi-site fashion recommendations")

# --------------------------------------------------
# USER GUIDE
# --------------------------------------------------
st.markdown("""
### How it works
1. Upload a **full-body photo**
2. AI extracts body structure
3. Size & category detected
4. Clothes recommended from **multiple websites**
5. Virtual try-on preview shown
""")

# --------------------------------------------------
# IMAGE UPLOAD (STATIC-LIKE POPUP)
# --------------------------------------------------
uploaded = st.file_uploader(
    "📸 Upload a clear full-body image",
    type=["jpg", "jpeg", "png"]
)

if uploaded is None:
    st.info("⬆️ Upload an image to start the analysis.")
    st.stop()

# --------------------------------------------------
# LOAD IMAGE
# --------------------------------------------------
image = Image.open(uploaded).convert("RGB")
image_np = np.array(image)

st.image(image, caption="Uploaded Image", width=300)

# --------------------------------------------------
# CACHED AI PIPELINE (EFFICIENCY PROOF)
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def run_pose_detection(img):
    return detect_pose(img)

@st.cache_data(show_spinner=False)
def run_measurements(landmarks):
    return extract_body_measurements(landmarks)

@st.cache_data(show_spinner=False)
def run_classification(measurements):
    return classify_person(measurements)

@st.cache_data(show_spinner=False)
def run_avatar(img):
    return generate_avatar(img)

# --------------------------------------------------
# POSE DETECTION
# --------------------------------------------------
with st.spinner("🔍 Detecting body pose..."):
    landmarks = run_pose_detection(image_np)

if landmarks is None:
    st.error("❌ Full body not detected. Please upload another image.")
    st.stop()

# --------------------------------------------------
# MEASUREMENTS & CLASSIFICATION
# --------------------------------------------------
measurements = run_measurements(landmarks)
category, size = run_classification(measurements)

st.success("✅ Analysis completed")

col1, col2 = st.columns(2)
col1.metric("Category", category)
col2.metric("Recommended Size", size)

with st.expander("📏 View Body Measurements"):
    st.json(measurements)

# --------------------------------------------------
# AVATAR GENERATION
# --------------------------------------------------
st.subheader("🧍 AI-Generated Avatar")

avatar = run_avatar(image_np)
st.image(avatar, width=260)

# --------------------------------------------------
# VIRTUAL TRY-ON
# --------------------------------------------------
st.subheader("👕 Virtual Try-On Preview")

tryon_img = apply_tryon(avatar, category)
st.image(tryon_img, width=260)

# --------------------------------------------------
# MULTI-SITE OUTFIT RECOMMENDATIONS
# --------------------------------------------------
st.subheader("🛒 Outfit Recommendations")

items = recommend_clothes(category, size)

if not items:
    st.warning("No recommendations found.")
else:
    cols = st.columns(min(len(items), 3))
    for col, item in zip(cols, items):
        with col:
            st.image(item["image"], width=180)
            st.markdown(f"**{item['name']}**")
            st.markdown(f"🛍️ {item['site']}")
            st.link_button("Buy Now", item["url"])

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("🚀 AI Virtual Fashion Stylist | Static & Efficient Streamlit App")
