import streamlit as st
import json
from PIL import Image
import time
import os

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    layout="centered"
)

st.title("👗 AI Virtual Fashion Stylist")
st.caption("Avatar-based size detection & fashion recommendations")

st.markdown(
    """
    **How it works**
    1. Upload your photo in Colab
    2. AI creates avatar + size + category
    3. Results are shown here with virtual try-on
    """
)

# --------------------------------------------------
# Load AI Output (from Colab)
# --------------------------------------------------
RESULT_FILE = "result.json"
AVATAR_FOLDER = "avatars"

if not os.path.exists(RESULT_FILE):
    st.warning("⚠️ AI results not found. Please run the Colab model first.")
    st.stop()

with open(RESULT_FILE, "r") as f:
    data = json.load(f)

category = data["category"]
size = data["size"]
age = data["age"]
measurements = data["measurements"]

# --------------------------------------------------
# Display Results
# --------------------------------------------------
st.success("✅ Analysis Complete")

col1, col2 = st.columns(2)

with col1:
    st.metric("Category", category)
    st.metric("Size", size)

with col2:
    st.metric("Age", age)

st.subheader("📏 Body Measurements")
st.json(measurements)

# --------------------------------------------------
# Show Avatar
# --------------------------------------------------
st.subheader("🧍 Your AI Avatar")

frames = sorted([
    f for f in os.listdir(AVATAR_FOLDER)
    if f.endswith(".png")
])

if not frames:
    st.error("Avatar images not found.")
    st.stop()

avatar_placeholder = st.empty()

for frame in frames:
    img = Image.open(os.path.join(AVATAR_FOLDER, frame))
    avatar_placeholder.image(img, width=300)
    time.sleep(0.08)

# --------------------------------------------------
# Outfit Recommendations
# --------------------------------------------------
st.subheader("👕 Recommended Outfits")

def recommend(category, size):
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

    if category == "Women":
        return [
            ("Kurti", "https://www.myntra.com"),
            ("Dress", "https://www.amazon.in"),
            ("Top", "https://www.flipkart.com")
        ]

    return []

items = recommend(category, size)

cols = st.columns(len(items))

for col, (name, link) in zip(cols, items):
    with col:
        st.image("https://via.placeholder.com/200x260.png?text=" + name)
        st.markdown(f"**{name}**")
        st.markdown(f"[🛒 Buy Now]({link})")

# --------------------------------------------------
# Virtual Try-On (Concept)
# --------------------------------------------------
st.subheader("👗 Virtual Try-On (Demo)")
st.info("Outfits can be overlaid on the avatar in the next phase (OpenCV / 3D).")

st.image(
    Image.open(os.path.join(AVATAR_FOLDER, frames[0])),
    caption="Avatar base for try-on",
    width=300
)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("🚀 Powered by AI | Built with Streamlit")
