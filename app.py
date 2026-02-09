import streamlit as st
import numpy as np
from PIL import Image
import cv2

# ---- Your internal modules ----
from core.pose import detect_pose
from core.measurements import extract_body_measurements
from core.classifier import classify_person
from core.avatar import generate_avatar
from core.tryon import apply_tryon
from utils.recommendations import recommend_clothes

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    layout="centered"
)

st.title("👗 AI Virtual Fashion Stylist")
st.caption("Instant body-size detection & virtual try-on")

st.markdown("""
### How it works
1. Upload a **full-body image**
2. AI detects body structure
3. Avatar + size are generated
4. Clothes are recommended
5. Virtual try-on preview shown
""")

# --------------------------------------------------
# Image Upload (POP-UP)
# --------------------------------------------------
uploaded = st.file_uploader(
    "📸 Upload a clear full-body image",
    type=["jpg", "jpeg", "png"]
)

if uploaded is None:
    st.info("⬆️ Please upload an image to begin.")
    st.stop()

# --------------------------------------------------
# Load Image
# --------------------------------------------------
image = Image.open(uploaded).convert("RGB")
image_np = np.array(image)

st.image(image, caption="Uploaded Image", width=280)

# --------------------------------------------------
# Pose Detection
# --------------------------------------------------
with st.spinner("🔍 Detecting body pose..."):
    landmarks = detect_pose(image_np)

if landmarks is None:
    st.error("❌ Full body not detected. Try another image.")
    st.stop()

# --------------------------------------------------
# Measurements & Classification
# --------------------------------------------------
measurements = extract_body_measurements(landmarks)
category, size = classify_person(measurements)

st.success("✅ Analysis Complete")

col1, col2 = st.columns(2)
col1.metric("Category", category)
col2.metric("Size", size)

st.subheader("📏 Body Measurements")
st.json(measurements)

# --------------------------------------------------
# Avatar Generation
# --------------------------------------------------
st.subheader("🧍 Generated Avatar")

avatar = generate_avatar(image_np)
st.image(avatar, width=260)

# --------------------------------------------------
# Virtual Try-On
# --------------------------------------------------
st.subheader("👕 Virtual Try-On")

tryon_img = apply_tryon(avatar, category)
st.image(tryon_img, width=260)

# --------------------------------------------------
# Outfit Recommendations
# --------------------------------------------------
st.subheader("🛒 Recommended Outfits")

items = recommend_clothes(category, size)

cols = st.columns(len(items))

for col, item in zip(cols, items):
    with col:
        st.image(item["image"], width=180)
        st.markdown(f"**{item['name']}**")
        st.markdown(f"[Buy on {item['site']}]({item['url']})")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("🚀 AI Virtual Fashion Stylist | Streamlit Deployment")
