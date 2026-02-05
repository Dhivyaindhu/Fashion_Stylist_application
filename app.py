import streamlit as st
import numpy as np
from PIL import Image

from utils import extract_body_features
from model import build_model, predict_size

# Page config
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    layout="centered"
)

st.title("👗 AI-Based Virtual Fashion Stylist")

st.write(
    "Upload a **clear full-body image** to estimate body size "
    "and get dress recommendations."
)

# Image uploader
uploaded = st.file_uploader(
    "Upload a full-body image",
    type=["jpg", "png", "jpeg"]
)

# Build demo CNN model
model = build_model()

if uploaded is not None:
    # Load and convert image
    image = Image.open(uploaded).convert("RGB")
    img_np = np.array(image)

    # Show uploaded image
    st.image(image, caption="Uploaded Image", width=300)

    # Extract body features using MediaPipe
    features = extract_body_features(img_np)

    if features is None:
        st.error(
            "❌ No full body detected.\n\n"
            "Please upload a clear full-body image "
            "with the person fully visible."
        )
    else:
        # Predict clothing size
        size = predict_size(model, features)

        st.success(f"✅ Estimated Clothing Size: **{size}**")

        # Recommendations
        st.subheader("👕 Recommended Dresses")

        if size in ["S", "M"]:
            st.image(
                "https://i.imgur.com/JQ9pRoF.png",
                caption="Casual Dress (Recommended)",
                width=200
            )
            st.markdown("🛒 [Buy on Myntra](https://www.myntra.com)")
        else:
            st.image(
                "https://i.imgur.com/8Km9tLL.png",
                caption="Relaxed Fit Outfit (Recommended)",
                width=200
            )
            st.markdown("🛒 [Buy on Amazon](https://www.amazon.in)")
