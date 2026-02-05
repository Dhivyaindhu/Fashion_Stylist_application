import streamlit as st
import cv2
import numpy as np
from PIL import Image

from utils import extract_body_features
from model import build_model, predict_size

st.set_page_config(page_title="AI Virtual Fashion Stylist", layout="centered")
st.title("👗 AI-Based Virtual Fashion Stylist")

uploaded = st.file_uploader("Upload a full-body image", type=["jpg","png","jpeg"])

model = build_model()  # demo model

if uploaded:
    image = Image.open(uploaded)
    img_np = np.array(image)

    st.image(image, caption="Uploaded Image", width=300)

    features = extract_body_features(img_np)

    if features is None:
        st.error("No full body detected. Please upload a clear image.")
    else:
        size = predict_size(model, features)

        st.success(f"✅ Estimated Clothing Size: {size}")

        st.subheader("Recommended Dresses")
        if size in ["S", "M"]:
            st.image("https://i.imgur.com/JQ9pRoF.png", width=200)
            st.markdown("[Buy on Myntra](https://www.myntra.com)")
        else:
            st.image("https://i.imgur.com/8Km9tLL.png", width=200)
            st.markdown("[Buy on Amazon](https://www.amazon.in)")
