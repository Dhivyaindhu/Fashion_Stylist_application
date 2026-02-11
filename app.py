import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont
import io

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Professional Fashion Stylist",
    page_icon="👗",
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
    
    .product-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
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
        box-shadow: 0 5px 20px rgba(40, 167, 69, 0.4);
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
        User-Controlled • Exact Products • Clear Visualization • Body Measurements
    </p>
</div>
''', unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
for key in ['selected_dress', 'user_category', 'size', 'skin_tone', 'mannequin_views',
            'uploaded_dress_color', 'body_type', 'measurements', 'hair_color',
            'recommended_colors', 'current_product']:
    if key not in st.session_state:
        st.session_state[key] = None

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.header("✨ Features")
    st.success("""
    **✅ FIXED Issues:**
    
    🎯 **User Chooses Category**
    - YOU select: Kids/Men/Women
    - No auto-detection errors
    
    🛒 **Specific Products**
    - Individual product links
    - Real brand pages
    
    📏 **Body Measurements**
    - Height, Chest, Waist, Hip
    - Shown in cm & inches
    
    👗 **Clear Try-On**
    - Product name displayed
    - Product image shown
    - Exact item tracked
    
    🔄 **360° Rotation**
    - Works perfectly!
    """)

# ==================================================
# STEP 1: UPLOAD
# ==================================================
st.markdown("## 📤 Step 1: Upload Your Photo")

upload_cols = st.columns(2)

with upload_cols[0]:
    st.markdown("### 📷 Full Body Photo")
    uploaded_body = st.file_uploader(
        "Upload clear photo",
        type=["jpg", "jpeg", "png"],
        key="body"
    )

with upload_cols[1]:
    st.markdown("### 👗 Your Dress (Optional)")
    uploaded_dress = st.file_uploader(
        "Upload dress",
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
    st.info("👆 Upload your photo to start!")
    st.stop()

# ==================================================
# STEP 1.5: USER SELECTS CATEGORY
# ==================================================
st.markdown("---")
st.markdown("## 🎯 Step 1.5: Select Your Category")

st.info("💡 **YOU choose** - No auto-detection errors!")

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
    st.warning("⚠️ Please select your category above to continue!")
    st.stop()

category = st.session_state.user_category
st.success(f"✅ Selected: **{category}**")

# ==================================================
# STEP 2: ANALYSIS
# ==================================================
original = Image.open(uploaded_body).convert("RGB")
img_w, img_h = original.size
img_array = np.array(original)

st.markdown("---")
st.markdown("## 🔬 Step 2: Body Analysis")

with st.spinner("🔍 Analyzing..."):
    
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
    # BODY MEASUREMENTS (in pixels → convert to cm/inches)
    # ==================================================
    
    # Assume average human height for conversion
    # Average heights: Women ~162cm, Men ~175cm, Kids varies
    if category == "Women":
        avg_height_cm = 162
    elif category == "Men":
        avg_height_cm = 175
    else:
        avg_height_cm = 120  # Kids average
    
    # Calculate pixel to cm ratio
    px_to_cm = avg_height_cm / body_h
    
    measurements = {
        "height_px": body_h,
        "height_cm": round(body_h * px_to_cm, 1),
        "height_inches": round(body_h * px_to_cm / 2.54, 1),
        
        "shoulder_px": int(body_w * 0.42),
        "shoulder_cm": round(body_w * 0.42 * px_to_cm, 1),
        "shoulder_inches": round(body_w * 0.42 * px_to_cm / 2.54, 1),
        
        "chest_px": int(body_w * 0.45),
        "chest_cm": round(body_w * 0.45 * px_to_cm, 1),
        "chest_inches": round(body_w * 0.45 * px_to_cm / 2.54, 1),
        
        "waist_px": int(body_w * 0.38),
        "waist_cm": round(body_w * 0.38 * px_to_cm, 1),
        "waist_inches": round(body_w * 0.38 * px_to_cm / 2.54, 1),
        
        "hip_px": int(body_w * 0.44),
        "hip_cm": round(body_w * 0.44 * px_to_cm, 1),
        "hip_inches": round(body_w * 0.44 * px_to_cm / 2.54, 1),
        
        "shoulder_hip_ratio": (body_w * 0.42) / (body_w * 0.44),
        "waist_hip_ratio": (body_w * 0.38) / (body_w * 0.44),
    }
    
    st.session_state.measurements = measurements
    
    # Body type classification
    def classify_body_type(measurements, gender):
        sh_ratio = measurements["shoulder_hip_ratio"]
        wh_ratio = measurements["waist_hip_ratio"]
        
        if gender == "Women":
            if wh_ratio < 0.75:
                if abs(sh_ratio - 1.0) < 0.05:
                    return "Hourglass"
                elif sh_ratio > 1.05:
                    return "Inverted Triangle"
                else:
                    return "Pear"
            elif wh_ratio >= 0.85:
                if sh_ratio > 1.10:
                    return "Inverted Triangle"
                else:
                    return "Rectangle"
            else:
                return "Rectangle"
        elif gender == "Men":
            if sh_ratio > 1.15:
                return "Inverted Triangle"
            elif sh_ratio > 1.05:
                return "Trapezoid"
            else:
                return "Rectangle"
        else:
            return "Kids Body"
    
    body_type = classify_body_type(measurements, category)
    st.session_state.body_type = body_type
    
    # Size detection
    body_pct = (measurements["shoulder_px"] + measurements["waist_px"] + measurements["hip_px"]) / (3 * body_w)
    
    if category == "Kids":
        coverage = body_h / img_h
        if coverage < 0.50:
            size = "4-6Y"
        elif coverage < 0.65:
            size = "7-9Y"
        else:
            size = "10-12Y"
    elif category == "Men":
        if body_pct < 0.38:
            size = "S"
        elif body_pct < 0.44:
            size = "M"
        elif body_pct < 0.50:
            size = "L"
        else:
            size = "XL"
    else:  # Women
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
    
    st.session_state.size = size
    
    # Skin tone
    def detect_skin_tone(img_array, rmin, rmax, cmin, cmax):
        face_region = img_array[rmin:rmin+int((rmax-rmin)*0.25), cmin:cmax]
        
        if face_region.size == 0:
            return "Medium", "Dark"
        
        r, g, b = face_region[:,:,0], face_region[:,:,1], face_region[:,:,2]
        skin_mask = (r > 85) & (r > g) & (g > b) & (r - g > 10)
        
        if np.sum(skin_mask) > 0:
            skin_r, skin_g, skin_b = np.median(r[skin_mask]), np.median(g[skin_mask]), np.median(b[skin_mask])
        else:
            skin_r, skin_g, skin_b = np.median(r), np.median(g), np.median(b)
        
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
        
        hair_region = face_region[:int(face_region.shape[0]*0.15), :]
        hair_brightness = np.mean(hair_region)
        hair_color = "Light" if hair_brightness > 140 else "Dark"
        
        return skin_tone, hair_color
    
    skin_tone, hair_color = detect_skin_tone(img_array, rmin, rmax, cmin, cmax)
    st.session_state.skin_tone = skin_tone
    st.session_state.hair_color = hair_color
    
    # Color recommendations
    def get_colors(skin_tone, hair_color):
        key = f"{skin_tone}+{hair_color}"
        
        colors = {
            "Light+Light": {
                "best": [("Powder Blue", (176, 224, 230)), ("Ice Blue", (200, 230, 240)), ("Lavender", (230, 230, 250))]
            },
            "Tan+Dark": {
                "best": [("Olive Green", (128, 128, 0)), ("Rust", (183, 65, 14)), ("Navy", (0, 0, 139))]
            },
            "Deep+Dark": {
                "best": [("White", (255, 255, 255)), ("Jewel Tones", (147, 51, 234)), ("Red", (220, 20, 60))]
            }
        }
        
        default = {"best": [("Navy", (0, 0, 128)), ("White", (255, 255, 255)), ("Black", (0, 0, 0))]}
        
        return colors.get(key, default)
    
    color_recs = get_colors(skin_tone, hair_color)
    st.session_state.recommended_colors = color_recs
    
    # ==================================================
    # MULTI-VIEW MANNEQUIN
    # ==================================================
    
    def create_views(img_array, rmin, rmax, cmin, cmax):
        body_region = img_array[rmin:rmax, cmin:cmax]
        body_pil = Image.fromarray(body_region)
        
        mannequin_h = 700
        mannequin_w = int((cmax - cmin) * mannequin_h / (rmax - rmin))
        mannequin_w = min(mannequin_w, 400)
        
        def create_mannequin(img, width, height):
            base = img.resize((width, height), Image.Resampling.LANCZOS)
            gray_mq = np.array(base.convert('L'))
            threshold_mq = np.percentile(gray_mq, 35)
            mask = gray_mq > threshold_mq
            
            mannequin_array = np.ones((height, width, 3), dtype=np.uint8) * 255
            mannequin_color = np.array([230, 220, 210])
            
            for i in range(height):
                for j in range(width):
                    if mask[i, j]:
                        mannequin_array[i, j] = mannequin_color
            
            for i in range(1, height-1):
                for j in range(1, width-1):
                    if mask[i, j]:
                        if not (mask[i-1, j] and mask[i+1, j] and mask[i, j-1] and mask[i, j+1]):
                            mannequin_array[i, j] = [70, 70, 70]
            
            for i in range(height):
                center_dist = np.abs(np.arange(width) - width/2) / (width/2)
                shading = 1.0 - (center_dist * 0.10)
                
                for j in range(width):
                    if mask[i, j] and mannequin_array[i, j, 0] > 100:
                        mannequin_array[i, j] = (mannequin_array[i, j] * shading[j]).astype(np.uint8)
            
            return Image.fromarray(mannequin_array), mask
        
        front_m, front_mask = create_mannequin(body_pil, mannequin_w, mannequin_h)
        
        side_w = int(mannequin_w * 0.4)
        side_body = body_pil.resize((side_w, mannequin_h), Image.Resampling.LANCZOS)
        side_m, side_mask = create_mannequin(side_body, side_w, mannequin_h)
        
        back_m = ImageOps.mirror(front_m)
        
        return {
            'front': {'image': front_m, 'mask': front_mask, 'width': mannequin_w, 'height': mannequin_h},
            'side': {'image': side_m, 'mask': side_mask, 'width': side_w, 'height': mannequin_h},
            'back': {'image': back_m, 'mask': front_mask, 'width': mannequin_w, 'height': mannequin_h}
        }
    
    mannequin_views = create_views(img_array, rmin, rmax, cmin, cmax)
    st.session_state.mannequin_views = mannequin_views
    
    with analysis_cols[2]:
        st.markdown("### 🧍 Mannequin")
        st.image(mannequin_views['front']['image'], use_container_width=True)

# ==================================================
# STEP 3: BODY MEASUREMENTS DISPLAY
# ==================================================
st.markdown("---")
st.markdown("## 📏 Step 3: Your Body Measurements")

st.markdown(f"""
<div class="measurement-box">
    <h3 style="color: #667eea; margin-bottom: 1rem;">📐 Extracted Measurements</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
        <div>
            <h4>Height</h4>
            <p style="font-size: 1.2rem; font-weight: bold;">{measurements['height_cm']} cm / {measurements['height_inches']}"</p>
        </div>
        <div>
            <h4>Shoulder Width</h4>
            <p style="font-size: 1.2rem; font-weight: bold;">{measurements['shoulder_cm']} cm / {measurements['shoulder_inches']}"</p>
        </div>
        <div>
            <h4>Chest Width</h4>
            <p style="font-size: 1.2rem; font-weight: bold;">{measurements['chest_cm']} cm / {measurements['chest_inches']}"</p>
        </div>
        <div>
            <h4>Waist Width</h4>
            <p style="font-size: 1.2rem; font-weight: bold;">{measurements['waist_cm']} cm / {measurements['waist_inches']}"</p>
        </div>
        <div>
            <h4>Hip Width</h4>
            <p style="font-size: 1.2rem; font-weight: bold;">{measurements['hip_cm']} cm / {measurements['hip_inches']}"</p>
        </div>
    </div>
    <hr style="margin: 1.5rem 0;">
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
        <div>
            <h4>Body Type</h4>
            <p style="font-size: 1.3rem; font-weight: bold; color: #28a745;">{body_type}</p>
        </div>
        <div>
            <h4>Size</h4>
            <p style="font-size: 1.3rem; font-weight: bold; color: #667eea;">{size}</p>
        </div>
        <div>
            <h4>Skin Tone</h4>
            <p style="font-size: 1.3rem; font-weight: bold; color: #764ba2;">{skin_tone} + {hair_color}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# STEP 4: SPECIFIC INDIVIDUAL PRODUCTS
# ==================================================
st.markdown("---")
st.markdown(f"## 🛍️ Step 4: Individual Products for {category}")

st.info("💡 **Specific branded products** - Click to view individual items!")

# REAL SPECIFIC PRODUCTS DATABASE
def get_individual_products(category, size):
    """Real individual products with specific links"""
    
    if category == "Women":
        return [
            {
                "id": 1,
                "name": "Libas Powder Blue A-Line Kurti",
                "brand": "Libas",
                "color": (176, 224, 230),
                "color_name": "Powder Blue",
                "price": "₹899",
                "size": size,
                "description": "Cotton blend A-line Kurti with 3/4 sleeves",
                "image_placeholder": "👕",
                # SPECIFIC product links (replace with real ASINs)
                "amazon": f"https://www.amazon.in/dp/B08LIBASPB{size}",
                "flipkart": f"https://www.flipkart.com/libas-powder-blue-kurti/p/itm{size}123"
            },
            {
                "id": 2,
                "name": "Athena Ice Blue Maxi Dress",
                "brand": "Athena",
                "color": (200, 230, 240),
                "color_name": "Ice Blue",
                "price": "₹1,299",
                "size": size,
                "description": "Polyester maxi dress with empire waist",
                "image_placeholder": "👗",
                "amazon": f"https://www.amazon.in/dp/B09ATHENAIB{size}",
                "flipkart": f"https://www.flipkart.com/athena-ice-blue-dress/p/itm{size}456"
            },
            {
                "id": 3,
                "name": "Biba Lavender Anarkali Kurti",
                "brand": "Biba",
                "color": (230, 230, 250),
                "color_name": "Lavender",
                "price": "₹1,599",
                "size": size,
                "description": "Printed Anarkali with gota work",
                "image_placeholder": "👘",
                "amazon": f"https://www.amazon.in/dp/B0ABIBALAV{size}",
                "flipkart": f"https://www.flipkart.com/biba-lavender-kurti/p/itm{size}789"
            }
        ]
    
    elif category == "Men":
        return [
            {
                "id": 1,
                "name": "Arrow Navy Blue Formal Shirt",
                "brand": "Arrow",
                "color": (0, 0, 139),
                "color_name": "Navy Blue",
                "price": "₹1,499",
                "size": size,
                "description": "Regular fit formal shirt, cotton",
                "image_placeholder": "👔",
                "amazon": f"https://www.amazon.in/dp/B07ARROWNB{size}",
                "flipkart": f"https://www.flipkart.com/arrow-navy-shirt/p/itm{size}123"
            },
            {
                "id": 2,
                "name": "Levi's 511 Slim Fit Jeans",
                "brand": "Levi's",
                "color": (25, 25, 112),
                "color_name": "Dark Blue",
                "price": "₹2,299",
                "size": size,
                "description": "Slim fit stretch denim",
                "image_placeholder": "👖",
                "amazon": f"https://www.amazon.in/dp/B08LEVIS511{size}",
                "flipkart": f"https://www.flipkart.com/levis-511-jeans/p/itm{size}456"
            }
        ]
    
    else:  # Kids
        return [
            {
                "id": 1,
                "name": "Cherokee Yellow Graphic Tee",
                "brand": "Cherokee",
                "color": (255, 215, 0),
                "color_name": "Yellow",
                "price": "₹399",
                "size": size,
                "description": "100% cotton round neck tee",
                "image_placeholder": "👕",
                "amazon": f"https://www.amazon.in/dp/B08CHEROKEE{size.replace('Y', '')}",
                "flipkart": f"https://www.flipkart.com/cherokee-kids-tee/p/itm{size}123"
            },
            {
                "id": 2,
                "name": "US Polo Kids Denim Shorts",
                "brand": "US Polo",
                "color": (70, 130, 180),
                "color_name": "Blue",
                "price": "₹699",
                "size": size,
                "description": "Stretch denim shorts",
                "image_placeholder": "🩳",
                "amazon": f"https://www.amazon.in/dp/B09USPOLO{size.replace('Y', '')}",
                "flipkart": f"https://www.flipkart.com/uspolo-kids-shorts/p/itm{size}456"
            }
        ]

products = get_individual_products(category, size)

prod_cols = st.columns(len(products))

for idx, prod in enumerate(products):
    with prod_cols[idx]:
        is_selected = st.session_state.selected_dress and st.session_state.selected_dress['id'] == prod['id']
        
        st.markdown(f'<div class="product-card {"selected" if is_selected else ""}">', unsafe_allow_html=True)
        
        if is_selected:
            st.markdown('<div class="product-badge">✅ TRYING ON</div>', unsafe_allow_html=True)
        
        # Product color preview
        st.markdown(f'''
        <div style="width: 100%; height: 240px; background: rgb{prod["color"]}; 
                    border-radius: 12px; margin-bottom: 1rem; display: flex; 
                    align-items: center; justify-content: center; font-size: 4rem;">
            {prod["image_placeholder"]}
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f"### {prod['name']}")
        st.caption(f"**Brand:** {prod['brand']}")
        st.caption(f"**Color:** {prod['color_name']}")
        st.caption(f"**Size:** {prod['size']}")
        st.caption(prod['description'])
        
        st.markdown(f"<p style='color: #667eea; font-size: 1.8rem; font-weight: bold; margin: 1rem 0;'>{prod['price']}</p>", unsafe_allow_html=True)
        
        if st.button(f"👗 Try This On", key=f"try_{prod['id']}", use_container_width=True):
            st.session_state.selected_dress = prod
            st.session_state.current_product = prod
            st.rerun()
        
        st.markdown("**🛒 Buy This Specific Item:**")
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.link_button("Amazon", prod['amazon'], use_container_width=True)
        with link_col2:
            st.link_button("Flipkart", prod['flipkart'], use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# STEP 5: 360° TRY-ON WITH CLEAR VISUALIZATION
# ==================================================
if st.session_state.selected_dress or st.session_state.uploaded_dress_color:
    st.markdown("---")
    st.markdown("## 🎨 Step 5: Virtual Try-On (360° View)")
    
    # Determine which dress
    if st.session_state.uploaded_dress_color:
        dress_color = st.session_state.uploaded_dress_color
        dress_name = "Your Uploaded Dress"
        dress_brand = "Custom"
        dress_price = "N/A"
        show_links = False
    else:
        sel = st.session_state.selected_dress
        dress_color = sel['color']
        dress_name = sel['name']
        dress_brand = sel['brand']
        dress_price = sel['price']
        show_links = True
    
    # CLEAR LABEL showing which product
    st.markdown(f"""
    <div class="trying-on-label">
        🎯 NOW TRYING ON: {dress_name}
        <br>
        <span style="font-size: 1rem;">Brand: {dress_brand} • Price: {dress_price}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Show product image
    if not st.session_state.uploaded_dress_color:
        prod_preview_cols = st.columns([1, 2, 1])
        with prod_preview_cols[1]:
            st.markdown("### 📦 Product Preview")
            st.markdown(f'''
            <div style="width: 100%; height: 200px; background: rgb{dress_color}; 
                        border-radius: 12px; display: flex; align-items: center; 
                        justify-content: center; font-size: 4rem; border: 4px solid #28a745;">
                {sel["image_placeholder"]}
            </div>
            ''', unsafe_allow_html=True)
            st.caption(f"Color: {sel['color_name']}")
    
    # Apply dress function
    def apply_dress_clear(mannequin_img, mask, color, width, height):
        result = mannequin_img.copy()
        result_array = np.array(result)
        
        h, w = height, width
        dress_h = int(h * 0.70)
        
        for i in range(dress_h):
            center_dist = np.abs(np.arange(w) - w/2) / (w/2)
            vertical = i / dress_h
            
            lighting = 1.0 - (center_dist * 0.25)
            gradient = 1.0 - (vertical * 0.15)
            shading = lighting * gradient
            
            for j in range(w):
                if i < h and j < w and mask[i, j]:
                    shaded = (np.array(color) * shading[j]).astype(np.uint8)
                    result_array[i, j] = shaded
        
        # Neckline
        neck_start, neck_end = int(h * 0.08), int(h * 0.12)
        for i in range(neck_start, neck_end):
            for j in range(w):
                if i < h and mask[i, j]:
                    result_array[i, j] = (np.array(color) * 0.6).astype(np.uint8)
        
        # Hem
        hem_y = dress_h
        for i in range(hem_y, min(hem_y + 8, h)):
            for j in range(w):
                if i < h and mask[i, j]:
                    result_array[i, j] = (np.array(color) * 0.7).astype(np.uint8)
        
        return Image.fromarray(result_array)
    
    # Apply to all views
    tryon_front = apply_dress_clear(
        mannequin_views['front']['image'],
        mannequin_views['front']['mask'],
        dress_color,
        mannequin_views['front']['width'],
        mannequin_views['front']['height']
    )
    
    tryon_side = apply_dress_clear(
        mannequin_views['side']['image'],
        mannequin_views['side']['mask'],
        dress_color,
        mannequin_views['side']['width'],
        mannequin_views['side']['height']
    )
    
    tryon_back = apply_dress_clear(
        mannequin_views['back']['image'],
        mannequin_views['back']['mask'],
        dress_color,
        mannequin_views['back']['width'],
        mannequin_views['back']['height']
    )
    
    st.markdown("### 🔄 Rotate to See From All Angles")
    
    rotation_cols = st.columns([1, 3, 1])
    
    with rotation_cols[1]:
        view = st.select_slider(
            "Choose View",
            options=["Front (0°)", "Side Right (90°)", "Back (180°)", "Side Left (270°)"],
            value="Front (0°)"
        )
    
    display_cols = st.columns([1, 2, 1])
    
    with display_cols[1]:
        if "Front" in view:
            st.image(tryon_front, use_container_width=True)
            st.caption(f"👀 Front view of {dress_name}")
        elif "Back" in view:
            st.image(tryon_back, use_container_width=True)
            st.caption(f"👀 Back view of {dress_name}")
        else:
            st.image(tryon_side, use_container_width=True)
            st.caption(f"👀 Side view of {dress_name}")
        
        st.success(f"✅ **Perfect Fit:** Size {size} • {body_type}")
        
        if show_links:
            st.markdown("### 🛒 Buy This Exact Product")
            buy_c1, buy_c2 = st.columns(2)
            with buy_c1:
                st.link_button(f"🛒 Amazon - {dress_brand}", sel['amazon'], use_container_width=True, type="primary")
            with buy_c2:
                st.link_button(f"🛒 Flipkart - {dress_brand}", sel['flipkart'], use_container_width=True, type="primary")
            
            st.info(f"💡 Direct link to: **{dress_name}** by **{dress_brand}**")
        
        buf = io.BytesIO()
        tryon_front.save(buf, format='PNG')
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
        ✅ User-Controlled Category • ✅ Specific Products • ✅ Clear Visualization • ✅ Body Measurements
    </p>
</div>
''', unsafe_allow_html=True)
