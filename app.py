import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont
import io
import math

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="3D Toy Fashion Stylist",
    page_icon="🧸",
    layout="wide"
)

# ==================================================
# ENHANCED CSS
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
    
    .measurement-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px solid #667eea;
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
        position: relative;
    }
    
    .product-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.5);
        border-color: #667eea;
    }
    
    .product-card.selected {
        border: 5px solid #28a745;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        box-shadow: 0 15px 40px rgba(40, 167, 69, 0.6);
    }
    
    .trying-on-label {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .color-recommendation {
        display: inline-block;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0.5rem;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
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
    <h1>🧸 3D Toy Fashion Stylist</h1>
    <p style="font-size: 1.3rem;">
        3D Rotating Mannequin • Skin Tone Color Match • Virtual Try-On
    </p>
</div>
''', unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
for key in ['selected_dress', 'user_category', 'size', 'skin_tone',  
            'uploaded_dress_color', 'body_type', 'measurements', 'hair_color',
            'recommended_colors', 'rotation_angle', 'toy_mannequin', 'ref_points']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.rotation_angle is None:
    st.session_state.rotation_angle = 0

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.header("🧸 3D Toy Features")
    st.success("""
    **✅ NEW Features:**
    
    🧸 **3D Toy Mannequin**
    - Realistic joints & segments
    - Smooth shading
    - Toy-like appearance
    
    🔄 **360° Rotation**
    - Smooth rotation slider
    - See from all angles
    - Real-time updates
    
    🎨 **Smart Color Match**
    - Based on skin tone
    - Personalized recommendations
    - Copy dress link feature
    
    👗 **Virtual Try-On**
    - On rotating mannequin
    - Clear visualization
    """)

# ==================================================
# STEP 1: UPLOAD
# ==================================================
st.markdown("## 📤 Step 1: Upload Your Photo")

uploaded_body = st.file_uploader(
    "Upload clear full-body photo",
    type=["jpg", "jpeg", "png"],
    key="body"
)

if not uploaded_body:
    st.info("👆 Upload your photo to create 3D toy mannequin!")
    st.stop()

# ==================================================
# STEP 1.5: USER SELECTS CATEGORY
# ==================================================
st.markdown("---")
st.markdown("## 🎯 Step 1.5: Select Your Category")

category_cols = st.columns(3)

with category_cols[0]:
    if st.button("👶 KIDS", use_container_width=True, type="primary" if st.session_state.user_category == "Kids" else "secondary"):
        st.session_state.user_category = "Kids"
        st.rerun()

with category_cols[1]:
    if st.button("👨 MEN", use_container_width=True, type="primary" if st.session_state.user_category == "Men" else "secondary"):
        st.session_state.user_category = "Men"
        st.rerun()

with category_cols[2]:
    if st.button("👩 WOMEN", use_container_width=True, type="primary" if st.session_state.user_category == "Women" else "secondary"):
        st.session_state.user_category = "Women"
        st.rerun()

if not st.session_state.user_category:
    st.warning("⚠️ Please select your category!")
    st.stop()

category = st.session_state.user_category
st.success(f"✅ Selected: **{category}**")

# ==================================================
# STEP 2: ANALYSIS & 3D TOY MANNEQUIN CREATION
# ==================================================
original = Image.open(uploaded_body).convert("RGB")
img_w, img_h = original.size
img_array = np.array(original)

st.markdown("---")
st.markdown("## 🔬 Step 2: Creating 3D Toy Mannequin")

with st.spinner("🧸 Building 3D toy mannequin..."):
    
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
    draw_det = ImageDraw.Draw(detected)
    draw_det.rectangle([cmin, rmin, cmax, rmax], outline="lime", width=6)
    
    with analysis_cols[1]:
        st.markdown("### 🎯 Detection")
        st.image(detected, use_container_width=True)
    
    # Measurements
    if category == "Women":
        avg_height_cm = 162
    elif category == "Men":
        avg_height_cm = 175
    else:
        avg_height_cm = 120
    
    px_to_cm = avg_height_cm / body_h
    
    measurements = {
        "height_cm": round(body_h * px_to_cm, 1),
        "shoulder_cm": round(body_w * 0.42 * px_to_cm, 1),
        "chest_cm": round(body_w * 0.45 * px_to_cm, 1),
        "waist_cm": round(body_w * 0.38 * px_to_cm, 1),
        "hip_cm": round(body_w * 0.44 * px_to_cm, 1),
        "shoulder_hip_ratio": (body_w * 0.42) / (body_w * 0.44),
        "waist_hip_ratio": (body_w * 0.38) / (body_w * 0.44),
    }
    
    st.session_state.measurements = measurements
    
    # Size detection
    body_pct = (body_w * 0.42 + body_w * 0.38 + body_w * 0.44) / (3 * body_w)
    
    if category == "Kids":
        coverage = body_h / img_h
        size = "4-6Y" if coverage < 0.50 else ("7-9Y" if coverage < 0.65 else "10-12Y")
    elif category == "Men":
        size = "S" if body_pct < 0.38 else ("M" if body_pct < 0.44 else ("L" if body_pct < 0.50 else "XL"))
    else:
        size = "XS" if body_pct < 0.36 else ("S" if body_pct < 0.41 else ("M" if body_pct < 0.47 else ("L" if body_pct < 0.53 else "XL")))
    
    st.session_state.size = size
    
    # Skin tone
    face_region = img_array[rmin:rmin+int(body_h*0.25), cmin:cmax]
    brightness = np.mean(face_region) if face_region.size > 0 else 150
    
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
    
    st.session_state.skin_tone = skin_tone
    
    # ==================================================
    # CREATE 3D TOY MANNEQUIN WITH ROTATION
    # ==================================================
    
    def create_rotatable_toy_mannequin(body_w, body_h, category, rotation_angle):
        """Create 3D toy mannequin that rotates"""
        
        canvas_h, canvas_w = 700, 400
        mannequin = Image.new('RGB', (canvas_w, canvas_h), (245, 245, 250))
        draw = ImageDraw.Draw(mannequin)
        
        center_x = canvas_w // 2
        
        # Calculate rotation (0° = front, 90° = side, 180° = back, 270° = side)
        angle_rad = math.radians(rotation_angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Width scaling based on angle (front=full, side=narrow)
        width_scale = abs(cos_angle)
        depth_scale = abs(sin_angle)
        
        # Toy dimensions
        if category == "Kids":
            head_r = 25
            torso_h, torso_w = 180, int(body_w * 0.45 * width_scale)
            leg_h, leg_w = 120, int(body_w * 0.20 * width_scale)
        elif category == "Men":
            head_r = 22
            torso_h, torso_w = 200, int(body_w * 0.50 * width_scale)
            leg_h, leg_w = 180, int(body_w * 0.22 * width_scale)
        else:
            head_r = 21
            torso_h, torso_w = 190, int(body_w * 0.45 * width_scale)
            leg_h, leg_w = 170, int(body_w * 0.20 * width_scale)
        
        # Skin color (toy-like)
        skin = (245, 220, 200)
        
        y = 50
        
        # HEAD
        for i in range(head_r * 2):
            prog = i / (head_r * 2)
            r = int(head_r * math.sin(prog * math.pi))
            shade = int(245 + 10 * (1 - abs(0.5 - prog) * 2))
            color = tuple(min(255, c + shade - 245) for c in skin)
            draw.ellipse([center_x - r, y + i, center_x + r, y + i + 2], fill=color)
        
        y += head_r * 2
        
        # NECK
        neck_h = 15
        neck_w = int(head_r * 0.6 * width_scale)
        for i in range(neck_h):
            draw.rectangle([center_x - neck_w, y + i, center_x + neck_w, y + i + 1], fill=tuple(max(0, c - 20) for c in skin))
        
        y += neck_h
        
        # TORSO with 3D shading
        torso_top = y
        for i in range(torso_h):
            prog = i / torso_h
            # Waist narrowing
            w_factor = 1.0 if prog < 0.3 else (0.85 if prog < 0.6 else 0.95)
            curr_w = int(torso_w * w_factor)
            
            for j in range(-curr_w, curr_w + 1):
                dist = abs(j) / curr_w if curr_w > 0 else 0
                shade = 1.0 - (dist * 0.2)
                lighting = 1.0 - (abs(sin_angle) * 0.15)
                
                color = tuple(int(c * shade * lighting) for c in skin)
                draw.point((center_x + j, y + i), fill=color)
        
        y += torso_h
        
        # LEGS
        leg_gap = int(torso_w * 0.25)
        for leg_x in [center_x - leg_gap, center_x + leg_gap]:
            for i in range(leg_h):
                shade = 1.0 - (abs(sin_angle) * 0.2)
                color = tuple(int(c * shade) for c in skin)
                draw.rectangle([leg_x - leg_w, y + i, leg_x + leg_w, y + i + 1], fill=color)
        
        # Reference points
        ref = {
            'torso_top': torso_top,
            'torso_h': torso_h,
            'torso_w': torso_w,
            'center_x': center_x,
            'angle': rotation_angle,
            'width_scale': width_scale
        }
        
        return mannequin, ref
    
    toy_mannequin, ref_points = create_rotatable_toy_mannequin(body_w, body_h, category, st.session_state.rotation_angle)
    st.session_state.toy_mannequin = toy_mannequin
    st.session_state.ref_points = ref_points
    
    with analysis_cols[2]:
        st.markdown("### 🧸 3D Toy")
        st.image(toy_mannequin, use_container_width=True)
        st.caption(f"Angle: {st.session_state.rotation_angle}°")

# ==================================================
# STEP 3: 360° ROTATION CONTROL
# ==================================================
st.markdown("---")
st.markdown("## 🔄 Step 3: Rotate Your 3D Toy Mannequin")

rotation_cols = st.columns([1, 3, 1])

with rotation_cols[1]:
    new_angle = st.slider(
        "Rotate 360°",
        min_value=0,
        max_value=360,
        value=st.session_state.rotation_angle,
        step=15,
        key="rotation_slider"
    )
    
    if new_angle != st.session_state.rotation_angle:
        st.session_state.rotation_angle = new_angle
        # Recreate mannequin with new angle
        toy_mannequin, ref_points = create_rotatable_toy_mannequin(body_w, body_h, category, new_angle)
        st.session_state.toy_mannequin = toy_mannequin
        st.session_state.ref_points = ref_points
        st.rerun()

rotation_display = st.columns([1, 2, 1])

with rotation_display[1]:
    st.image(st.session_state.toy_mannequin, use_container_width=True)
    
    angle_desc = "Front View" if new_angle < 45 or new_angle > 315 else (
        "Right Side" if 45 <= new_angle < 135 else (
            "Back View" if 135 <= new_angle < 225 else "Left Side"
        )
    )
    
    st.success(f"🎯 **{angle_desc}** • Angle: {new_angle}°")

# ==================================================
# STEP 4: COLOR RECOMMENDATIONS BASED ON SKIN TONE
# ==================================================
st.markdown("---")
st.markdown(f"## 🎨 Step 4: Color Recommendations for {skin_tone} Skin")

def get_color_recommendations(skin_tone):
    """Get color recommendations based on skin tone"""
    
    recommendations = {
        "Fair": {
            "best": [
                ("Powder Blue", (176, 224, 230)),
                ("Soft Pink", (255, 192, 203)),
                ("Lavender", (230, 230, 250)),
                ("Mint Green", (189, 252, 201)),
                ("Peach", (255, 218, 185))
            ],
            "avoid": ["Neon colors", "Very dark browns"]
        },
        "Light": {
            "best": [
                ("Coral", (255, 127, 80)),
                ("Aqua", (127, 255, 212)),
                ("Blush Pink", (255, 182, 193)),
                ("Sky Blue", (135, 206, 235)),
                ("Champagne", (247, 231, 206))
            ],
            "avoid": ["Pale yellows", "Washed out pastels"]
        },
        "Medium": {
            "best": [
                ("Olive Green", (128, 128, 0)),
                ("Rust Orange", (183, 65, 14)),
                ("Navy Blue", (0, 0, 128)),
                ("Burgundy", (128, 0, 32)),
                ("Mustard", (255, 219, 88))
            ],
            "avoid": ["Muddy browns"]
        },
        "Tan": {
            "best": [
                ("Emerald Green", (80, 200, 120)),
                ("Crimson", (220, 20, 60)),
                ("Royal Blue", (65, 105, 225)),
                ("Gold", (255, 215, 0)),
                ("Deep Purple", (102, 51, 153))
            ],
            "avoid": ["Pale pastels"]
        },
        "Deep": {
            "best": [
                ("White", (255, 255, 255)),
                ("Bright Red", (255, 0, 0)),
                ("Electric Blue", (125, 249, 255)),
                ("Hot Pink", (255, 105, 180)),
                ("Lime Green", (50, 205, 50))
            ],
            "avoid": ["Dark muddy colors"]
        }
    }
    
    return recommendations.get(skin_tone, recommendations["Medium"])

color_recs = get_color_recommendations(skin_tone)
st.session_state.recommended_colors = color_recs

st.markdown(f"""
<div class="measurement-box">
    <h3 style="color: #667eea;">🎨 Perfect Colors for {skin_tone} Skin Tone</h3>
    <p style="font-size: 1.1rem; margin: 1rem 0;">
        Based on color theory and your skin tone analysis, these colors will look amazing on you!
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### ✨ Recommended Colors")

color_cols = st.columns(5)

for idx, (color_name, color_rgb) in enumerate(color_recs["best"]):
    with color_cols[idx]:
        st.markdown(f'''
        <div style="text-align: center;">
            <div class="color-recommendation" style="background: rgb{color_rgb};"></div>
            <p style="font-weight: 600; margin-top: 0.5rem;">{color_name}</p>
        </div>
        ''', unsafe_allow_html=True)

st.warning(f"⚠️ **Colors to Avoid:** {', '.join(color_recs['avoid'])}")

# ==================================================
# STEP 5: PRODUCT RECOMMENDATIONS (Generic Links)
# ==================================================
st.markdown("---")
st.markdown(f"## 🛍️ Step 5: Product Recommendations ({category} • Size {size})")

st.info("""
💡 **How to Try Any Dress:**
1. Browse recommendations below (or search on Amazon/Flipkart)
2. Find a dress you like
3. **Right-click → Copy image** OR **Download the dress image**
4. Upload it in Step 6 below
5. See it on your 3D toy mannequin!
""")

def get_products_by_color(category, size, recommended_colors):
    """Generate products based on recommended colors"""
    
    products = []
    color_list = recommended_colors["best"]
    
    for idx, (color_name, color_rgb) in enumerate(color_list[:3]):  # Top 3 colors
        
        if category == "Women":
            product_types = ["Kurti", "Dress", "Saree"]
            product = {
                "id": idx + 1,
                "name": f"{color_name} {product_types[idx]}",
                "color": color_rgb,
                "color_name": color_name,
                "price": f"₹{899 + idx * 200}",
                "size": size,
                # Generic search links (not specific products)
                "amazon": f"https://www.amazon.in/s?k=womens+{product_types[idx].lower()}+{color_name.lower().replace(' ', '+')}+size+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+{product_types[idx].lower()}+{color_name.lower().replace(' ', '+')}+{size}"
            }
        elif category == "Men":
            product_types = ["Shirt", "T-Shirt", "Kurta"]
            product = {
                "id": idx + 1,
                "name": f"{color_name} {product_types[idx]}",
                "color": color_rgb,
                "color_name": color_name,
                "price": f"₹{1299 + idx * 300}",
                "size": size,
                "amazon": f"https://www.amazon.in/s?k=mens+{product_types[idx].lower()}+{color_name.lower().replace(' ', '+')}+size+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+{product_types[idx].lower()}+{color_name.lower().replace(' ', '+')}+{size}"
            }
        else:  # Kids
            product_types = ["T-Shirt", "Dress", "Set"]
            product = {
                "id": idx + 1,
                "name": f"{color_name} Kids {product_types[idx]}",
                "color": color_rgb,
                "color_name": color_name,
                "price": f"₹{499 + idx * 100}",
                "size": size,
                "amazon": f"https://www.amazon.in/s?k=kids+{product_types[idx].lower()}+{color_name.lower().replace(' ', '+')}+age+{size.replace('Y', '+years')}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+{product_types[idx].lower()}+{color_name.lower().replace(' ', '+')}+{size}"
            }
        
        products.append(product)
    
    return products

products = get_products_by_color(category, size, color_recs)

prod_cols = st.columns(3)

for idx, prod in enumerate(products):
    with prod_cols[idx]:
        is_selected = st.session_state.selected_dress and st.session_state.selected_dress['id'] == prod['id']
        
        st.markdown(f'<div class="product-card {"selected" if is_selected else ""}">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div style="width: 100%; height: 200px; background: rgb{prod["color"]}; 
                    border-radius: 12px; margin-bottom: 1rem; display: flex; 
                    align-items: center; justify-content: center; font-size: 3rem;">
            👗
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f"### {prod['name']}")
        st.caption(f"**Color:** {prod['color_name']}")
        st.caption(f"**Perfect for {skin_tone} skin!**")
        st.markdown(f"<p style='color: #667eea; font-size: 1.5rem; font-weight: bold;'>{prod['price']}</p>", unsafe_allow_html=True)
        
        if st.button(f"👗 Try This Color", key=f"try_{prod['id']}", use_container_width=True):
            st.session_state.selected_dress = prod
            st.rerun()
        
        st.markdown("**🔗 Browse Similar Products:**")
        st.link_button("🛒 Amazon", prod['amazon'], use_container_width=True)
        st.link_button("🛒 Flipkart", prod['flipkart'], use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# STEP 6: UPLOAD ANY DRESS IMAGE FOR TRY-ON
# ==================================================
st.markdown("---")
st.markdown("## 🖼️ Step 6: Upload ANY Dress Image to Try On")

st.markdown("""
<div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
            padding: 1.5rem; border-radius: 12px; border-left: 5px solid #ffc107; margin: 1rem 0;">
    <h3 style="margin-top: 0; color: #856404;">📋 Instructions:</h3>
    <ol style="font-size: 1.05rem; line-height: 1.8;">
        <li>Click on Amazon/Flipkart links above to browse dresses</li>
        <li>Find a dress you like</li>
        <li><strong>Right-click on the dress image → "Save image as..."</strong></li>
        <li>Upload the saved image below</li>
        <li>See it instantly on your 3D toy mannequin! 🎉</li>
    </ol>
    <p style="margin-bottom: 0; color: #856404; font-weight: 600;">
        💡 Works with ANY dress image from ANY website!
    </p>
</div>
""", unsafe_allow_html=True)

upload_dress_cols = st.columns([1, 2, 1])

with upload_dress_cols[1]:
    st.markdown("### 📤 Upload Dress Image")
    
    uploaded_dress = st.file_uploader(
        "Choose a dress image to try on",
        type=["jpg", "jpeg", "png"],
        key="dress_upload",
        help="Upload any dress image from Amazon, Flipkart, or any website"
    )
    
    if uploaded_dress:
        dress_img = Image.open(uploaded_dress).convert("RGB")
        
        # Show uploaded dress
        st.image(dress_img, caption="Your Selected Dress", use_container_width=True)
        
        # Extract dominant color from dress
        dress_array = np.array(dress_img)
        h, w = dress_array.shape[:2]
        
        # Sample center region (avoid background)
        center_region = dress_array[h//4:3*h//4, w//4:3*w//4]
        
        # Get median color (more robust than mean)
        dress_r = int(np.median(center_region[:,:,0]))
        dress_g = int(np.median(center_region[:,:,1]))
        dress_b = int(np.median(center_region[:,:,2]))
        
        dress_color = (dress_r, dress_g, dress_b)
        
        # Color analysis
        brightness = (dress_r + dress_g + dress_b) / 3
        
        if dress_r > dress_g and dress_r > dress_b:
            color_family = "Red/Pink"
        elif dress_g > dress_r and dress_g > dress_b:
            color_family = "Green"
        elif dress_b > dress_r and dress_b > dress_g:
            color_family = "Blue"
        elif dress_r > 200 and dress_g > 200 and dress_b > 200:
            color_family = "White/Light"
        elif dress_r < 50 and dress_g < 50 and dress_b < 50:
            color_family = "Black/Dark"
        else:
            color_family = "Mixed"
        
        st.success(f"✅ **Color Extracted:** {color_family}")
        
        # Show color swatch
        st.markdown(f'''
        <div style="text-align: center; margin: 1rem 0;">
            <div style="display: inline-block; width: 100px; height: 100px; 
                        background: rgb({dress_r}, {dress_g}, {dress_b}); 
                        border-radius: 12px; border: 4px solid #667eea;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);"></div>
            <p style="margin-top: 0.5rem; font-weight: 600;">RGB({dress_r}, {dress_g}, {dress_b})</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Check if it's a recommended color
        is_recommended = False
        for rec_name, rec_color in color_recs["best"]:
            # Check if colors are similar (within 50 units for each channel)
            if (abs(rec_color[0] - dress_r) < 50 and 
                abs(rec_color[1] - dress_g) < 50 and 
                abs(rec_color[2] - dress_b) < 50):
                is_recommended = True
                st.success(f"🌟 **Great choice!** This color matches our recommendation: {rec_name}")
                break
        
        if not is_recommended:
            st.info(f"💡 This color wasn't in our top recommendations, but it might still look great on you!")
        
        # Store for try-on
        st.session_state.uploaded_dress_color = dress_color
        st.session_state.selected_dress = {
            'id': 999,
            'name': 'Your Uploaded Dress',
            'color': dress_color,
            'color_name': color_family,
            'from_upload': True
        }

# ==================================================
# STEP 7: VIRTUAL TRY-ON ON 3D TOY
# ==================================================
if st.session_state.selected_dress:
    st.markdown("---")
    st.markdown("## 🎨 Step 7: Virtual Try-On (On 3D Toy Mannequin)")
    
    sel = st.session_state.selected_dress
    
    # Check if it's uploaded dress or recommended color
    if sel.get('from_upload', False):
        st.markdown(f"""
        <div class="trying-on-label">
            🎯 TRYING ON: Your Uploaded Dress ({sel['color_name']})
            <br>
            <span style="font-size: 1rem;">✅ Custom dress from your selection!</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="trying-on-label">
            🎯 TRYING ON: {sel['name']} ({sel['color_name']})
            <br>
            <span style="font-size: 1rem;">✨ Recommended color for {skin_tone} skin</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Apply dress to toy mannequin
    def apply_dress_to_toy(toy_mannequin, ref_points, dress_color):
        """Apply dress to 3D toy mannequin"""
        
        result = toy_mannequin.copy()
        draw = ImageDraw.Draw(result)
        
        torso_top = ref_points['torso_top']
        torso_h = ref_points['torso_h']
        torso_w = ref_points['torso_w']
        center_x = ref_points['center_x']
        width_scale = ref_points['width_scale']
        
        dress_h = int(torso_h * 0.75)
        
        # Draw dress with 3D shading
        for i in range(dress_h):
            prog = i / dress_h
            w_factor = 1.0 if prog < 0.3 else 0.9
            curr_w = int(torso_w * w_factor)
            
            for j in range(-curr_w, curr_w + 1):
                dist = abs(j) / curr_w if curr_w > 0 else 0
                shade = (1.0 - dist * 0.3) * (0.7 + width_scale * 0.3)
                
                color = tuple(int(c * shade) for c in dress_color)
                
                y = torso_top + i
                x = center_x + j
                
                if 0 <= x < result.width and 0 <= y < result.height:
                    draw.point((x, y), fill=color)
        
        # Neckline (darker shade)
        neck_y = torso_top
        neck_color = tuple(int(c * 0.6) for c in dress_color)
        for i in range(12):
            neck_w = int(torso_w * 0.5)
            draw.rectangle([
                center_x - neck_w, neck_y + i,
                center_x + neck_w, neck_y + i + 1
            ], fill=neck_color)
        
        # Sleeves (short sleeves)
        sleeve_y = torso_top + 15
        sleeve_h = int(torso_h * 0.15)
        sleeve_color = tuple(int(c * 0.8) for c in dress_color)
        
        # Left sleeve
        left_sleeve_x = center_x - torso_w - 5
        for i in range(sleeve_h):
            draw.ellipse([
                left_sleeve_x - 15, sleeve_y + i,
                left_sleeve_x + 15, sleeve_y + i + 2
            ], fill=sleeve_color)
        
        # Right sleeve
        right_sleeve_x = center_x + torso_w + 5
        for i in range(sleeve_h):
            draw.ellipse([
                right_sleeve_x - 15, sleeve_y + i,
                right_sleeve_x + 15, sleeve_y + i + 2
            ], fill=sleeve_color)
        
        # Hem (decorative border)
        hem_y = torso_top + dress_h
        hem_color = tuple(int(c * 0.75) for c in dress_color)
        for i in range(8):
            draw.rectangle([
                center_x - torso_w, hem_y + i,
                center_x + torso_w, hem_y + i + 1
            ], fill=hem_color)
        
        # Add decorative dots on hem
        for j in range(center_x - torso_w, center_x + torso_w, 15):
            draw.ellipse([j - 2, hem_y + 3, j + 2, hem_y + 7], fill=(255, 215, 0))
        
        return result
    
    tryon_result = apply_dress_to_toy(st.session_state.toy_mannequin, st.session_state.ref_points, sel['color'])
    
    display_cols = st.columns([1, 2, 1])
    
    with display_cols[1]:
        st.image(tryon_result, use_container_width=True)
        
        st.success(f"✅ **Dress successfully applied to your 3D toy mannequin!**")
        
        # Show details
        if sel.get('from_upload', False):
            st.info(f"""
            🎨 **Your Uploaded Dress**
            - Color Family: {sel['color_name']}
            - RGB: {sel['color']}
            - Applied to your body structure
            """)
        else:
            st.info(f"""
            🎨 **{sel['name']}**
            - Color: {sel['color_name']} (Perfect for {skin_tone} skin)
            - Size: {size} (Based on your measurements)
            """)
        
        # Rotation controls
        st.markdown("### 🔄 Rotate to See Different Angles")
        
        quick_rotate_cols = st.columns(4)
        with quick_rotate_cols[0]:
            if st.button("⬅️ Left (270°)", use_container_width=True):
                st.session_state.rotation_angle = 270
                toy_mannequin, ref_points = create_rotatable_toy_mannequin(body_w, body_h, category, 270)
                st.session_state.toy_mannequin = toy_mannequin
                st.session_state.ref_points = ref_points
                st.rerun()
        
        with quick_rotate_cols[1]:
            if st.button("⬆️ Front (0°)", use_container_width=True):
                st.session_state.rotation_angle = 0
                toy_mannequin, ref_points = create_rotatable_toy_mannequin(body_w, body_h, category, 0)
                st.session_state.toy_mannequin = toy_mannequin
                st.session_state.ref_points = ref_points
                st.rerun()
        
        with quick_rotate_cols[2]:
            if st.button("⬇️ Back (180°)", use_container_width=True):
                st.session_state.rotation_angle = 180
                toy_mannequin, ref_points = create_rotatable_toy_mannequin(body_w, body_h, category, 180)
                st.session_state.toy_mannequin = toy_mannequin
                st.session_state.ref_points = ref_points
                st.rerun()
        
        with quick_rotate_cols[3]:
            if st.button("➡️ Right (90°)", use_container_width=True):
                st.session_state.rotation_angle = 90
                toy_mannequin, ref_points = create_rotatable_toy_mannequin(body_w, body_h, category, 90)
                st.session_state.toy_mannequin = toy_mannequin
                st.session_state.ref_points = ref_points
                st.rerun()
        
        st.warning("💡 **Tip:** Scroll up to Step 3 to use the slider for precise rotation!")
        
        # Download
        st.markdown("---")
        buf = io.BytesIO()
        tryon_result.save(buf, format='PNG')
        st.download_button(
            "⬇️ Download Try-On Image",
            buf.getvalue(),
            f"3d_toy_tryon_{sel['color_name'].replace(' ', '_')}.png",
            "image/png",
            use_container_width=True
        )
        
        # Try another dress
        if st.button("🔄 Try Another Dress", use_container_width=True, type="secondary"):
            st.session_state.selected_dress = None
            st.session_state.uploaded_dress_color = None
            st.rerun()

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown('''
<div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 20px; color: white;">
    <h2>🧸 3D Toy Fashion Stylist</h2>
    <p style="font-size: 1.2rem;">
        ✅ 3D Rotating Mannequin • ✅ Skin Tone Color Match • ✅ Virtual Try-On
    </p>
</div>
''', unsafe_allow_html=True)
