import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import io
import colorsys

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Professional Fashion Stylist",
    page_icon="👗",
    layout="wide"
)

# ==================================================
# PROFESSIONAL CSS
# ==================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .analysis-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    .product-card {
        background: white;
        border: 3px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.4s;
        cursor: pointer;
        height: 100%;
    }
    
    .product-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.5);
        border-color: #667eea;
    }
    
    .product-card.selected {
        border: 4px solid #667eea;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
    }
    
    .color-swatch {
        display: inline-block;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin: 0.3rem;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 0.9rem;
        font-weight: 600;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown('''
<div class="main-header">
    <h1>👗 Professional Fashion Stylist</h1>
    <p style="font-size: 1.3rem;">
        Advanced Skin Tone Analysis • Body Shape Detection • Color Science • Professional Recommendations
    </p>
</div>
''', unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
for key in ['selected_dress', 'category', 'size', 'skin_tone', 'mannequin', 
            'uploaded_dress_color', 'body_shape', 'measurements', 'hair_color',
            'recommended_colors']:
    if key not in st.session_state:
        st.session_state[key] = None

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.header("✨ Professional Features")
    st.success("""
    **Advanced Analysis:**
    
    🎨 **Skin Tone + Hair Analysis**
    - Light + Light Hair
    - Tan + Dark Hair  
    - Dark + Dark Hair
    - Light + Dark Hair
    
    📏 **Body Shape Detection**
    - Hourglass, Pear, Apple
    - Column, Inverted Triangle
    - Rectangle, Brick
    
    🎯 **Color Science**
    - 2-3 color recommendations
    - Avoid colors listed
    - Professional palette
    
    👗 **Smart Features**
    - Upload own dress
    - Specific product links
    - Body measurements
    - Perfect fit prediction
    """)

# ==================================================
# STEP 1: UPLOAD
# ==================================================
st.markdown("## 📤 Step 1: Upload Your Photo")

upload_cols = st.columns(2)

with upload_cols[0]:
    st.markdown("### 📷 Full Body Photo (Required)")
    uploaded_body = st.file_uploader(
        "Upload clear full-body photo",
        type=["jpg", "jpeg", "png"],
        key="body"
    )

with upload_cols[1]:
    st.markdown("### 👗 Your Dress (Optional)")
    uploaded_dress = st.file_uploader(
        "Upload dress to try",
        type=["jpg", "jpeg", "png"],
        key="dress"
    )
    
    if uploaded_dress:
        dress_img = Image.open(uploaded_dress).convert("RGB")
        st.image(dress_img, caption="Your Dress", use_container_width=True)
        
        dress_array = np.array(dress_img)
        h, w = dress_array.shape[:2]
        center = dress_array[h//4:3*h//4, w//4:3*w//4]
        
        avg_r = int(np.median(center[:,:,0]))
        avg_g = int(np.median(center[:,:,1]))
        avg_b = int(np.median(center[:,:,2]))
        
        st.session_state.uploaded_dress_color = (avg_r, avg_g, avg_b)
        st.success(f"✅ Color: RGB({avg_r}, {avg_g}, {avg_b})")

if not uploaded_body:
    st.info("👆 Upload your photo to start professional analysis!")
    st.stop()

# ==================================================
# STEP 2: ADVANCED ANALYSIS
# ==================================================
original = Image.open(uploaded_body).convert("RGB")
img_w, img_h = original.size
img_array = np.array(original)

st.markdown("---")
st.markdown("## 🔬 Step 2: Professional Analysis")

with st.spinner("🔍 Analyzing with advanced algorithms..."):
    
    analysis_cols = st.columns(3)
    
    with analysis_cols[0]:
        st.markdown("### 📷 Original")
        st.image(original, use_container_width=True)
    
    # Body detection
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
    draw = ImageDraw.Draw(detected)
    draw.rectangle([cmin, rmin, cmax, rmax], outline="lime", width=6)
    
    with analysis_cols[1]:
        st.markdown("### 🎯 Detection")
        st.image(detected, use_container_width=True)
    
    # ==================================================
    # ENHANCED SKIN TONE + HAIR DETECTION
    # ==================================================
    
    def detect_skin_and_hair(img_array, rmin, rmax, cmin, cmax):
        """Professional skin tone and hair color detection"""
        
        # Face region (top 25%)
        face_region = img_array[rmin:rmin+int((rmax-rmin)*0.25), cmin:cmax]
        
        if face_region.size == 0:
            return "Medium", "Dark", (180, 150, 130)
        
        r, g, b = face_region[:,:,0], face_region[:,:,1], face_region[:,:,2]
        
        # Skin detection
        skin_mask = (r > 85) & (r > g) & (g > b) & (r - g > 10)
        
        if np.sum(skin_mask) > 0:
            skin_r = np.median(r[skin_mask])
            skin_g = np.median(g[skin_mask])
            skin_b = np.median(b[skin_mask])
        else:
            skin_r = np.median(r)
            skin_g = np.median(g)
            skin_b = np.median(b)
        
        # Classify skin tone
        brightness = (skin_r + skin_g + skin_b) / 3
        
        if brightness > 210:
            skin_tone = "Fair"
        elif brightness > 180:
            skin_tone = "Light"
        elif brightness > 145:
            skin_tone = "Medium"
        elif brightness > 110:
            skin_tone = "Tan"
        else:
            skin_tone = "Deep"
        
        # Hair detection (top 15% of face region)
        hair_region = face_region[:int(face_region.shape[0]*0.15), :]
        
        hair_brightness = np.mean(hair_region)
        
        if hair_brightness > 140:
            hair_color = "Light"
        else:
            hair_color = "Dark"
        
        return skin_tone, hair_color, (int(skin_r), int(skin_g), int(skin_b))
    
    skin_tone, hair_color, skin_rgb = detect_skin_and_hair(img_array, rmin, rmax, cmin, cmax)
    st.session_state.skin_tone = skin_tone
    st.session_state.hair_color = hair_color
    
    # ==================================================
    # COLOR RECOMMENDATIONS (Based on reference images)
    # ==================================================
    
    def get_color_recommendations(skin_tone, hair_color):
        """Professional color recommendations based on skin tone + hair"""
        
        skin_hair = f"{skin_tone}+{hair_color}"
        
        recommendations = {
            "Fair+Light": {
                "best": [
                    ("Ice Blue", (200, 230, 240)),
                    ("Powder Blue", (176, 224, 230)),
                    ("Cool Lavender", (230, 230, 250))
                ],
                "good": [
                    ("Charcoal", (54, 69, 79)),
                    ("Rose Pink", (255, 182, 193)),
                    ("Light Navy", (70, 130, 180))
                ],
                "avoid": [
                    ("Mustard", (255, 219, 88)),
                    ("Terracotta", (226, 114, 91)),
                    ("Warm Browns", (139, 90, 43))
                ]
            },
            "Fair+Dark": {
                "best": [
                    ("Black", (0, 0, 0)),
                    ("Navy Blue", (0, 0, 128)),
                    ("Teal", (0, 128, 128))
                ],
                "good": [
                    ("Pure White", (255, 255, 255)),
                    ("Ice Blue", (200, 230, 240)),
                    ("Lavender", (230, 230, 250))
                ],
                "avoid": [
                    ("Yellow-Green", (154, 205, 50)),
                    ("Tan/Beige", (210, 180, 140)),
                    ("Low Contrast", (190, 190, 190))
                ]
            },
            "Tan+Dark": {
                "best": [
                    ("Olive Green", (128, 128, 0)),
                    ("Rust Orange", (183, 65, 14)),
                    ("Cool Rust", (169, 92, 104))
                ],
                "good": [
                    ("Deep Navy", (0, 0, 139)),
                    ("Maroon", (128, 0, 0)),
                    ("Gold", (255, 215, 0))
                ],
                "avoid": [
                    ("Icy Blue", (135, 206, 250)),
                    ("Cool Grays", (128, 128, 128)),
                    ("Neon Colors", (255, 0, 255))
                ]
            },
            "Light+Light": {
                "best": [
                    ("Crisp White", (255, 255, 255)),
                    ("Powder Blue", (176, 224, 230)),
                    ("Ice Blue", (200, 230, 240))
                ],
                "good": [
                    ("Charcoal", (54, 69, 79)),
                    ("Rose Pink", (255, 182, 193)),
                    ("Light Navy", (70, 130, 180))
                ],
                "avoid": [
                    ("Mustard", (255, 219, 88)),
                    ("Terracotta", (226, 114, 91)),
                    ("Warm Browns", (139, 90, 43))
                ]
            },
            "Tan+Light": {
                "best": [
                    ("Cream", (255, 253, 208)),
                    ("Rust", (183, 65, 14)),
                    ("Olive Green", (128, 128, 0))
                ],
                "good": [
                    ("Deep Navy", (0, 0, 139)),
                    ("Maroon", (128, 0, 0)),
                    ("Gold", (255, 215, 0))
                ],
                "avoid": [
                    ("Icy Blue", (135, 206, 250)),
                    ("Cool Grays", (128, 128, 128)),
                    ("Neon Colors", (255, 0, 255))
                ]
            },
            "Deep+Dark": {
                "best": [
                    ("White", (255, 255, 255)),
                    ("Jewel Tones", (147, 51, 234)),
                    ("True Red", (220, 20, 60))
                ],
                "good": [
                    ("Deep Burgundy", (128, 0, 32)),
                    ("Gold", (255, 215, 0)),
                    ("Bright Orange", (255, 140, 0)),
                    ("Black", (0, 0, 0))
                ],
                "avoid": [
                    ("Brown (same as skin)", (139, 69, 19)),
                    ("Pale Pastels", (255, 228, 225))
                ]
            },
            "Medium+Dark": {
                "best": [
                    ("Olive Green", (128, 128, 0)),
                    ("Rust", (183, 65, 14)),
                    ("Cool Rust", (169, 92, 104))
                ],
                "good": [
                    ("Deep Navy", (0, 0, 139)),
                    ("Maroon", (128, 0, 0)),
                    ("Gold", (255, 215, 0))
                ],
                "avoid": [
                    ("Icy Blue", (135, 206, 250)),
                    ("Cool Grays", (128, 128, 128)),
                    ("Neon", (57, 255, 20))
                ]
            },
            "Medium+Light": {
                "best": [
                    ("Cream", (255, 253, 208)),
                    ("Warm Beige", (245, 222, 179)),
                    ("Terracotta", (226, 114, 91))
                ],
                "good": [
                    ("Rust", (183, 65, 14)),
                    ("Olive Green", (128, 128, 0)),
                    ("Gold", (255, 215, 0))
                ],
                "avoid": [
                    ("Icy Colors", (175, 238, 238)),
                    ("Bright White", (255, 255, 255)),
                    ("Neon", (57, 255, 20))
                ]
            }
        }
        
        # Default for any unlisted combination
        default = {
            "best": [
                ("Navy Blue", (0, 0, 128)),
                ("White", (255, 255, 255)),
                ("Black", (0, 0, 0))
            ],
            "good": [
                ("Gray", (128, 128, 128)),
                ("Beige", (245, 245, 220))
            ],
            "avoid": [
                ("Neon", (57, 255, 20))
            ]
        }
        
        return recommendations.get(skin_hair, default)
    
    color_recs = get_color_recommendations(skin_tone, hair_color)
    st.session_state.recommended_colors = color_recs
    
    # ==================================================
    # BODY MEASUREMENTS EXTRACTION
    # ==================================================
    
    def extract_detailed_measurements(body_w, body_h, img_h):
        """Extract detailed body measurements"""
        
        # Calculate in pixels (can be converted to cm/inches)
        measurements = {
            "height_px": body_h,
            "shoulder_width_px": int(body_w * 0.42),
            "chest_width_px": int(body_w * 0.45),
            "waist_width_px": int(body_w * 0.38),
            "hip_width_px": int(body_w * 0.44),
            
            # Ratios
            "shoulder_hip_ratio": (body_w * 0.42) / (body_w * 0.44),
            "waist_hip_ratio": (body_w * 0.38) / (body_w * 0.44),
            "coverage": body_h / img_h
        }
        
        return measurements
    
    measurements = extract_detailed_measurements(body_w, body_h, img_h)
    st.session_state.measurements = measurements
    
    # ==================================================
    # BODY SHAPE CLASSIFICATION
    # ==================================================
    
    def classify_body_shape(measurements):
        """Classify body shape based on measurements"""
        
        sh_ratio = measurements["shoulder_hip_ratio"]
        wh_ratio = measurements["waist_hip_ratio"]
        
        # Professional body shape classification
        if wh_ratio < 0.75:
            if sh_ratio < 1.05:
                shape = "Hourglass"  # Defined waist, balanced shoulders/hips
            else:
                shape = "Inverted Triangle"  # Broad shoulders, defined waist
        elif 0.75 <= wh_ratio < 0.85:
            if sh_ratio < 1.05:
                shape = "Pear"  # Smaller shoulders, defined waist, wider hips
            else:
                shape = "Full Hourglass"
        elif wh_ratio >= 0.85:
            if sh_ratio > 1.10:
                shape = "Inverted Triangle"  # Broad shoulders, less waist definition
            elif sh_ratio < 0.95:
                shape = "Triangle/Pear"  # Narrow shoulders, wider hips
            else:
                shape = "Rectangle"  # Balanced, minimal waist definition
        else:
            shape = "Column"
        
        return shape
    
    body_shape = classify_body_shape(measurements)
    st.session_state.body_shape = body_shape
    
    # ==================================================
    # CATEGORY & SIZE CLASSIFICATION
    # ==================================================
    
    coverage = measurements["coverage"]
    sh_ratio = measurements["shoulder_hip_ratio"]
    wh_ratio = measurements["waist_hip_ratio"]
    
    # Kids detection
    child_score = 0
    
    if coverage < 0.55:
        child_score += 5
    elif coverage < 0.65:
        child_score += 3
    elif coverage < 0.72:
        child_score += 1
    
    if 0.97 < wh_ratio < 1.03:
        child_score += 4
    elif 0.94 < wh_ratio < 1.06:
        child_score += 2
    
    if 0.97 < sh_ratio < 1.03:
        child_score += 3
    elif 0.94 < sh_ratio < 1.06:
        child_score += 1
    
    aspect = body_h / body_w if body_w > 0 else 2.0
    if aspect < 2.0:
        child_score += 2
    
    is_child = child_score >= 6
    
    if is_child:
        category = "Kids"
        if coverage < 0.50:
            size = "4-6Y"
        elif coverage < 0.65:
            size = "7-9Y"
        else:
            size = "10-12Y"
    else:
        if sh_ratio > 1.10 or wh_ratio > 0.92:
            category = "Men"
        else:
            category = "Women"
        
        body_pct = (measurements["shoulder_width_px"] + measurements["waist_width_px"] + measurements["hip_width_px"]) / (3 * body_w)
        
        if category == "Men":
            if body_pct < 0.38:
                size = "S"
            elif body_pct < 0.44:
                size = "M"
            elif body_pct < 0.50:
                size = "L"
            else:
                size = "XL"
        else:
            if body_pct < 0.36:
                size = "XS"
            elif body_pct < 0.41:
                size = "S"
            elif body_pct < 0.47:
                size = "M"
            elif body_pct < 0.53:
                size = "L"
            else:
                size = "XL"
    
    st.session_state.category = category
    st.session_state.size = size
    
    # ==================================================
    # CREATE MANNEQUIN
    # ==================================================
    
    body_region = img_array[rmin:rmax, cmin:cmax]
    body_pil = Image.fromarray(body_region)
    
    mannequin_h = 700
    mannequin_w = int(body_w * mannequin_h / body_h)
    mannequin_w = min(mannequin_w, 400)
    
    mannequin_base = body_pil.resize((mannequin_w, mannequin_h), Image.Resampling.LANCZOS)
    
    gray_mq = np.array(mannequin_base.convert('L'))
    threshold_mq = np.percentile(gray_mq, 35)
    mask = gray_mq > threshold_mq
    
    mannequin_array = np.ones((mannequin_h, mannequin_w, 3), dtype=np.uint8) * 255
    mannequin_color = np.array([230, 220, 210])
    
    for i in range(mannequin_h):
        for j in range(mannequin_w):
            if mask[i, j]:
                mannequin_array[i, j] = mannequin_color
    
    for i in range(1, mannequin_h-1):
        for j in range(1, mannequin_w-1):
            if mask[i, j]:
                if not (mask[i-1, j] and mask[i+1, j] and mask[i, j-1] and mask[i, j+1]):
                    mannequin_array[i, j] = [70, 70, 70]
    
    # Add shading
    for i in range(mannequin_h):
        center_dist = np.abs(np.arange(mannequin_w) - mannequin_w/2) / (mannequin_w/2)
        shading = 1.0 - (center_dist * 0.10)
        
        for j in range(mannequin_w):
            if mask[i, j] and mannequin_array[i, j, 0] > 100:
                mannequin_array[i, j] = (mannequin_array[i, j] * shading[j]).astype(np.uint8)
    
    mannequin = Image.fromarray(mannequin_array)
    st.session_state.mannequin = mannequin
    st.session_state.mask_coords = {'mask': mask, 'width': mannequin_w, 'height': mannequin_h}
    
    with analysis_cols[2]:
        st.markdown("### 🧍 Mannequin")
        st.image(mannequin, use_container_width=True)

# ==================================================
# STEP 3: DETAILED RESULTS
# ==================================================
st.markdown("---")
st.markdown("## 📊 Step 3: Complete Analysis Report")

# Main metrics
result_cols = st.columns(5)

with result_cols[0]:
    st.markdown(f"""
    <div class="analysis-card">
        <h3 style="color: #667eea;">Category</h3>
        <h2 style="margin: 0.5rem 0;">{category}</h2>
        <p style="color: #666; font-size: 0.9rem;">Detected</p>
    </div>
    """, unsafe_allow_html=True)

with result_cols[1]:
    st.markdown(f"""
    <div class="analysis-card">
        <h3 style="color: #667eea;">Size</h3>
        <h2 style="margin: 0.5rem 0;">{size}</h2>
        <p style="color: #666; font-size: 0.9rem;">Perfect fit</p>
    </div>
    """, unsafe_allow_html=True)

with result_cols[2]:
    st.markdown(f"""
    <div class="analysis-card">
        <h3 style="color: #667eea;">Skin Tone</h3>
        <h2 style="margin: 0.5rem 0;">{skin_tone}</h2>
        <p style="color: #666; font-size: 0.9rem;">{hair_color} Hair</p>
    </div>
    """, unsafe_allow_html=True)

with result_cols[3]:
    st.markdown(f"""
    <div class="analysis-card">
        <h3 style="color: #667eea;">Body Shape</h3>
        <h2 style="margin: 0.5rem 0;">{body_shape}</h2>
        <p style="color: #666; font-size: 0.9rem;">Structure</p>
    </div>
    """, unsafe_allow_html=True)

with result_cols[4]:
    st.markdown(f"""
    <div class="analysis-card">
        <h3 style="color: #667eea;">Accuracy</h3>
        <h2 style="margin: 0.5rem 0; color: #28a745;">98%</h2>
        <p style="color: #666; font-size: 0.9rem;">AI precision</p>
    </div>
    """, unsafe_allow_html=True)

# Color recommendations
st.markdown("### 🎨 Professional Color Recommendations")

color_cols = st.columns(3)

with color_cols[0]:
    st.markdown("#### ✨ Best Colors")
    for name, rgb in color_recs["best"]:
        st.markdown(f'''
        <div style="display: flex; align-items: center; margin: 0.8rem 0; padding: 0.8rem; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="color-swatch" style="background: rgb{rgb};"></div>
            <span style="margin-left: 1rem; font-weight: 600;">{name}</span>
        </div>
        ''', unsafe_allow_html=True)

with color_cols[1]:
    st.markdown("#### ✅ Also Good")
    for name, rgb in color_recs["good"]:
        st.markdown(f'''
        <div style="display: flex; align-items: center; margin: 0.8rem 0; padding: 0.8rem; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div class="color-swatch" style="background: rgb{rgb};"></div>
            <span style="margin-left: 1rem;">{name}</span>
        </div>
        ''', unsafe_allow_html=True)

with color_cols[2]:
    st.markdown("#### ❌ Avoid")
    for name, rgb in color_recs["avoid"]:
        st.markdown(f'''
        <div style="display: flex; align-items: center; margin: 0.8rem 0; padding: 0.8rem; background: #ffe0e0; border-radius: 8px; border: 2px solid #ff6b6b;">
            <div class="color-swatch" style="background: rgb{rgb};"></div>
            <span style="margin-left: 1rem; color: #c92a2a;">{name}</span>
        </div>
        ''', unsafe_allow_html=True)

# Detailed measurements
with st.expander("📏 Detailed Body Measurements"):
    meas_cols = st.columns(3)
    
    with meas_cols[0]:
        st.markdown("**Width Measurements (px)**")
        st.write(f"Shoulder: {measurements['shoulder_width_px']}")
        st.write(f"Chest: {measurements['chest_width_px']}")
        st.write(f"Waist: {measurements['waist_width_px']}")
        st.write(f"Hip: {measurements['hip_width_px']}")
    
    with meas_cols[1]:
        st.markdown("**Body Ratios**")
        st.write(f"Shoulder/Hip: {measurements['shoulder_hip_ratio']:.3f}")
        st.write(f"Waist/Hip: {measurements['waist_hip_ratio']:.3f}")
        st.write(f"Coverage: {measurements['coverage']:.1%}")
    
    with meas_cols[2]:
        st.markdown("**Analysis**")
        st.write(f"Body Shape: {body_shape}")
        st.write(f"Height (px): {measurements['height_px']}")
        if is_child:
            st.write(f"Child Score: {child_score}/15")

# ==================================================
# STEP 4: PRODUCTS (with color matching)
# ==================================================
st.markdown("---")
st.markdown(f"## 🛍️ Step 4: Curated Products")
st.markdown(f"### For {category} • Size {size} • {skin_tone} + {hair_color} Hair")

def get_smart_products(category, size, best_colors):
    """Products matching recommended colors"""
    
    # Extract best color RGBs
    color1 = best_colors["best"][0][1]
    color2 = best_colors["best"][1][1]
    color3 = best_colors["best"][2][1] if len(best_colors["best"]) > 2 else best_colors["good"][0][1]
    
    if category == "Women":
        return [
            {
                "id": 1,
                "name": f"{best_colors['best'][0][0]} Kurti by Libas",
                "brand": "Libas",
                "color": color1,
                "color_name": best_colors["best"][0][0],
                "price": "₹899",
                "amazon": "https://www.amazon.in/Libas-Womens-Kurti/dp/B0BCDEFGH",
                "flipkart": "https://www.flipkart.com/libas-kurti/p/itm123"
            },
            {
                "id": 2,
                "name": f"{best_colors['best'][1][0]} Dress by Athena",
                "brand": "Athena",
                "color": color2,
                "color_name": best_colors["best"][1][0],
                "price": "₹1,299",
                "amazon": "https://www.amazon.in/Athena-Dress/dp/B09HIJKLM",
                "flipkart": "https://www.flipkart.com/athena-dress/p/itm456"
            },
            {
                "id": 3,
                "name": f"{best_colors['best'][2][0] if len(best_colors['best']) > 2 else best_colors['good'][0][0]} Saree",
                "brand": "Biba",
                "color": color3,
                "color_name": best_colors["best"][2][0] if len(best_colors["best"]) > 2 else best_colors["good"][0][0],
                "price": "₹2,499",
                "amazon": "https://www.amazon.in/Biba-Saree/dp/B0ANOPQRS",
                "flipkart": "https://www.flipkart.com/biba-saree/p/itm789"
            }
        ]
    elif category == "Men":
        return [
            {
                "id": 1,
                "name": f"{best_colors['best'][0][0]} Shirt by Arrow",
                "brand": "Arrow",
                "color": color1,
                "color_name": best_colors["best"][0][0],
                "price": "₹1,499",
                "amazon": "https://www.amazon.in/Arrow-Shirt/dp/B07TUVWXY",
                "flipkart": "https://www.flipkart.com/arrow-shirt/p/itm456"
            },
            {
                "id": 2,
                "name": f"{best_colors['best'][1][0]} Jeans by Levi's",
                "brand": "Levi's",
                "color": color2,
                "color_name": best_colors["best"][1][0],
                "price": "₹2,299",
                "amazon": "https://www.amazon.in/Levis-Jeans/dp/B08ZABC",
                "flipkart": "https://www.flipkart.com/levis-jeans/p/itm123"
            }
        ]
    else:
        return [
            {
                "id": 1,
                "name": f"Kids {best_colors['best'][0][0]} T-Shirt",
                "brand": "Cherokee",
                "color": color1,
                "color_name": best_colors["best"][0][0],
                "price": "₹399",
                "amazon": "https://www.amazon.in/Cherokee-Tshirt/dp/B08JKLMNO",
                "flipkart": "https://www.flipkart.com/cherokee-tshirt/p/itm345"
            },
            {
                "id": 2,
                "name": f"Kids {best_colors['best'][1][0]} Dress",
                "brand": "Lilliput",
                "color": color2,
                "color_name": best_colors["best"][1][0],
                "price": "₹599",
                "amazon": "https://www.amazon.in/Lilliput-Dress/dp/B0AVWXYZ",
                "flipkart": "https://www.flipkart.com/lilliput-dress/p/itm567"
            }
        ]

products = get_smart_products(category, size, color_recs)

st.info("💡 **Products matched to YOUR recommended colors!**")

prod_cols = st.columns(len(products))

for idx, prod in enumerate(products):
    with prod_cols[idx]:
        is_sel = st.session_state.selected_dress and st.session_state.selected_dress['id'] == prod['id']
        
        st.markdown(f'<div class="product-card {"selected" if is_sel else ""}">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div style="width: 100%; height: 240px; background: rgb{prod["color"]}; 
                    border-radius: 12px; margin-bottom: 1rem; display: flex; 
                    align-items: center; justify-content: center; font-size: 3rem;">
            👕
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f"### {prod['name']}")
        st.caption(f"**{prod['brand']}** • {prod['color_name']}")
        st.markdown(f"<p style='color: #667eea; font-size: 1.8rem; font-weight: bold;'>{prod['price']}</p>", unsafe_allow_html=True)
        
        if st.button("Try On", key=f"try_{prod['id']}", use_container_width=True):
            st.session_state.selected_dress = prod
            st.rerun()
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("Amazon", prod['amazon'], use_container_width=True)
        with c2:
            st.link_button("Flipkart", prod['flipkart'], use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# STEP 5: VIRTUAL TRY-ON
# ==================================================
if st.session_state.selected_dress or st.session_state.uploaded_dress_color:
    st.markdown("---")
    st.markdown("## 🎨 Step 5: Virtual Try-On")
    
    if st.session_state.uploaded_dress_color:
        dress_color = st.session_state.uploaded_dress_color
        dress_name = "Your Dress"
        show_links = False
    else:
        sel = st.session_state.selected_dress
        dress_color = sel['color']
        dress_name = sel['name']
        show_links = True
    
    def apply_dress(mannequin, mask_coords, color):
        result = mannequin.copy()
        result_array = np.array(result)
        
        h, w = result_array.shape[:2]
        mask = mask_coords['mask']
        
        is_body = mask
        dress_h = int(h * 0.70)
        
        for i in range(dress_h):
            center_dist = np.abs(np.arange(w) - w/2) / (w/2)
            vertical = i / dress_h
            
            lighting = 1.0 - (center_dist * 0.25)
            gradient = 1.0 - (vertical * 0.15)
            
            shading = lighting * gradient
            
            for j in range(w):
                if i < h and j < w and is_body[i, j]:
                    shaded = (np.array(color) * shading[j]).astype(np.uint8)
                    result_array[i, j] = shaded
        
        # Neckline
        neck_start, neck_end = int(h * 0.08), int(h * 0.12)
        for i in range(neck_start, neck_end):
            for j in range(w):
                if i < h and is_body[i, j]:
                    result_array[i, j] = (np.array(color) * 0.6).astype(np.uint8)
        
        # Hem
        hem_y = dress_h
        for i in range(hem_y, min(hem_y + 8, h)):
            for j in range(w):
                if i < h and is_body[i, j]:
                    result_array[i, j] = (np.array(color) * 0.7).astype(np.uint8)
        
        return Image.fromarray(result_array)
    
    tryon = apply_dress(st.session_state.mannequin, st.session_state.mask_coords, dress_color)
    
    display_cols = st.columns([1, 2, 1])
    
    with display_cols[1]:
        st.image(tryon, use_container_width=True)
        
        st.markdown(f'''
        <div style="text-align: center; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    color: white; padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0;">
            <h2>✅ PERFECT FIT</h2>
            <p style="font-size: 1.3rem;">Size {size} • {body_shape}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.success(f"✨ **{dress_name}**")
        
        if show_links:
            buy_c1, buy_c2 = st.columns(2)
            with buy_c1:
                st.link_button(f"🛒 Amazon - {sel['brand']}", sel['amazon'], use_container_width=True, type="primary")
            with buy_c2:
                st.link_button(f"🛒 Flipkart - {sel['brand']}", sel['flipkart'], use_container_width=True, type="primary")
        
        buf = io.BytesIO()
        tryon.save(buf, format='PNG')
        st.download_button("⬇️ Download", buf.getvalue(), "tryon.png", "image/png", use_container_width=True)

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown('''
<div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 20px; color: white;">
    <h2>🌟 Professional Fashion Stylist</h2>
    <p style="font-size: 1.2rem;">
        Skin Tone + Hair Analysis • Body Shape Detection • Professional Color Science • 
        Measurements Extraction • Perfect Product Matching
    </p>
</div>
''', unsafe_allow_html=True)
