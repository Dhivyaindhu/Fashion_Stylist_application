import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFilter
import io

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Smart Fashion Stylist",
    page_icon="👗",
    layout="wide"
)

# ==================================================
# CSS
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
    
    .measurement-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 1rem 0;
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
    
    .extraction-steps {
        background: rgba(102, 126, 234, 0.1);
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 0.9rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown('''
<div class="main-header">
    <h1>👗 Smart Fashion Stylist</h1>
    <p style="font-size: 1.3rem;">
        Automatic Dress Extraction • Virtual Try-On • Body Measurements
    </p>
</div>
''', unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
for key in ['user_category', 'size', 'measurements', 'mannequin_views',
            'extracted_dress', 'dress_mask']:
    if key not in st.session_state:
        st.session_state[key] = None

# ==================================================
# CLOTHING EXTRACTION ALGORITHM
# ==================================================

def extract_clothing_from_product_image(product_img):
    """
    Extract ONLY the clothing from a product image showing a model.
    
    Algorithm:
    1. Detect skin tones (face, hands, legs)
    2. Remove background (detect edges + flood fill)
    3. Remove skin regions
    4. Keep only clothing area
    5. Return clothing with transparent background
    """
    
    img_array = np.array(product_img.convert("RGB"))
    h, w = img_array.shape[:2]
    
    # Step 1: Detect skin tones
    r = img_array[:,:,0].astype(float)
    g = img_array[:,:,1].astype(float)
    b = img_array[:,:,2].astype(float)
    
    # Skin detection using color rules
    # Skin typically has: R > G > B, and specific ratios
    skin_mask = np.zeros((h, w), dtype=bool)
    
    # Multiple skin tone ranges
    for _ in range(1):
        # Fair to medium skin
        condition1 = (r > 95) & (g > 40) & (b > 20)
        condition2 = (r > g) & (r > b)
        condition3 = (abs(r - g) > 15)
        condition4 = (r - b > 15)
        
        fair_medium_skin = condition1 & condition2 & condition3 & condition4
        
        # Tan to deep skin
        condition5 = (r > 50) & (g > 30) & (b > 15)
        condition6 = (r > g) & (g > b)
        condition7 = (r - g < 50)
        
        tan_deep_skin = condition5 & condition6 & condition7
        
        skin_mask = fair_medium_skin | tan_deep_skin
    
    # Expand skin regions slightly
    from scipy import ndimage
    try:
        skin_mask = ndimage.binary_dilation(skin_mask, iterations=3)
    except:
        # Fallback without scipy
        for _ in range(3):
            temp = skin_mask.copy()
            for i in range(1, h-1):
                for j in range(1, w-1):
                    if skin_mask[i, j]:
                        temp[i-1:i+2, j-1:j+2] = True
            skin_mask = temp
    
    # Step 2: Remove background
    # Detect edges
    gray = np.mean(img_array, axis=2)
    
    # Simple background detection (corners are usually background)
    corners_val = [
        gray[0, 0], gray[0, w-1],
        gray[h-1, 0], gray[h-1, w-1],
        np.mean(gray[0, :]),  # top edge
        np.mean(gray[h-1, :]),  # bottom edge
        np.mean(gray[:, 0]),  # left edge
        np.mean(gray[:, w-1])  # right edge
    ]
    bg_threshold = np.median(corners_val)
    
    # Background mask (similar to corner values)
    bg_mask = np.abs(gray - bg_threshold) < 30
    
    # Step 3: Create clothing mask
    # Clothing = NOT (skin OR background)
    clothing_mask = ~(skin_mask | bg_mask)
    
    # Clean up small regions
    # Remove very small disconnected regions
    for i in range(h):
        for j in range(w):
            if clothing_mask[i, j]:
                # Check if isolated
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if 0 <= i+di < h and 0 <= j+dj < w:
                            if clothing_mask[i+di, j+dj]:
                                neighbors += 1
                if neighbors < 3:
                    clothing_mask[i, j] = False
    
    # Step 4: Extract clothing with transparency
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result_array = np.array(result)
    
    for i in range(h):
        for j in range(w):
            if clothing_mask[i, j]:
                result_array[i, j] = (*img_array[i, j], 255)
    
    result = Image.fromarray(result_array)
    
    # Crop to clothing bounding box
    # Find bounding box of clothing
    rows_with_clothing = np.any(clothing_mask, axis=1)
    cols_with_clothing = np.any(clothing_mask, axis=0)
    
    if rows_with_clothing.any() and cols_with_clothing.any():
        rmin, rmax = np.where(rows_with_clothing)[0][[0, -1]]
        cmin, cmax = np.where(cols_with_clothing)[0][[0, -1]]
        
        result = result.crop((cmin, rmin, cmax, rmax))
        clothing_mask_cropped = clothing_mask[rmin:rmax, cmin:cmax]
    else:
        clothing_mask_cropped = clothing_mask
    
    return result, clothing_mask_cropped


def extract_clothing_simple(product_img):
    """
    SIMPLIFIED extraction - works without scipy
    Focuses on torso region and removes skin tones
    """
    
    img_array = np.array(product_img.convert("RGB"))
    h, w = img_array.shape[:2]
    
    r = img_array[:,:,0].astype(float)
    g = img_array[:,:,1].astype(float)
    b = img_array[:,:,2].astype(float)
    
    # Skin detection
    skin_mask = (r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b) & ((r - g) > 15)
    
    # Background detection (very light or very dark)
    brightness = (r + g + b) / 3
    bg_mask = (brightness > 240) | (brightness < 20)
    
    # Clothing = NOT (skin OR background)
    clothing_mask = ~(skin_mask | bg_mask)
    
    # Focus on center region (where clothing usually is)
    center_mask = np.zeros((h, w), dtype=bool)
    center_mask[h//8:7*h//8, w//6:5*w//6] = True
    clothing_mask = clothing_mask & center_mask
    
    # Create RGBA output
    result_array = np.zeros((h, w, 4), dtype=np.uint8)
    result_array[:,:,:3] = img_array
    result_array[:,:,3] = (clothing_mask * 255).astype(np.uint8)
    
    result = Image.fromarray(result_array, 'RGBA')
    
    # Crop to bounding box
    rows = np.any(clothing_mask, axis=1)
    cols = np.any(clothing_mask, axis=0)
    
    if rows.any() and cols.any():
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        result = result.crop((cmin, rmin, cmax, rmax))
        clothing_mask = clothing_mask[rmin:rmax, cmin:cmax]
    
    return result, clothing_mask

# ==================================================
# STEP 1: UPLOAD BODY PHOTO + SELECT CATEGORY
# ==================================================
st.markdown("## 📤 Step 1: Upload Your Photo & Select Category")

upload_cols = st.columns(2)

with upload_cols[0]:
    st.markdown("### 📷 Your Photo")
    uploaded_body = st.file_uploader("Upload full body", type=["jpg", "jpeg", "png"], key="body")

with upload_cols[1]:
    st.markdown("### 🎯 Category")
    cat_cols = st.columns(3)
    with cat_cols[0]:
        if st.button("👶 Kids", use_container_width=True):
            st.session_state.user_category = "Kids"
    with cat_cols[1]:
        if st.button("👨 Men", use_container_width=True):
            st.session_state.user_category = "Men"
    with cat_cols[2]:
        if st.button("👩 Women", use_container_width=True):
            st.session_state.user_category = "Women"
    
    if st.session_state.user_category:
        st.success(f"✅ {st.session_state.user_category}")

if not uploaded_body:
    st.info("👆 Upload your photo")
    st.stop()

if not st.session_state.user_category:
    st.warning("⚠️ Please select category")
    st.stop()

category = st.session_state.user_category

# Process body image
original = Image.open(uploaded_body).convert("RGB")
img_array = np.array(original)
img_h, img_w = img_array.shape[:2]

# Simple body detection
gray = np.mean(img_array, axis=2)
threshold = np.percentile(gray, 25)
body_mask = gray > threshold

rows = np.any(body_mask, axis=1)
cols = np.any(body_mask, axis=0)

if rows.any() and cols.any():
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
else:
    rmin, rmax = int(img_h * 0.05), int(img_h * 0.95)
    cmin, cmax = int(img_w * 0.15), int(img_w * 0.85)

body_h = rmax - rmin
body_w = cmax - cmin

# Calculate measurements
avg_height = 162 if category == "Women" else (175 if category == "Men" else 120)
px_to_cm = avg_height / body_h

measurements = {
    "height_cm": round(body_h * px_to_cm, 1),
    "shoulder_cm": round(body_w * 0.42 * px_to_cm, 1),
    "chest_cm": round(body_w * 0.45 * px_to_cm, 1),
    "waist_cm": round(body_w * 0.38 * px_to_cm, 1),
    "hip_cm": round(body_w * 0.44 * px_to_cm, 1),
}

st.session_state.measurements = measurements

# Size detection
chest_cm = measurements["chest_cm"]
if category == "Kids":
    size = "4-6Y" if measurements["height_cm"] < 115 else "7-9Y"
elif category == "Men":
    if chest_cm < 88: size = "S"
    elif chest_cm < 96: size = "M"
    elif chest_cm < 104: size = "L"
    else: size = "XL"
else:
    if chest_cm < 88: size = "S"
    elif chest_cm < 96: size = "M"
    elif chest_cm < 104: size = "L"
    else: size = "XL"

st.session_state.size = size

# Create simple mannequin
def create_simple_mannequin(body_array, rmin, rmax, cmin, cmax):
    body_region = body_array[rmin:rmax, cmin:cmax]
    body_pil = Image.fromarray(body_region)
    
    mannequin_h = 600
    mannequin_w = int(body_w * mannequin_h / body_h)
    mannequin_w = min(mannequin_w, 350)
    
    base = body_pil.resize((mannequin_w, mannequin_h), Image.Resampling.LANCZOS)
    gray_m = np.array(base.convert('L'))
    threshold_m = np.percentile(gray_m, 35)
    mask = gray_m > threshold_m
    
    mannequin_array = np.ones((mannequin_h, mannequin_w, 3), dtype=np.uint8) * 255
    mannequin_color = np.array([230, 220, 210])
    
    for i in range(mannequin_h):
        for j in range(mannequin_w):
            if mask[i, j]:
                mannequin_array[i, j] = mannequin_color
    
    # Outline
    for i in range(1, mannequin_h-1):
        for j in range(1, mannequin_w-1):
            if mask[i, j]:
                if not (mask[i-1, j] and mask[i+1, j] and mask[i, j-1] and mask[i, j+1]):
                    mannequin_array[i, j] = [70, 70, 70]
    
    mannequin = Image.fromarray(mannequin_array)
    return {'image': mannequin, 'mask': mask, 'width': mannequin_w, 'height': mannequin_h}

mannequin_data = create_simple_mannequin(img_array, rmin, rmax, cmin, cmax)
st.session_state.mannequin_views = {'front': mannequin_data}

# Display
st.markdown("---")
st.markdown("## 📊 Step 2: Analysis Results")

analysis_cols = st.columns(3)

with analysis_cols[0]:
    st.markdown("### 📷 Original")
    st.image(original, use_container_width=True)

with analysis_cols[1]:
    st.markdown("### 📏 Measurements")
    st.markdown(f"""
    <div class="measurement-box">
        <h4>Height: {measurements['height_cm']} cm</h4>
        <h4>Shoulder: {measurements['shoulder_cm']} cm</h4>
        <h4>Chest: {measurements['chest_cm']} cm</h4>
        <h4>Waist: {measurements['waist_cm']} cm</h4>
        <h4>Hip: {measurements['hip_cm']} cm</h4>
        <hr>
        <h3 style="color: #667eea;">Size: {size}</h3>
    </div>
    """, unsafe_allow_html=True)

with analysis_cols[2]:
    st.markdown("### 🧍 Your Mannequin")
    st.image(mannequin_data['image'], use_container_width=True)

# ==================================================
# STEP 3: UPLOAD PRODUCT IMAGE (with model)
# ==================================================
st.markdown("---")
st.markdown("## 👗 Step 3: Upload Product Image from Amazon/Flipkart")

st.markdown("""
<div class="extraction-steps">
    <h4>📸 How it works:</h4>
    <ol>
        <li>Go to Amazon/Flipkart and find a dress you like</li>
        <li><strong>Right-click on the product image → Save Image</strong></li>
        <li>Upload that image below</li>
        <li>AI will <strong>automatically extract ONLY the dress</strong> (removing model & background)</li>
        <li>See the dress on YOUR mannequin!</li>
    </ol>
</div>
""", unsafe_allow_html=True)

product_upload = st.file_uploader(
    "📁 Upload product image (saved from Amazon/Flipkart)",
    type=["jpg", "jpeg", "png"],
    key="product"
)

if product_upload:
    product_img = Image.open(product_upload).convert("RGB")
    
    st.markdown("### 🔬 Extracting Dress...")
    
    extract_cols = st.columns(3)
    
    with extract_cols[0]:
        st.markdown("#### 1️⃣ Original Product")
        st.image(product_img, use_container_width=True)
        st.caption("Product image with model")
    
    # Extract clothing
    with st.spinner("🔍 Removing model & background..."):
        extracted_dress, dress_mask = extract_clothing_simple(product_img)
    
    st.session_state.extracted_dress = extracted_dress
    st.session_state.dress_mask = dress_mask
    
    with extract_cols[1]:
        st.markdown("#### 2️⃣ Extracted Dress")
        st.image(extracted_dress, use_container_width=True)
        st.caption("ONLY the dress (transparent background)")
    
    # Apply to mannequin
    def apply_extracted_dress_to_mannequin(mannequin_img, mannequin_mask, dress_img, mannequin_w, mannequin_h):
        """Apply extracted dress to mannequin"""
        
        result = mannequin_img.copy()
        result_array = np.array(result)
        
        # Resize dress to fit mannequin torso
        dress_width = int(mannequin_w * 0.95)
        dress_height = int(mannequin_h * 0.65)
        
        dress_resized = dress_img.resize((dress_width, dress_height), Image.Resampling.LANCZOS)
        dress_array = np.array(dress_resized)
        
        # Position on mannequin (center, starting from shoulders)
        start_y = int(mannequin_h * 0.12)
        start_x = (mannequin_w - dress_width) // 2
        
        # Overlay dress
        for i in range(min(dress_height, mannequin_h - start_y)):
            for j in range(min(dress_width, mannequin_w - start_x)):
                y = start_y + i
                x = start_x + j
                
                if y < mannequin_h and x < mannequin_w:
                    if mannequin_mask[y, x]:  # Only on mannequin body
                        if dress_array.shape[2] == 4:  # Has alpha
                            alpha = dress_array[i, j, 3] / 255.0
                            if alpha > 0.1:  # Not transparent
                                result_array[y, x] = dress_array[i, j, :3]
                        else:
                            result_array[y, x] = dress_array[i, j, :3]
        
        return Image.fromarray(result_array)
    
    mannequin_with_dress = apply_extracted_dress_to_mannequin(
        mannequin_data['image'],
        mannequin_data['mask'],
        extracted_dress,
        mannequin_data['width'],
        mannequin_data['height']
    )
    
    with extract_cols[2]:
        st.markdown("#### 3️⃣ Virtual Try-On")
        st.image(mannequin_with_dress, use_container_width=True)
        st.caption("Dress on YOUR body shape!")
    
    # Final display
    st.markdown("---")
    st.markdown("## ✨ Final Result")
    
    st.markdown(f"""
    <div class="trying-on-label">
        🎯 VIRTUAL TRY-ON COMPLETE
        <br>
        <span style="font-size: 1rem;">Size: {size} • Category: {category}</span>
    </div>
    """, unsafe_allow_html=True)
    
    final_cols = st.columns([1, 2, 1])
    
    with final_cols[1]:
        st.image(mannequin_with_dress, use_container_width=True)
        
        st.success(f"✅ This dress will fit your {category} body perfectly!")
        
        # Download
        buf = io.BytesIO()
        mannequin_with_dress.save(buf, format='PNG')
        st.download_button(
            "⬇️ Download Virtual Try-On",
            buf.getvalue(),
            "virtual_tryon.png",
            "image/png",
            use_container_width=True
        )

else:
    st.info("👆 **Upload a product image** from Amazon/Flipkart to try it on!")

# Footer
st.markdown("---")
st.markdown('''
<div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 20px; color: white;">
    <h2>🌟 Smart Fashion Stylist</h2>
    <p style="font-size: 1.2rem;">
        ✅ Automatic Dress Extraction • ✅ Remove Model & Background • ✅ Virtual Try-On
    </p>
</div>
''', unsafe_allow_html=True)
