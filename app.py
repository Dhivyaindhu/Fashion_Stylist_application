import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import mediapipe as mp

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    layout="centered"
)

st.title("👗 AI Virtual Fashion Stylist")
st.caption("Efficient body-size detection & virtual try-on")

st.markdown("""
### How it works
1. Upload a **full-body image**
2. AI detects pose using MediaPipe
3. Category & size are predicted
4. Avatar is generated
5. Outfit recommendations shown
""")

# --------------------------------------------------
# Image Upload (Popup)
# --------------------------------------------------
uploaded = st.file_uploader(
    "📸 Upload a clear full-body image",
    type=["jpg", "jpeg", "png"]
)

if uploaded is None:
    st.info("⬆️ Upload an image to continue")
    st.stop()

image = Image.open(uploaded).convert("RGB")
st.image(image, caption="Uploaded Image", width=280)

image_np = np.array(image)

# --------------------------------------------------
# Pose Detection (MediaPipe)
# --------------------------------------------------
@st.cache_resource
def load_pose():
    return mp.solutions.pose.Pose(static_image_mode=True)

pose = load_pose()

with st.spinner("🔍 Detecting body pose..."):
    results = pose.process(image_np)

if not results.pose_landmarks:
    st.error("❌ Full body not detected. Please try another image.")
    st.stop()

landmarks = results.pose_landmarks.landmark

# --------------------------------------------------
# Body Measurements
# --------------------------------------------------
def extract_measurements(lm):
    shoulder = abs(lm[11].x - lm[12].x)
    hip = abs(lm[23].x - lm[24].x)
    height = abs(lm[0].y - lm[27].y)

    return {
        "shoulder_width": round(shoulder, 3),
        "hip_width": round(hip, 3),
        "height_ratio": round(height, 3)
    }

measurements = extract_measurements(landmarks)

# --------------------------------------------------
# Classification
# --------------------------------------------------
def classify_person(m):
    if m["height_ratio"] < 0.55:
        return "Kids", "S"
    elif m["shoulder_width"] > m["hip_width"]:
        return "Men", "M"
    else:
        return "Women", "M"

category, size = classify_person(measurements)

# --------------------------------------------------
# Results
# --------------------------------------------------
st.success("✅ Analysis Complete")

c1, c2 = st.columns(2)
c1.metric("Category", category)
c2.metric("Size", size)

st.subheader("📏 Body Measurements")
st.json(measurements)

# --------------------------------------------------
# Avatar Generation (PIL)
# --------------------------------------------------
def generate_avatar(img):
    avatar = img.resize((260, 520))
    return avatar

avatar = generate_avatar(image)

st.subheader("🧍 Generated Avatar")
st.image(avatar, width=260)

# --------------------------------------------------
# Virtual Try-On (Overlay Simulation)
# --------------------------------------------------
def virtual_tryon(avatar, category):
    overlay = avatar.copy()
    draw = ImageDraw.Draw(overlay)

    color = (255, 180, 200, 120) if category == "Women" else (180, 200, 255, 120)
    draw.rectangle([60, 200, 200, 350], fill=color)

    return overlay

tryon_img = virtual_tryon(avatar, category)

st.subheader("👕 Virtual Try-On (Demo)")
st.image(tryon_img, width=260)

# --------------------------------------------------
# Outfit Recommendations
# --------------------------------------------------
st.subheader("🛒 Recommended Outfits")

def recommend(category):
    if category == "Kids":
        return [
            ("Kids Hoodie", "https://www.myntra.com"),
            ("Kids Jeans", "https://www.amazon.in")
        ]
    if category == "Men":
        return [
            ("Casual Shirt", "https://www.flipkart.com"),
            ("T-Shirt", "https://www.myntra.com"),
            ("Jeans", "https://www.amazon.in")
        ]
    return [
        ("Kurti", "https://www.myntra.com"),
        ("Dress", "https://www.amazon.in"),
        ("Top", "https://www.flipkart.com")
    ]

items = recommend(category)
cols = st.columns(len(items))

for col, (name, link) in zip(cols, items):
    with col:
        st.image(f"https://via.placeholder.com/180x240.png?text={name}")
        st.markdown(f"**{name}**")
        st.markdown(f"[🛒 Buy Now]({link})")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("🚀 AI Virtual Fashion Stylist | Streamlit Cloud Compatible")
