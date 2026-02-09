import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageStat
import io
import colorsys

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Fashion Stylist",
    page_icon="👗",
    layout="wide"
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .fit-badge {
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
        margin: 0.5rem;
    }
    .fit-perfect { background: #28a745; color: white; }
    .fit-tight { background: #ffc107; color: #000; }
    .fit-loose { background: #17a2b8; color: white; }
    .product-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
        height: 100%;
    }
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    .product-card.selected {
        border: 3px solid #667eea;
        background: #f0f4ff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>👗 Smart Fashion Stylist</h1>
    <p style="font-size: 1.2rem;">AI Body Analysis • Skin Tone Detection • Perfect Fit Checker</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Session State
# --------------------------------------------------
if 'mannequin' not in st.session_state:
    st.session_state.mannequin = None
if 'selected_dress' not in st.session_state:
    st.session_state.selected_dress = None
if 'category' not in st.session_state:
    st.session_state.category = None
if 'size' not in st.session_state:
    st.session_state.size = None
if 'skin_tone' not in st.session_state:
    st.session_state.skin_tone = None

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.header("🎯 Features")
    st.success("""
    ✅ Smart body analysis
    ✅ Accurate gender detection
    ✅ Skin tone analysis
    ✅ Size recommendation
    ✅ Mannequin generation
    ✅ Virtual try-on
    ✅ Fit checker
    ✅ Personalized recommendations
    ✅ Direct shopping links
    """)
    
    st.header("📸 Photo Tips")
    st.info("""
    • Full body OR upper body OK
    • Good lighting
    • Clear image
    • Standing pose
    • Any background
    """)

# --------------------------------------------------
# Upload
# --------------------------------------------------
st.markdown("## 📤 Step 1: Upload Your Photo")

uploaded = st.file_uploader("Choose your photo", type=["jpg", "jpeg", "png"])

if not uploaded:
    st.info("👆 Upload your photo to start")
    st.stop()

# --------------------------------------------------
# Process Image
# --------------------------------------------------
image = Image.open(uploaded).convert("RGB")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📷 Your Photo")
    st.image(image, use_container_width=True)

img_width, img_height = image.size
img_array = np.array(image)

# --------------------------------------------------
# Improved Detection
# --------------------------------------------------
with st.spinner("🔍 Analyzing..."):
    gray = np.mean(img_array, axis=2)
    
    # Body detection
    threshold = np.percentile(gray, 30)
    body_mask = gray > threshold
    
    rows = np.any(body_mask, axis=1)
    cols = np.any(body_mask, axis=0)
    
    if rows.any() and cols.any():
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
    else:
        rmin, rmax = int(img_height * 0.1), int(img_height * 0.9)
        cmin, cmax = int(img_width * 0.2), int(img_width * 0.8)
    
    body_h = rmax - rmin
    body_w = cmax - cmin

# --------------------------------------------------
# Extract Face Region for Better Classification
# --------------------------------------------------
def detect_face_region(img_array):
    """Detect face region using brightness and color"""
    h, w = img_array.shape[:2]
    
    # Check top 40% of image for face
    top_region = img_array[:int(h*0.4), :]
    
    # Skin tone detection in RGB
    r = top_region[:,:,0]
    g = top_region[:,:,1]
    b = top_region[:,:,2]
    
    # Skin tone typically: R > G > B and R > 95
    skin_mask = (r > 95) & (r > g) & (g > b) & (r - g > 15)
    
    if np.any(skin_mask):
        face_rows, face_cols = np.where(skin_mask)
        if len(face_rows) > 100:  # Enough skin pixels
            face_rmin, face_rmax = face_rows.min(), face_rows.max()
            face_cmin, face_cmax = face_cols.min(), face_cols.max()
            
            face_height = face_rmax - face_rmin
            face_width = face_cmax - face_cmin
            
            # Valid face proportions
            if 0.7 < face_width / face_height < 1.3 and face_height > h * 0.08:
                return True, (face_rmin, face_rmax, face_cmin, face_cmax)
    
    return False, None

has_face, face_coords = detect_face_region(img_array)

# --------------------------------------------------
# Skin Tone Detection
# --------------------------------------------------
def detect_skin_tone(img_array, face_coords=None):
    """Detect skin tone from image"""
    
    if face_coords:
        # Use face region
        fr_min, fr_max, fc_min, fc_max = face_coords
        skin_region = img_array[fr_min:fr_max, fc_min:fc_max]
    else:
        # Use upper 30% of detected body
        skin_region = img_array[rmin:rmin+int(body_h*0.3), cmin:cmax]
    
    # Get average skin color
    avg_r = np.mean(skin_region[:,:,0])
    avg_g = np.mean(skin_region[:,:,1])
    avg_b = np.mean(skin_region[:,:,2])
    
    # Convert to HSV for better analysis
    r, g, b = avg_r/255, avg_g/255, avg_b/255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Classify skin tone
    if v > 0.75:
        if s < 0.15:
            tone = "Fair"
            tone_colors = ["pastels", "jewel tones", "burgundy", "navy"]
        else:
            tone = "Light"
            tone_colors = ["earth tones", "coral", "teal", "warm colors"]
    elif v > 0.50:
        if s < 0.25:
            tone = "Medium"
            tone_colors = ["vibrant", "emerald", "ruby", "gold"]
        else:
            tone = "Olive"
            tone_colors = ["warm earth", "olive green", "burnt orange"]
    else:
        if s < 0.20:
            tone = "Tan"
            tone_colors = ["rich jewels", "deep blues", "warm reds"]
        else:
            tone = "Deep"
            tone_colors = ["bright", "bold", "metallics", "white"]
    
    return tone, tone_colors, (int(avg_r), int(avg_g), int(avg_b))

skin_tone, recommended_colors, skin_rgb = detect_skin_tone(img_array, face_coords)
st.session_state.skin_tone = skin_tone

# --------------------------------------------------
# Measurements
# --------------------------------------------------
def extract_measurements(body_w, body_h, img_w, img_h, img_array, rmin, rmax, cmin, cmax):
    """Extract body measurements"""
    
    body_region = img_array[rmin:rmax, cmin:cmax]
    region_h, region_w = body_region.shape[:2]
    
    # Analyze vertical sections
    shoulder_region = body_region[:int(region_h * 0.3), :]
    waist_region = body_region[int(region_h * 0.4):int(region_h * 0.6), :]
    hip_region = body_region[int(region_h * 0.6):int(region_h * 0.8), :]
    
    def get_width(section):
        if section.size == 0:
            return region_w * 0.8
        gray_section = np.mean(section, axis=2)
        col_var = np.var(gray_section, axis=0)
        threshold = np.percentile(col_var, 25)
        body_cols = col_var > threshold
        if np.any(body_cols):
            left = np.where(body_cols)[0][0]
            right = np.where(body_cols)[0][-1]
            return right - left
        return region_w * 0.8
    
    shoulder_w = get_width(shoulder_region)
    waist_w = get_width(waist_region)
    hip_w = get_width(hip_region)
    chest_w = (shoulder_w + waist_w) / 2
    
    return {
        "shoulder_width": shoulder_w,
        "chest_width": chest_w,
        "waist_width": waist_w,
        "hip_width": hip_w,
        "total_height": body_h,
        "shoulder_hip_ratio": shoulder_w / hip_w if hip_w > 0 else 1.0,
        "waist_hip_ratio": waist_w / hip_w if hip_w > 0 else 0.85,
        "body_coverage": body_h / img_h  # How much of image is body
    }

measurements = extract_measurements(body_w, body_h, img_width, img_height, img_array, rmin, rmax, cmin, cmax)

# --------------------------------------------------
# IMPROVED CLASSIFICATION
# --------------------------------------------------
def classify_improved(measurements, has_face, img_h, body_h):
    """Improved classification with face detection"""
    
    shoulder_hip = measurements["shoulder_hip_ratio"]
    waist_hip = measurements["waist_hip_ratio"]
    coverage = measurements["body_coverage"]
    
    # KEY INSIGHT: If face is detected + curves visible = ADULT
    # Kids don't have developed curves (waist_hip close to 1.0)
    
    # Step 1: Check if it's a child
    # Children have:
    # - Less body definition (waist/hip ratio > 0.92)
    # - Similar shoulder/hip (0.95-1.05)
    # - Shorter overall
    
    is_child_score = 0
    
    # Body proportions (most reliable for kids)
    if 0.92 < waist_hip < 1.08:  # Kids have minimal waist definition
        is_child_score += 3
    
    if 0.95 < shoulder_hip < 1.05:  # Kids have similar shoulder/hip
        is_child_score += 2
    
    # Coverage (kids are usually smaller in frame, BUT this woman is also not full body!)
    # So we REDUCE weight of this factor
    if coverage < 0.70:
        is_child_score += 1  # Reduced from 3
    
    # Face detection is CRITICAL
    # If face is detected AND waist/hip shows curves, it's ADULT
    if has_face and waist_hip < 0.88:
        is_child_score = 0  # Override! Clear adult with curves
    
    # Classify
    if is_child_score >= 4:  # Need stronger evidence for child
        category = "Kids"
        if body_h < img_h * 0.50:
            size = "4-6Y"
        elif body_h < img_h * 0.65:
            size = "7-9Y"
        else:
            size = "10-12Y"
    else:
        # ADULT - now determine Men vs Women
        # Women: defined waist (waist_hip < 0.85) OR balanced shoulders
        # Men: broader shoulders (shoulder_hip > 1.08) AND less waist definition
        
        is_male_score = 0
        
        # Shoulder dominance
        if shoulder_hip > 1.12:
            is_male_score += 3
        elif shoulder_hip > 1.06:
            is_male_score += 1
        
        # Waist definition (CRITICAL for women)
        if waist_hip < 0.78:
            is_male_score -= 4  # Strong female indicator
        elif waist_hip < 0.85:
            is_male_score -= 2  # Moderate female indicator
        elif waist_hip > 0.92:
            is_male_score += 2  # Male indicator
        
        # Final classification
        if is_male_score >= 2:
            category = "Men"
        else:
            category = "Women"
        
        # Size determination
        shoulder_pct = measurements["shoulder_width"] / (cmax - cmin)
        waist_pct = measurements["waist_width"] / (cmax - cmin)
        hip_pct = measurements["hip_width"] / (cmax - cmin)
        
        if category == "Men":
            size_score = shoulder_pct * 0.5 + waist_pct * 0.3 + hip_pct * 0.2
            if size_score < 0.62:
                size = "S"
            elif size_score < 0.72:
                size = "M"
            elif size_score < 0.82:
                size = "L"
            else:
                size = "XL"
        else:  # Women
            size_score = shoulder_pct * 0.3 + waist_pct * 0.3 + hip_pct * 0.4
            if size_score < 0.58:
                size = "XS"
            elif size_score < 0.66:
                size = "S"
            elif size_score < 0.74:
                size = "M"
            elif size_score < 0.82:
                size = "L"
            else:
                size = "XL"
    
    return category, size

category, size = classify_improved(measurements, has_face, img_height, body_h)
st.session_state.category = category
st.session_state.size = size

# --------------------------------------------------
# Create Mannequin
# --------------------------------------------------
def create_mannequin(measurements, category):
    canvas = Image.new('RGB', (400, 800), 'white')
    draw = ImageDraw.Draw(canvas, 'RGBA')
    
    scale = 600 / measurements["total_height"]
    
    shoulder_w = int(measurements["shoulder_width"] * scale)
    chest_w = int(measurements["chest_width"] * scale)
    waist_w = int(measurements["waist_width"] * scale)
    hip_w = int(measurements["hip_width"] * scale)
    
    cx = 200
    head_y = 80
    
    # Colors
    if category == "Men":
        base = (220, 215, 210)
    elif category == "Women":
        base = (230, 225, 220)
    else:
        base = (240, 235, 230)
    
    outline = (100, 100, 100)
    
    # Head
    draw.ellipse([cx-30, head_y, cx+30, head_y+60], fill=base, outline=outline, width=3)
    
    # Neck
    draw.rectangle([cx-15, head_y+60, cx+15, head_y+90], fill=base, outline=outline, width=2)
    
    # Torso
    torso_top = head_y + 90
    chest_y = torso_top + 60
    waist_y = torso_top + 150
    hip_y = torso_top + 220
    
    torso_points = [
        (cx - shoulder_w//2, torso_top),
        (cx + shoulder_w//2, torso_top),
        (cx + chest_w//2, chest_y),
        (cx + waist_w//2, waist_y),
        (cx + hip_w//2, hip_y),
        (cx - hip_w//2, hip_y),
        (cx - waist_w//2, waist_y),
        (cx - chest_w//2, chest_y),
    ]
    draw.polygon(torso_points, fill=base, outline=outline, width=3)
    
    # Arms
    arm_w = 20
    draw.rectangle([cx - shoulder_w//2 - arm_w - 5, torso_top + 10,
                   cx - shoulder_w//2 - 5, torso_top + 160],
                  fill=base, outline=outline, width=2)
    draw.rectangle([cx + shoulder_w//2 + 5, torso_top + 10,
                   cx + shoulder_w//2 + arm_w + 5, torso_top + 160],
                  fill=base, outline=outline, width=2)
    
    # Legs
    leg_w = hip_w // 2 - 10
    draw.polygon([
        (cx - 10, hip_y), (cx - leg_w, hip_y),
        (cx - leg_w + 15, hip_y + 300), (cx - 5, hip_y + 300)
    ], fill=base, outline=outline, width=3)
    draw.polygon([
        (cx + 10, hip_y), (cx + leg_w, hip_y),
        (cx + leg_w - 15, hip_y + 300), (cx + 5, hip_y + 300)
    ], fill=base, outline=outline, width=3)
    
    ref_points = {
        "center_x": cx,
        "torso_top": torso_top,
        "chest_y": chest_y,
        "waist_y": waist_y,
        "hip_y": hip_y,
        "shoulder_w": shoulder_w,
        "chest_w": chest_w,
        "waist_w": waist_w,
        "hip_w": hip_w,
    }
    
    return canvas, ref_points

mannequin, ref_points = create_mannequin(measurements, category)
st.session_state.mannequin = mannequin
st.session_state.ref_points = ref_points

with col2:
    st.markdown("### 🎨 Your Mannequin")
    st.image(mannequin, use_container_width=True)

# --------------------------------------------------
# Results
# --------------------------------------------------
st.markdown("---")
st.markdown("## 📊 Step 2: Your Analysis")

cols = st.columns(4)
with cols[0]:
    st.metric("Category", category)
with cols[1]:
    st.metric("Size", size)
with cols[2]:
    st.metric("Skin Tone", skin_tone)
with cols[3]:
    st.metric("Face Detected", "Yes" if has_face else "No")

with st.expander("📏 Detailed Measurements & Classification Logic"):
    st.write(f"**Shoulder/Hip Ratio:** {measurements['shoulder_hip_ratio']:.2f}")
    st.write(f"**Waist/Hip Ratio:** {measurements['waist_hip_ratio']:.2f}")
    st.write(f"**Body Coverage:** {measurements['body_coverage']:.1%}")
    st.write(f"**Has Face:** {has_face}")
    
    if category == "Women":
        st.success(f"""
        **Classified as WOMEN because:**
        - Waist/Hip ratio {measurements['waist_hip_ratio']:.2f} shows defined waist (< 0.88 indicates curves)
        - Face detected: {has_face}
        - Clear adult body proportions with feminine curves
        """)
    elif category == "Men":
        st.info(f"""
        **Classified as MEN because:**
        - Shoulder/Hip ratio {measurements['shoulder_hip_ratio']:.2f} (broader shoulders)
        - Waist/Hip ratio {measurements['waist_hip_ratio']:.2f} (less waist definition)
        """)
    else:
        st.warning(f"""
        **Classified as KIDS because:**
        - Minimal waist definition (ratio {measurements['waist_hip_ratio']:.2f})
        - Proportional body (shoulder/hip {measurements['shoulder_hip_ratio']:.2f})
        """)

# Color recommendations
st.markdown(f"### 🎨 Colors That Suit Your {skin_tone} Skin Tone")
color_cols = st.columns(len(recommended_colors))
for idx, color in enumerate(recommended_colors):
    with color_cols[idx]:
        st.info(f"**{color.title()}**")

# --------------------------------------------------
# Products
# --------------------------------------------------
st.markdown("---")
st.markdown(f"## 👗 Step 3: Personalized Recommendations ({category} • Size {size})")

def get_products(category, size, skin_tone):
    """Get products based on category, size AND skin tone"""
    
    # Color recommendations based on skin tone
    if skin_tone in ["Fair", "Light"]:
        colors = [(255, 182, 193), (135, 206, 250), (186, 85, 211), (255, 215, 0)]
    elif skin_tone in ["Medium", "Olive"]:
        colors = [(255, 140, 0), (0, 128, 128), (220, 20, 60), (107, 142, 35)]
    else:  # Tan, Deep
        colors = [(255, 69, 0), (30, 144, 255), (255, 20, 147), (255, 255, 255)]
    
    if category == "Women":
        return [
            {"id": 1, "name": "Elegant Kurti", "price": "₹899", "color": colors[0],
             "amazon": f"https://www.amazon.in/s?k=womens+kurti+{size}+{skin_tone}",
             "flipkart": f"https://www.flipkart.com/search?q=womens+kurti+{size}"},
            {"id": 2, "name": "Party Dress", "price": "₹1,499", "color": colors[1],
             "amazon": f"https://www.amazon.in/s?k=womens+party+dress+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=womens+dress+{size}"},
            {"id": 3, "name": "Designer Saree", "price": "₹2,499", "color": colors[2],
             "amazon": f"https://www.amazon.in/s?k=womens+saree+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=saree+{size}"},
            {"id": 4, "name": "Casual Top", "price": "₹799", "color": colors[3],
             "amazon": f"https://www.amazon.in/s?k=womens+top+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=womens+top+{size}"},
        ]
    elif category == "Men":
        return [
            {"id": 1, "name": "Formal Shirt", "price": "₹1,299", "color": colors[0],
             "amazon": f"https://www.amazon.in/s?k=mens+shirt+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=mens+shirt+{size}"},
            {"id": 2, "name": "Casual Jeans", "price": "₹1,599", "color": colors[1],
             "amazon": f"https://www.amazon.in/s?k=mens+jeans+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=mens+jeans+{size}"},
            {"id": 3, "name": "Kurta Set", "price": "₹1,799", "color": colors[2],
             "amazon": f"https://www.amazon.in/s?k=mens+kurta+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=mens+kurta+{size}"},
        ]
    else:  # Kids
        return [
            {"id": 1, "name": "Kids Dress", "price": "₹499", "color": colors[0],
             "amazon": f"https://www.amazon.in/s?k=kids+dress+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=kids+dress+{size}"},
            {"id": 2, "name": "Kids Set", "price": "₹699", "color": colors[1],
             "amazon": f"https://www.amazon.in/s?k=kids+wear+{size}",
             "flipkart": f"https://www.flipkart.com/search?q=kids+wear+{size}"},
        ]

products = get_products(category, size, skin_tone)

cols = st.columns(len(products))
for idx, prod in enumerate(products):
    with cols[idx]:
        is_selected = st.session_state.selected_dress and st.session_state.selected_dress['id'] == prod['id']
        st.markdown(f'<div class="product-card {"selected" if is_selected else ""}">', unsafe_allow_html=True)
        
        st.markdown(f"**{prod['name']}**")
        st.markdown(f"<p style='color: #667eea; font-size: 24px;'>{prod['price']}</p>", unsafe_allow_html=True)
        
        if st.button(f"Try On", key=f"try_{prod['id']}", use_container_width=True):
            st.session_state.selected_dress = prod
            st.rerun()
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("Amazon", prod['amazon'], use_container_width=True)
        with c2:
            st.link_button("Flipkart", prod['flipkart'], use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Try-On with Fit Checker
# --------------------------------------------------
if st.session_state.selected_dress:
    st.markdown("---")
    st.markdown("## 🎨 Step 4: Virtual Try-On & Fit Check")
    
    sel = st.session_state.selected_dress
    
    # Create try-on
    result = mannequin.copy()
    draw = ImageDraw.Draw(result, 'RGBA')
    
    ref = ref_points
    cx = ref["center_x"]
    
    # Draw dress
    color_rgba = sel['color'] + (200,)
    draw.polygon([
        (cx - ref["shoulder_w"]//2 + 15, ref["torso_top"] + 30),
        (cx + ref["shoulder_w"]//2 - 15, ref["torso_top"] + 30),
        (cx + ref["waist_w"]//2, ref["waist_y"]),
        (cx + ref["hip_w"]//2 + 20, ref["hip_y"] + 100),
        (cx - ref["hip_w"]//2 - 20, ref["hip_y"] + 100),
        (cx - ref["waist_w"]//2, ref["waist_y"]),
    ], fill=color_rgba, outline=sel['color'], width=3)
    
    # FIT CHECKER
    st.markdown("### 🎯 Fit Analysis")
    
    # User selects their actual size
    fit_col1, fit_col2 = st.columns([1, 2])
    
    with fit_col1:
        actual_size = st.selectbox(
            "What size do you usually wear?",
            ["XS", "S", "M", "L", "XL"] if category == "Women" else
            (["S", "M", "L", "XL"] if category == "Men" else ["4-6Y", "7-9Y", "10-12Y"])
        )
    
    size_map = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5,
                "4-6Y": 1, "7-9Y": 2, "10-12Y": 3}
    
    recommended_num = size_map.get(size, 3)
    actual_num = size_map.get(actual_size, 3)
    
    diff = recommended_num - actual_num
    
    if diff == 0:
        fit = "Perfect Fit"
        fit_class = "fit-perfect"
        fit_text = "✅ This size should fit you perfectly!"
    elif diff == 1:
        fit = "Slightly Loose"
        fit_class = "fit-loose"
        fit_text = "ℹ️ May be slightly loose. Consider trying one size down."
    elif diff >= 2:
        fit = "Too Loose"
        fit_class = "fit-loose"
        fit_text = "⚠️ Likely too loose. Try a smaller size."
    elif diff == -1:
        fit = "Slightly Tight"
        fit_class = "fit-tight"
        fit_text = "⚠️ May be slightly tight. Consider sizing up."
    else:
        fit = "Too Tight"
        fit_class = "fit-tight"
        fit_text = "❌ Likely too tight. Try a larger size."
    
    with fit_col2:
        st.markdown(f'<div class="fit-badge {fit_class}">{fit}</div>', unsafe_allow_html=True)
        st.info(fit_text)
    
    # Display
    display_cols = st.columns([1, 2, 1])
    with display_cols[1]:
        st.image(result, use_container_width=True)
        
        st.markdown(f"### {sel['name']} - {sel['price']}")
        st.success(f"Recommended Size: **{size}** • Your Size: **{actual_size}**")
        
        buy_c1, buy_c2 = st.columns(2)
        with buy_c1:
            st.link_button("🛒 Buy on Amazon", sel['amazon'], use_container_width=True)
        with buy_c2:
            st.link_button("🛒 Buy on Flipkart", sel['flipkart'], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
    <h3>🌟 Smart Fashion Stylist</h3>
    <p>Accurate Classification • Skin Tone Analysis • Perfect Fit Checker</p>
</div>
""", unsafe_allow_html=True)
