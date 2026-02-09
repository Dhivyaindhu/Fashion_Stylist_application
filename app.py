import streamlit as st
import numpy as np
from PIL import Image
import cv2
import mediapipe as mp
import requests

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    layout="centered"
)

st.title("👗 AI Virtual Fashion Stylist")
st.caption("Body-size detection • Avatar creation • Virtual try-on")

st.markdown("""
### How it works
1. Upload a **clear full-body image**
2. AI extracts body structure
3. Category & size are predicted
4. Avatar is generated
5. Clothes are recommended with links
""")

# --------------------------------------------------
# Image Upload (Pop-up style)
# --------------------------------------------------
uploaded = st.file_uploader(
    "📸 Upload a full-body image",
    type=["jpg", "jpeg", "png"]
)

if uploaded is None:
    st.info("⬆️ Upload an image to begin")
    st.stop()

# --------------------------------------------------
# Load Image
# --------------------------------------------------
image = Image.open(uploaded).convert("RGB")
image_np = np.array(image)

st.image(image, caption="Uploaded Image", width=280)

# --------------------------------------------------
# Pose Detection (MediaPipe)
# --------------------------------------------------
@st.cache_resource
def load_pose_model():
    return mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False
    )

pose = load_pose_model()

with st.spinner("🔍 Detecting body pose..."):
    result = pose.process(image_np)

if not result.pose_landmarks:
    st.error("❌ Full body not detected. Try another image.")
    st.stop()

landmarks = result.pose_landmarks.landmark

# --------------------------------------------------
# Body Measurements (Normalized)
# --------------------------------------------------
def extract_measurements(lm):
    shoulder = abs(lm[11].x - lm[12].x)
    hip = abs(lm[23].x - lm[24].x)
    height = abs(lm[0].y - lm[27].y)
    waist_ratio = hip / (shoulder + 1e-6)

    return {
        "shoulder": round(shoulder, 3),
        "hip": round(hip, 3),
        "height": round(height, 3),
        "waist_ratio": round(waist_ratio, 3)
    }

measurements = extract_measurements(landmarks)

# --------------------------------------------------
# Classification (FIXED CHILD LOGIC)
# --------------------------------------------------
def classify_person(measurements):
    height = measurements["height"]
    waist = measurements["waist_ratio"]

    if height < 0.55:
        category = "Kids"
        size = "S"
    elif waist < 0.85:
        category = "Men"
        size = "M" if height < 0.75 else "L"
    else:
        category = "Women"
        size = "M"

    return category, size

category, size = classify_person(measurements)

# --------------------------------------------------
# Results
# --------------------------------------------------
st.success("✅ Analysis Complete")

c1, c2 = st.columns(2)
c1.metric("Category", category)
c2.metric("Size", size)

st.subheader("📏 Measurements")
st.json(measurements)

# --------------------------------------------------
# Avatar Generation (Cartoon / Toy-like)
# --------------------------------------------------
def generate_avatar(img):
    avatar = cv2.resize(img, (256, 512))
    avatar = cv2.GaussianBlur(avatar, (15, 15), 0)
    return avatar

avatar = generate_avatar(image_np)

st.subheader("🧍 Generated Avatar")
st.image(avatar, width=260)

# --------------------------------------------------
# Virtual Try-On (2D Overlay Demo)
# --------------------------------------------------
def apply_tryon(avatar, category):
    overlay = avatar.copy()

    color = (255, 200, 200) if category == "Women" else (200, 200, 255)
    cv2.rectangle(overlay, (60, 180), (200, 320), color, -1)

    blended = cv2.addWeighted(overlay, 0.4, avatar, 0.6, 0)
    return blended

tryon = apply_tryon(avatar, category)

st.subheader("👕 Virtual Try-On (Demo)")
st.image(tryon, width=260)

# --------------------------------------------------
# Outfit Recommendations (Multi-Website)
# --------------------------------------------------
st.subheader("🛒 Recommended Outfits")

def recommend(category, size):
    if category == "Kids":
        return [
            ("Kids Hoodie", "Myntra", "https://www.myntra.com"),
            ("Kids Jeans", "Amazon", "https://www.amazon.in")
        ]
    if category == "Men":
        return [
            ("Casual Shirt", "Flipkart", "https://www.flipkart.com"),
            ("T-Shirt", "Myntra", "https://www.myntra.com"),
            ("Jeans", "Amazon", "https://www.amazon.in")
        ]
    return [
        ("Kurti", "Myntra", "https://www.myntra.com"),
        ("Dress", "Amazon", "https://www.amazon.in"),
        ("Top", "Flipkart", "https://www.flipkart.com")
    ]

items = recommend(category, size)
cols = st.columns(len(items))

for col, (name, site, url) in zip(cols, items):
    with col:
        st.image(f"https://via.placeholder.com/180x240.png?text={name}")
        st.markdown(f"**{name}**")
        st.markdown(f"[🛒 Buy on {site}]({url})")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("🚀 AI Virtual Fashion Stylist | Streamlit Cloud Ready")
