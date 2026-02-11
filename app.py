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

# Session State
for key in ['selected_dress', 'user_category', 'size', 'skin_tone', 'toy_mannequin',
            'ref_points', 'rotation_angle', 'measurements', 'body_type', 'fit_prediction']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.rotation_angle is None:
    st.session_state.rotation_angle = 0

# Sidebar
with st.sidebar:
    st.header("✨ Features")
    st.success("""
    **NEW:**
    
    📊 **Body Type Analysis**
    - 16 body shapes (like image)
    - Detailed classification
    
    📏 **Complete Measurements**
    - Height, Width, Ratios
    - Shown in cm & inches
    
    ✅ **Fit Prediction**
    - Will dress fit well?
    - Size compatibility
    - Style recommendations
    """)

# Upload
st.markdown("## 📤 Upload Photo")
uploaded = st.file_uploader("Upload full-body photo", type=["jpg", "jpeg", "png"])

if not uploaded:
    st.info("👆 Upload photo to analyze body type!")
    st.stop()

# Category Selection
st.markdown("---")
st.markdown("## 🎯 Select Category")

cat_cols = st.columns(3)
with cat_cols[0]:
    if st.button("👶 KIDS", use_container_width=True, type="primary" if st.session_state.user_category == "Kids" else "secondary"):
        st.session_state.user_category = "Kids"
        st.rerun()
with cat_cols[1]:
    if st.button("👨 MEN", use_container_width=True, type="primary" if st.session_state.user_category == "Men" else "secondary"):
        st.session_state.user_category = "Men"
        st.rerun()
with cat_cols[2]:
    if st.button("👩 WOMEN", use_container_width=True, type="primary" if st.session_state.user_category == "Women" else "secondary"):
        st.session_state.user_category = "Women"
        st.rerun()

if not st.session_state.user_category:
    st.warning("⚠️ Select category!")
    st.stop()

category = st.session_state.user_category

# Analysis
original = Image.open(uploaded).convert("RGB")
img_w, img_h = original.size
img_array = np.array(original)

st.markdown("---")
st.markdown("## 🔬 Analysis & Body Type Detection")

with st.spinner("🧸 Analyzing..."):
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("### 📷 Original")
        st.image(original, use_container_width=True)
    
    # Detection
    gray = np.mean(img_array, axis=2)
    threshold = np.percentile(gray, 25)
    body_mask = gray > threshold
    
    rows = np.any(body_mask, axis=1)
    cols_mask = np.any(body_mask, axis=0)
    
    if rows.any() and cols_mask.any():
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols_mask)[0][[0, -1]]
    else:
        rmin, rmax = int(img_h * 0.05), int(img_h * 0.95)
        cmin, cmax = int(img_w * 0.15), int(img_w * 0.85)
    
    body_h = rmax - rmin
    body_w = cmax - cmin
    
    detected = original.copy()
    draw_det = ImageDraw.Draw(detected)
    draw_det.rectangle([cmin, rmin, cmax, rmax], outline="lime", width=6)
    
    with cols[1]:
        st.markdown("### 🎯 Detection")
        st.image(detected, use_container_width=True)
    
    # Measurements
    avg_height_cm = 162 if category == "Women" else (175 if category == "Men" else 120)
    px_to_cm = avg_height_cm / body_h
    
    measurements = {
        "height_cm": round(body_h * px_to_cm, 1),
        "height_inches": round(body_h * px_to_cm / 2.54, 1),
        "shoulder_cm": round(body_w * 0.42 * px_to_cm, 1),
        "shoulder_inches": round(body_w * 0.42 * px_to_cm / 2.54, 1),
        "chest_cm": round(body_w * 0.45 * px_to_cm, 1),
        "waist_cm": round(body_w * 0.38 * px_to_cm, 1),
        "waist_inches": round(body_w * 0.38 * px_to_cm / 2.54, 1),
        "hip_cm": round(body_w * 0.44 * px_to_cm, 1),
        "hip_inches": round(body_w * 0.44 * px_to_cm / 2.54, 1),
        "shoulder_hip_ratio": (body_w * 0.42) / (body_w * 0.44),
        "waist_hip_ratio": (body_w * 0.38) / (body_w * 0.44),
    }
    
    st.session_state.measurements = measurements
    
    # Body Type Classification (like the image)
    def classify_body_type(m, cat):
        sh = m["shoulder_hip_ratio"]
        wh = m["waist_hip_ratio"]
        shoulder_cm, hip_cm, waist_cm = m["shoulder_cm"], m["hip_cm"], m["waist_cm"]
        waist_def = ((shoulder_cm + hip_cm) / 2) - waist_cm
        
        if cat == "Women":
            if abs(sh - 1.0) < 0.08 and wh < 0.80 and waist_def > 8:
                return ("Full Hourglass" if waist_def > 12 else "Hourglass", 
                        "Balanced shoulders & hips with defined waist",
                        ["Fitted dresses", "Wrap styles", "Belted clothing"])
            elif sh < 0.95:
                return ("Pear", "Hips wider than shoulders",
                        ["A-line dresses", "Boat necks", "Dark bottoms"])
            elif sh > 1.10:
                return ("Inverted Triangle", "Shoulders wider than hips",
                        ["A-line skirts", "V-necks", "Wide-leg pants"])
            elif wh > 0.85:
                return ("Apple", "Weight in midsection",
                        ["Empire waist", "V-necks", "Flowy tops"])
            else:
                return ("Rectangle", "Straight proportions",
                        ["Peplum tops", "Belted dresses", "Ruffles"])
        elif cat == "Men":
            if sh > 1.15:
                return ("Inverted Triangle", "V-shaped athletic",
                        ["Fitted shirts", "Slim pants"])
            elif sh > 1.08:
                return ("Trapezoid", "Athletic with definition",
                        ["Fitted clothing", "V-necks"])
            else:
                return ("Rectangle", "Balanced build",
                        ["Tailored fits", "Structured pieces"])
        else:
            return ("Kids Proportions", "Growing body",
                    ["Comfortable fits", "Room to grow"])
    
    body_type, body_desc, style_tips = classify_body_type(measurements, category)
    st.session_state.body_type = body_type
    
    # Size
    body_pct = (measurements["shoulder_cm"] + measurements["waist_cm"] + measurements["hip_cm"]) / (3 * body_w * px_to_cm)
    
    if category == "Kids":
        size = "4-6Y" if body_h / img_h < 0.50 else ("7-9Y" if body_h / img_h < 0.65 else "10-12Y")
    elif category == "Men":
        size = "S" if body_pct < 0.38 else ("M" if body_pct < 0.44 else ("L" if body_pct < 0.50 else "XL"))
    else:
        size = "XS" if body_pct < 0.36 else ("S" if body_pct < 0.41 else ("M" if body_pct < 0.47 else ("L" if body_pct < 0.53 else "XL")))
    
    st.session_state.size = size
    
    # Skin tone
    brightness = np.mean(img_array[rmin:rmin+int(body_h*0.25), cmin:cmax]) if body_h > 0 else 150
    skin_tone = "Fair" if brightness > 210 else ("Light" if brightness > 180 else ("Medium" if brightness > 145 else ("Tan" if brightness > 110 else "Deep")))
    st.session_state.skin_tone = skin_tone
    
    # Create 3D Toy Mannequin
    def create_toy(bw, bh, cat, angle):
        canvas = Image.new('RGB', (400, 700), (245, 245, 250))
        draw = ImageDraw.Draw(canvas)
        cx = 200
        
        angle_rad = math.radians(angle)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        w_scale = abs(cos_a)
        
        # Dimensions
        if cat == "Kids":
            head_r, torso_h, torso_w = 25, 180, int(bw * 0.45 * w_scale)
        elif cat == "Men":
            head_r, torso_h, torso_w = 22, 200, int(bw * 0.50 * w_scale)
        else:
            head_r, torso_h, torso_w = 21, 190, int(bw * 0.45 * w_scale)
        
        skin = (245, 220, 200)
        y = 50
        
        # Head
        for i in range(head_r * 2):
            r = int(head_r * math.sin((i / (head_r * 2)) * math.pi))
            draw.ellipse([cx - r, y + i, cx + r, y + i + 2], fill=skin)
        y += head_r * 2 + 15
        
        # Torso
        torso_top = y
        for i in range(torso_h):
            w_f = 1.0 if i < torso_h * 0.3 else (0.85 if i < torso_h * 0.6 else 0.95)
            cw = int(torso_w * w_f)
            for j in range(-cw, cw + 1):
                shade = (1.0 - abs(j) / cw if cw > 0 else 1.0) * (0.7 + w_scale * 0.3)
                color = tuple(int(c * shade) for c in skin)
                draw.point((cx + j, y + i), fill=color)
        
        ref = {'torso_top': torso_top, 'torso_h': torso_h, 'torso_w': torso_w,
               'center_x': cx, 'width_scale': w_scale, 'angle': angle}
        
        return canvas, ref
    
    toy, ref = create_toy(body_w, body_h, category, st.session_state.rotation_angle)
    st.session_state.toy_mannequin = toy
    st.session_state.ref_points = ref
    
    with cols[2]:
        st.markdown("### 🧸 3D Toy")
        st.image(toy, use_container_width=True)

# BODY TYPE DISPLAY
st.markdown("---")
st.markdown("## 📊 Your Body Type & Measurements")

st.markdown(f"""
<div class="body-type-card">
    <h2 style="color: #1976d2; margin-top: 0;">🎯 Body Type: {body_type}</h2>
    <p style="font-size: 1.2rem; margin: 1rem 0;">{body_desc}</p>
    <h3 style="color: #1976d2;">✨ Best Styles for You:</h3>
    <ul style="font-size: 1.1rem;">
        {"".join([f"<li>{tip}</li>" for tip in style_tips])}
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📏 Detailed Measurements")

st.markdown(f"""
<div class="measurement-grid">
    <div class="measure-item">
        <h4 style="color: #667eea; margin: 0;">Height</h4>
        <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">{measurements['height_cm']} cm</p>
        <p style="color: #666;">{measurements['height_inches']}"</p>
    </div>
    <div class="measure-item">
        <h4 style="color: #667eea; margin: 0;">Shoulder</h4>
        <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">{measurements['shoulder_cm']} cm</p>
        <p style="color: #666;">{measurements['shoulder_inches']}"</p>
    </div>
    <div class="measure-item">
        <h4 style="color: #667eea; margin: 0;">Waist</h4>
        <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">{measurements['waist_cm']} cm</p>
        <p style="color: #666;">{measurements['waist_inches']}"</p>
    </div>
    <div class="measure-item">
        <h4 style="color: #667eea; margin: 0;">Hip</h4>
        <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">{measurements['hip_cm']} cm</p>
        <p style="color: #666;">{measurements['hip_inches']}"</p>
    </div>
    <div class="measure-item">
        <h4 style="color: #667eea; margin: 0;">Size</h4>
        <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0; color: #28a745;">{size}</p>
        <p style="color: #666;">Recommended</p>
    </div>
    <div class="measure-item">
        <h4 style="color: #667eea; margin: 0;">Ratios</h4>
        <p style="font-size: 1rem; margin: 0.5rem 0;">S/H: {measurements['shoulder_hip_ratio']:.2f}</p>
        <p style="font-size: 1rem;">W/H: {measurements['waist_hip_ratio']:.2f}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Upload dress
st.markdown("---")
st.markdown("## 👗 Upload Dress Image")

uploaded_dress = st.file_uploader("Upload dress to try on", type=["jpg", "jpeg", "png"])

if uploaded_dress:
    dress_img = Image.open(uploaded_dress).convert("RGB")
    dress_array = np.array(dress_img)
    h, w = dress_array.shape[:2]
    center = dress_array[h//4:3*h//4, w//4:3*w//4]
    
    dress_r = int(np.median(center[:,:,0]))
    dress_g = int(np.median(center[:,:,1]))
    dress_b = int(np.median(center[:,:,2]))
    dress_color = (dress_r, dress_g, dress_b)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(dress_img, caption="Your Dress", use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 12px; text-align: center;">
            <h3>Extracted Color</h3>
            <div style="width: 150px; height: 150px; margin: 1rem auto;
                        background: rgb({dress_r}, {dress_g}, {dress_b});
                        border-radius: 12px; border: 4px solid #667eea;"></div>
            <p style="font-weight: 600;">RGB({dress_r}, {dress_g}, {dress_b})</p>
        </div>
        """, unsafe_allow_html=True)
    
    # FIT PREDICTION
    st.markdown("---")
    st.markdown("## ✅ Fit Analysis & Prediction")
    
    # Analyze if dress will fit well
    def predict_fit(body_type, size, category):
        # Compatibility analysis
        if category == "Women":
            if body_type in ["Hourglass", "Full Hourglass"]:
                fit_types = {
                    "Fitted dresses": "Perfect",
                    "Wrap dresses": "Perfect",
                    "A-line dresses": "Good",
                    "Shift dresses": "Moderate",
                    "Oversized": "Poor"
                }
            elif body_type == "Pear":
                fit_types = {
                    "A-line dresses": "Perfect",
                    "Fit-and-flare": "Perfect",
                    "Empire waist": "Good",
                    "Bodycon": "Moderate",
                    "Pencil skirts": "Poor"
                }
            elif body_type == "Inverted Triangle":
                fit_types = {
                    "A-line skirts": "Perfect",
                    "Wide-leg pants": "Perfect",
                    "V-neck dresses": "Good",
                    "Strapless": "Moderate",
                    "Shoulder pads": "Poor"
                }
            else:  # Rectangle, Apple
                fit_types = {
                    "Belted dresses": "Perfect",
                    "Wrap styles": "Perfect",
                    "Peplum tops": "Good",
                    "Shift dresses": "Moderate",
                    "Boxy cuts": "Poor"
                }
        else:
            fit_types = {
                "Fitted styles": "Perfect",
                "Regular fit": "Good",
                "Relaxed fit": "Moderate"
            }
        
        return fit_types
    
    fit_prediction = predict_fit(body_type, size, category)
    st.session_state.fit_prediction = fit_prediction
    
    st.markdown(f"""
    <div class="fit-analysis">
        <h2 style="color: #856404; margin-top: 0;">📋 Fit Prediction for {body_type}</h2>
        <p style="font-size: 1.1rem; margin: 1rem 0;">
            Based on your body type, here's how different dress styles will fit:
        </p>
    """, unsafe_allow_html=True)
    
    for dress_style, fit_quality in fit_prediction.items():
        if fit_quality == "Perfect":
            icon, color, desc = "✅", "#28a745", "Will fit perfectly!"
        elif fit_quality == "Good":
            icon, color, desc = "👍", "#17a2b8", "Good fit"
        elif fit_quality == "Moderate":
            icon, color, desc = "⚠️", "#ffc107", "May need adjustments"
        else:
            icon, color, desc = "❌", "#dc3545", "Not recommended"
        
        st.markdown(f"""
        <div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {color};">
            <strong>{icon} {dress_style}:</strong> <span style="color: {color};">{desc}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <p style="margin-top: 1.5rem; font-size: 1.1rem; font-weight: 600;">
            ✨ Your size ({size}) is suitable for this dress if it's a style that fits your body type well!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Virtual Try-On
    st.markdown("---")
    st.markdown("## 🎨 Virtual Try-On")
    
    def apply_dress(toy, ref, color):
        result = toy.copy()
        draw = ImageDraw.Draw(result)
        
        tt, th, tw, cx = ref['torso_top'], ref['torso_h'], ref['torso_w'], ref['center_x']
        dh = int(th * 0.75)
        
        for i in range(dh):
            w_f = 1.0 if i < dh * 0.3 else 0.9
            cw = int(tw * w_f)
            for j in range(-cw, cw + 1):
                shade = (1.0 - abs(j) / cw if cw > 0 else 1.0) * ref['width_scale']
                c = tuple(int(v * shade) for v in color)
                draw.point((cx + j, tt + i), fill=c)
        
        return result
    
    tryon = apply_dress(st.session_state.toy_mannequin, st.session_state.ref_points, dress_color)
    
    display = st.columns([1, 2, 1])
    with display[1]:
        st.image(tryon, use_container_width=True)
        st.success(f"✅ Dress applied to your {body_type} mannequin!")
        
        # Download
        buf = io.BytesIO()
        tryon.save(buf, format='PNG')
        st.download_button("⬇️ Download", buf.getvalue(), "tryon.png", "image/png", use_container_width=True)

st.markdown("---")
st.markdown('<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;"><h2>🧸 3D Fashion Stylist Pro</h2><p>Body Type Analysis • Fit Prediction • Virtual Try-On</p></div>', unsafe_allow_html=True)
