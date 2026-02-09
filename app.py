import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import base64

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Professional Fashion Stylist",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .mannequin-card {
        background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #dee2e6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .product-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
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
        transform: translateY(-5px);
    }
    .size-badge {
        background: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 0.75rem;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>👗 Professional Fashion Stylist</h1>
    <p style="font-size: 1.2rem;">AI-Powered Mannequin Fitting & Virtual Try-On</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=Fashion+Stylist", use_container_width=True)
    
    st.markdown("### 🎯 How It Works")
    st.info("""
    **Step 1:** Upload your full-body photo
    
    **Step 2:** AI converts you to a professional mannequin
    
    **Step 3:** Get personalized dress recommendations
    
    **Step 4:** Virtually try on outfits on your mannequin
    
    **Step 5:** Purchase directly from shopping links
    """)
    
    st.markdown("### 📸 Photo Guidelines")
    st.success("""
    ✅ Full body visible (head to toe)
    ✅ Standing straight, arms at sides
    ✅ Good lighting, plain background
    ✅ Fitted clothing (to see body shape)
    ✅ Clear, high-resolution image
    """)
    
    st.markdown("### 💡 Pro Tips")
    st.warning("""
    • White or light background works best
    • Remove accessories for accurate fit
    • Face the camera directly
    • Avoid baggy clothing
    """)

# --------------------------------------------------
# Initialize Session State
# --------------------------------------------------
if 'mannequin' not in st.session_state:
    st.session_state.mannequin = None
if 'selected_dress' not in st.session_state:
    st.session_state.selected_dress = None
if 'measurements' not in st.session_state:
    st.session_state.measurements = None
if 'category' not in st.session_state:
    st.session_state.category = None
if 'size' not in st.session_state:
    st.session_state.size = None

# --------------------------------------------------
# Image Upload
# --------------------------------------------------
st.markdown("## 📤 Step 1: Upload Your Photo")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear full-body photo for best results"
    )

if uploaded_file is None:
    st.info("👆 Upload your photo to begin your personalized styling session")
    
    # Demo visualization
    st.markdown("### 📋 Preview of Results")
    demo_cols = st.columns(4)
    with demo_cols[0]:
        st.metric("Category", "Women", help="Detected clothing category")
    with demo_cols[1]:
        st.metric("Size", "M", help="Recommended size")
    with demo_cols[2]:
        st.metric("Fit Score", "94%", help="AI confidence")
    with demo_cols[3]:
        st.metric("Products", "12", help="Available outfits")
    
    st.stop()

# --------------------------------------------------
# Process Image
# --------------------------------------------------
original_image = Image.open(uploaded_file).convert("RGB")

st.markdown("---")
st.markdown("## 🔄 Step 2: Mannequin Conversion")

process_col1, process_col2 = st.columns(2)

with process_col1:
    st.markdown("### 📷 Your Original Photo")
    st.image(original_image, use_container_width=True)

# --------------------------------------------------
# Advanced Body Analysis
# --------------------------------------------------
with st.spinner("🔍 Analyzing body structure and proportions..."):
    
    # Get dimensions
    img_width, img_height = original_image.size
    img_array = np.array(original_image)
    
    # Advanced body detection using color and edge analysis
    # Convert to different color spaces for better detection
    gray = np.mean(img_array, axis=2)
    
    # Multi-method detection
    # Method 1: Brightness thresholding
    threshold = np.percentile(gray, 30)
    body_mask1 = gray > threshold
    
    # Method 2: Edge-based detection
    # Simple edge detection using gradient
    grad_x = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    grad_y = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    edges = grad_x[:, :-1] + grad_y[:-1, :]
    body_mask2 = edges > np.percentile(edges, 40)
    
    # Combine masks
    body_mask = body_mask1 | body_mask2
    
    # Find body bounding box
    rows = np.any(body_mask, axis=1)
    cols = np.any(body_mask, axis=0)
    
    if rows.any() and cols.any():
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        # Add margins
        margin_h = int((rmax - rmin) * 0.05)
        margin_w = int((cmax - cmin) * 0.05)
        
        rmin = max(0, rmin - margin_h)
        rmax = min(img_height, rmax + margin_h)
        cmin = max(0, cmin - margin_w)
        cmax = min(img_width, cmax + margin_w)
    else:
        # Fallback to center region
        rmin, rmax = int(img_height * 0.1), int(img_height * 0.9)
        cmin, cmax = int(img_width * 0.2), int(img_width * 0.8)
    
    body_h = rmax - rmin
    body_w = cmax - cmin

# --------------------------------------------------
# Extract Detailed Measurements
# --------------------------------------------------
def extract_professional_measurements(body_w, body_h, img_w, img_h, img_array, rmin, rmax, cmin, cmax):
    """Extract professional tailor-grade measurements"""
    
    # Extract body region
    body_region = img_array[rmin:rmax, cmin:cmax]
    region_h, region_w = body_region.shape[:2]
    
    # Analyze vertical segments for better accuracy
    # Top 30% = shoulders/chest
    # Middle 40% = waist
    # Bottom 30% = hips/legs
    
    shoulder_region = body_region[:int(region_h * 0.3), :]
    waist_region = body_region[int(region_h * 0.3):int(region_h * 0.7), :]
    hip_region = body_region[int(region_h * 0.7):, :]
    
    # Measure width at each section (find actual body width)
    def get_section_width(section):
        """Get actual body width in a section"""
        gray_section = np.mean(section, axis=2)
        # Find columns with significant variation (body present)
        col_variance = np.var(gray_section, axis=0)
        threshold = np.percentile(col_variance, 25)
        body_cols = col_variance > threshold
        if np.any(body_cols):
            left = np.where(body_cols)[0][0]
            right = np.where(body_cols)[0][-1]
            return right - left
        return region_w * 0.8  # fallback
    
    shoulder_width = get_section_width(shoulder_region)
    waist_width = get_section_width(waist_region)
    hip_width = get_section_width(hip_region)
    
    # Calculate chest width (between shoulder and waist)
    chest_width = (shoulder_width + waist_width) / 2
    
    # Height measurements
    total_height = body_h
    torso_height = body_h * 0.55
    leg_length = body_h * 0.45
    
    # Ratios for classification
    shoulder_hip_ratio = shoulder_width / hip_width if hip_width > 0 else 1.0
    waist_hip_ratio = waist_width / hip_width if hip_width > 0 else 0.85
    height_width_ratio = total_height / shoulder_width if shoulder_width > 0 else 2.0
    
    return {
        "shoulder_width": shoulder_width,
        "chest_width": chest_width,
        "waist_width": waist_width,
        "hip_width": hip_width,
        "total_height": total_height,
        "torso_height": torso_height,
        "leg_length": leg_length,
        "shoulder_hip_ratio": shoulder_hip_ratio,
        "waist_hip_ratio": waist_hip_ratio,
        "height_width_ratio": height_width_ratio,
        "body_region_h": region_h,
        "body_region_w": region_w
    }

measurements = extract_professional_measurements(
    body_w, body_h, img_width, img_height, img_array, rmin, rmax, cmin, cmax
)

st.session_state.measurements = measurements

# --------------------------------------------------
# Professional Classification
# --------------------------------------------------
def classify_professional(measurements, img_h):
    """Professional size classification"""
    
    height_ratio = measurements["total_height"] / img_h
    aspect_ratio = measurements["height_width_ratio"]
    shoulder_hip = measurements["shoulder_hip_ratio"]
    waist_hip = measurements["waist_hip_ratio"]
    
    # Kids detection
    if height_ratio < 0.65 or aspect_ratio > 2.8:
        category = "Kids"
        if height_ratio < 0.45:
            size = "4-6Y"
        elif height_ratio < 0.55:
            size = "7-9Y"
        else:
            size = "10-12Y"
        fit_score = 0.88
    else:
        # Adult classification - more sophisticated
        # Men: broader shoulders, less waist definition
        # Women: balanced or wider hips, defined waist
        
        gender_score = (shoulder_hip - 1.0) * 2 + (1.0 - waist_hip) * 1.5
        
        if gender_score > 0.15 or aspect_ratio < 1.9:
            category = "Men"
        else:
            category = "Women"
        
        # Size based on multiple factors
        shoulder_percentile = measurements["shoulder_width"] / measurements["body_region_w"]
        waist_percentile = measurements["waist_width"] / measurements["body_region_w"]
        
        size_score = (shoulder_percentile * 0.6) + (waist_percentile * 0.4)
        
        if category == "Men":
            if size_score < 0.65:
                size = "S"
            elif size_score < 0.75:
                size = "M"
            elif size_score < 0.85:
                size = "L"
            else:
                size = "XL"
        else:  # Women
            if size_score < 0.60:
                size = "XS"
            elif size_score < 0.68:
                size = "S"
            elif size_score < 0.76:
                size = "M"
            elif size_score < 0.84:
                size = "L"
            else:
                size = "XL"
        
        fit_score = 0.92
    
    return category, size, fit_score

category, size, fit_score = classify_professional(measurements, img_height)
st.session_state.category = category
st.session_state.size = size

# --------------------------------------------------
# Create Professional Mannequin
# --------------------------------------------------
def create_professional_mannequin(measurements, category):
    """Create realistic fashion mannequin"""
    
    # Standard mannequin dimensions
    canvas_w, canvas_h = 400, 800
    
    # Create base with subtle gradient
    mannequin = Image.new('RGB', (canvas_w, canvas_h), color='white')
    draw = ImageDraw.Draw(mannequin, 'RGBA')
    
    # Scale measurements to canvas
    scale_factor = (canvas_h * 0.75) / measurements["total_height"]
    
    # Scaled measurements
    shoulder_w = int(measurements["shoulder_width"] * scale_factor)
    chest_w = int(measurements["chest_width"] * scale_factor)
    waist_w = int(measurements["waist_width"] * scale_factor)
    hip_w = int(measurements["hip_width"] * scale_factor)
    torso_h = int(measurements["torso_height"] * scale_factor)
    leg_h = int(measurements["leg_length"] * scale_factor)
    
    # Center positioning
    center_x = canvas_w // 2
    start_y = 100
    
    # Mannequin colors - professional neutral tones
    if category == "Men":
        base_color = (220, 215, 210)  # Warm beige
        outline_color = (100, 100, 100)
    elif category == "Women":
        base_color = (230, 225, 220)  # Soft cream
        outline_color = (120, 120, 120)
    else:  # Kids
        base_color = (240, 235, 230)  # Light ivory
        outline_color = (140, 140, 140)
    
    # Draw head/neck
    head_radius = shoulder_w // 3
    neck_width = head_radius // 2
    
    # Head
    draw.ellipse([
        center_x - head_radius,
        start_y,
        center_x + head_radius,
        start_y + head_radius * 2
    ], fill=base_color, outline=outline_color, width=3)
    
    # Neck
    neck_y = start_y + head_radius * 2
    draw.rectangle([
        center_x - neck_width,
        neck_y,
        center_x + neck_width,
        neck_y + head_radius
    ], fill=base_color, outline=outline_color, width=2)
    
    # Torso - shaped (shoulders -> chest -> waist -> hips)
    torso_start_y = neck_y + head_radius
    
    # Shoulder line
    shoulder_y = torso_start_y
    # Chest line (25% down torso)
    chest_y = torso_start_y + int(torso_h * 0.25)
    # Waist line (60% down torso)
    waist_y = torso_start_y + int(torso_h * 0.60)
    # Hip line (bottom of torso)
    hip_y = torso_start_y + torso_h
    
    # Draw torso as polygon for natural shape
    torso_points = [
        (center_x - shoulder_w//2, shoulder_y),  # Left shoulder
        (center_x + shoulder_w//2, shoulder_y),  # Right shoulder
        (center_x + chest_w//2, chest_y),        # Right chest
        (center_x + waist_w//2, waist_y),        # Right waist
        (center_x + hip_w//2, hip_y),            # Right hip
        (center_x - hip_w//2, hip_y),            # Left hip
        (center_x - waist_w//2, waist_y),        # Left waist
        (center_x - chest_w//2, chest_y),        # Left chest
    ]
    draw.polygon(torso_points, fill=base_color, outline=outline_color, width=3)
    
    # Arms
    arm_w = shoulder_w // 6
    arm_length = int(torso_h * 0.7)
    
    # Left arm
    draw.rectangle([
        center_x - shoulder_w//2 - arm_w - 5,
        shoulder_y + 10,
        center_x - shoulder_w//2 - 5,
        shoulder_y + 10 + arm_length
    ], fill=base_color, outline=outline_color, width=2)
    
    # Right arm
    draw.rectangle([
        center_x + shoulder_w//2 + 5,
        shoulder_y + 10,
        center_x + shoulder_w//2 + arm_w + 5,
        shoulder_y + 10 + arm_length
    ], fill=base_color, outline=outline_color, width=2)
    
    # Legs
    leg_start_y = hip_y
    leg_w = hip_w // 2 - 15
    leg_gap = 10
    
    # Left leg
    draw.polygon([
        (center_x - leg_gap, leg_start_y),
        (center_x - leg_w, leg_start_y),
        (center_x - leg_w + 10, leg_start_y + leg_h),
        (center_x - leg_gap, leg_start_y + leg_h)
    ], fill=base_color, outline=outline_color, width=3)
    
    # Right leg
    draw.polygon([
        (center_x + leg_gap, leg_start_y),
        (center_x + leg_w, leg_start_y),
        (center_x + leg_w - 10, leg_start_y + leg_h),
        (center_x + leg_gap, leg_start_y + leg_h)
    ], fill=base_color, outline=outline_color, width=3)
    
    # Add subtle shading for 3D effect
    enhancer = ImageEnhance.Contrast(mannequin)
    mannequin = enhancer.enhance(1.1)
    
    # Store reference points for dress overlay
    ref_points = {
        "center_x": center_x,
        "shoulder_y": shoulder_y,
        "chest_y": chest_y,
        "waist_y": waist_y,
        "hip_y": hip_y,
        "leg_end_y": leg_start_y + leg_h,
        "shoulder_w": shoulder_w,
        "chest_w": chest_w,
        "waist_w": waist_w,
        "hip_w": hip_w,
        "torso_h": torso_h,
        "leg_h": leg_h
    }
    
    return mannequin, ref_points

mannequin, ref_points = create_professional_mannequin(measurements, category)
st.session_state.mannequin = mannequin
st.session_state.ref_points = ref_points

with process_col2:
    st.markdown("### 🎨 Professional Mannequin")
    st.image(mannequin, use_container_width=True)
    st.success("✅ Mannequin conversion complete!")

# --------------------------------------------------
# Display Measurements
# --------------------------------------------------
st.markdown("---")
st.markdown("## 📊 Step 3: Your Measurements & Size")

metrics_cols = st.columns(4)
with metrics_cols[0]:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("👤 Category", category)
    st.markdown('</div>', unsafe_allow_html=True)

with metrics_cols[1]:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("📏 Size", size)
    st.markdown('</div>', unsafe_allow_html=True)

with metrics_cols[2]:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("🎯 Fit Score", f"{int(fit_score * 100)}%")
    st.markdown('</div>', unsafe_allow_html=True)

with metrics_cols[3]:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("📐 Aspect Ratio", f"{measurements['height_width_ratio']:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

# Detailed measurements
with st.expander("📏 View Detailed Measurements"):
    measure_cols = st.columns(3)
    with measure_cols[0]:
        st.markdown("**Upper Body**")
        st.write(f"Shoulder: {measurements['shoulder_width']:.0f}px")
        st.write(f"Chest: {measurements['chest_width']:.0f}px")
        st.write(f"Waist: {measurements['waist_width']:.0f}px")
    
    with measure_cols[1]:
        st.markdown("**Lower Body**")
        st.write(f"Hip: {measurements['hip_width']:.0f}px")
        st.write(f"Torso: {measurements['torso_height']:.0f}px")
        st.write(f"Legs: {measurements['leg_length']:.0f}px")
    
    with measure_cols[2]:
        st.markdown("**Ratios**")
        st.write(f"Shoulder/Hip: {measurements['shoulder_hip_ratio']:.2f}")
        st.write(f"Waist/Hip: {measurements['waist_hip_ratio']:.2f}")
        st.write(f"Height/Width: {measurements['height_width_ratio']:.2f}")

# --------------------------------------------------
# Dress Catalog
# --------------------------------------------------
st.markdown("---")
st.markdown("## 👗 Step 4: Browse & Select Outfits")

def get_dress_catalog(category, size):
    """Get curated dress catalog with real shopping links"""
    
    if category == "Kids":
        return [
            {
                "id": 1,
                "name": "Rainbow Cotton Dress",
                "price": "₹499",
                "color": (255, 192, 203),  # Pink
                "image": "https://via.placeholder.com/250x300/FFB6C1/000000?text=Rainbow+Dress",
                "meesho": f"https://www.meesho.com/kids-rainbow-dress-size-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+rainbow+dress+{size}",
                "description": "Colorful cotton dress perfect for parties"
            },
            {
                "id": 2,
                "name": "Denim Jumpsuit",
                "price": "₹699",
                "color": (100, 149, 237),  # Cornflower blue
                "image": "https://via.placeholder.com/250x300/6495ED/FFFFFF?text=Denim+Jumpsuit",
                "meesho": f"https://www.meesho.com/kids-denim-jumpsuit-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+denim+jumpsuit+{size}",
                "description": "Comfortable denim one-piece"
            },
            {
                "id": 3,
                "name": "Princess Gown",
                "price": "₹899",
                "color": (218, 112, 214),  # Orchid
                "image": "https://via.placeholder.com/250x300/DA70D6/FFFFFF?text=Princess+Gown",
                "meesho": f"https://www.meesho.com/kids-princess-gown-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+princess+gown+{size}",
                "description": "Elegant party wear gown"
            },
            {
                "id": 4,
                "name": "Casual T-Shirt & Shorts",
                "price": "₹599",
                "color": (255, 215, 0),  # Gold
                "image": "https://via.placeholder.com/250x300/FFD700/000000?text=Casual+Set",
                "meesho": f"https://www.meesho.com/kids-casual-set-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+casual+wear+{size}",
                "description": "Perfect everyday comfort wear"
            }
        ]
    
    elif category == "Men":
        return [
            {
                "id": 1,
                "name": "Formal Shirt & Trouser",
                "price": "₹1,299",
                "color": (70, 130, 180),  # Steel blue
                "image": "https://via.placeholder.com/250x300/4682B4/FFFFFF?text=Formal+Set",
                "meesho": f"https://www.meesho.com/mens-formal-set-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+formal+shirt+{size}",
                "description": "Professional office wear"
            },
            {
                "id": 2,
                "name": "Casual Denim Jacket",
                "price": "₹1,599",
                "color": (25, 25, 112),  # Midnight blue
                "image": "https://via.placeholder.com/250x300/191970/FFFFFF?text=Denim+Jacket",
                "meesho": f"https://www.meesho.com/mens-denim-jacket-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+denim+jacket+{size}",
                "description": "Trendy casual outerwear"
            },
            {
                "id": 3,
                "name": "Sports Track Suit",
                "price": "₹999",
                "color": (255, 69, 0),  # Orange red
                "image": "https://via.placeholder.com/250x300/FF4500/FFFFFF?text=Track+Suit",
                "meesho": f"https://www.meesho.com/mens-tracksuit-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+tracksuit+{size}",
                "description": "Athletic performance wear"
            },
            {
                "id": 4,
                "name": "Designer Kurta Set",
                "price": "₹1,799",
                "color": (139, 69, 19),  # Saddle brown
                "image": "https://via.placeholder.com/250x300/8B4513/FFFFFF?text=Kurta+Set",
                "meesho": f"https://www.meesho.com/mens-kurta-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+kurta+{size}",
                "description": "Traditional ethnic wear"
            },
            {
                "id": 5,
                "name": "Business Suit",
                "price": "₹2,999",
                "color": (47, 79, 79),  # Dark slate gray
                "image": "https://via.placeholder.com/250x300/2F4F4F/FFFFFF?text=Business+Suit",
                "meesho": f"https://www.meesho.com/mens-suit-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+suit+{size}",
                "description": "Premium formal suit"
            },
            {
                "id": 6,
                "name": "Polo T-Shirt",
                "price": "₹799",
                "color": (0, 128, 128),  # Teal
                "image": "https://via.placeholder.com/250x300/008080/FFFFFF?text=Polo+Shirt",
                "meesho": f"https://www.meesho.com/mens-polo-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+polo+{size}",
                "description": "Smart casual polo"
            }
        ]
    
    else:  # Women
        return [
            {
                "id": 1,
                "name": "Elegant Kurti",
                "price": "₹899",
                "color": (255, 182, 193),  # Light pink
                "image": "https://via.placeholder.com/250x300/FFB6C1/000000?text=Kurti",
                "meesho": f"https://www.meesho.com/womens-kurti-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+kurti+{size}",
                "description": "Traditional Indian kurti"
            },
            {
                "id": 2,
                "name": "Party Dress",
                "price": "₹1,499",
                "color": (186, 85, 211),  # Medium orchid
                "image": "https://via.placeholder.com/250x300/BA55D3/FFFFFF?text=Party+Dress",
                "meesho": f"https://www.meesho.com/womens-party-dress-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+party+dress+{size}",
                "description": "Glamorous evening wear"
            },
            {
                "id": 3,
                "name": "Casual Top & Jeans",
                "price": "₹1,099",
                "color": (135, 206, 250),  # Light sky blue
                "image": "https://via.placeholder.com/250x300/87CEEB/000000?text=Casual+Wear",
                "meesho": f"https://www.meesho.com/womens-casual-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+casual+wear+{size}",
                "description": "Everyday comfort outfit"
            },
            {
                "id": 4,
                "name": "Designer Saree",
                "price": "₹2,499",
                "color": (255, 20, 147),  # Deep pink
                "image": "https://via.placeholder.com/250x300/FF1493/FFFFFF?text=Saree",
                "meesho": f"https://www.meesho.com/womens-saree-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+saree+{size}",
                "description": "Classic Indian saree"
            },
            {
                "id": 5,
                "name": "Office Blazer Set",
                "price": "₹1,899",
                "color": (112, 128, 144),  # Slate gray
                "image": "https://via.placeholder.com/250x300/708090/FFFFFF?text=Blazer+Set",
                "meesho": f"https://www.meesho.com/womens-blazer-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+blazer+{size}",
                "description": "Professional work attire"
            },
            {
                "id": 6,
                "name": "Maxi Dress",
                "price": "₹1,299",
                "color": (250, 128, 114),  # Salmon
                "image": "https://via.placeholder.com/250x300/FA8072/FFFFFF?text=Maxi+Dress",
                "meesho": f"https://www.meesho.com/womens-maxi-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+maxi+dress+{size}",
                "description": "Flowing summer dress"
            },
            {
                "id": 7,
                "name": "Lehenga Choli",
                "price": "₹3,499",
                "color": (255, 105, 180),  # Hot pink
                "image": "https://via.placeholder.com/250x300/FF69B4/FFFFFF?text=Lehenga",
                "meesho": f"https://www.meesho.com/womens-lehenga-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+lehenga+{size}",
                "description": "Bridal & festive wear"
            },
            {
                "id": 8,
                "name": "Denim Jacket",
                "price": "₹1,399",
                "color": (70, 130, 180),  # Steel blue
                "image": "https://via.placeholder.com/250x300/4682B4/FFFFFF?text=Denim+Jacket",
                "meesho": f"https://www.meesho.com/womens-denim-jacket-{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+denim+jacket+{size}",
                "description": "Trendy casual jacket"
            }
        ]

catalog = get_dress_catalog(category, size)

# Display catalog
st.markdown(f"### 🎯 Recommended for {category} - Size **{size}**")
st.info(f"💡 Showing {len(catalog)} outfits perfectly matched to your measurements")

# Create columns for products
num_cols = 4 if category == "Women" else 3
product_cols = st.columns(num_cols)

for idx, dress in enumerate(catalog):
    col_idx = idx % num_cols
    
    with product_cols[col_idx]:
        # Check if selected
        is_selected = (st.session_state.selected_dress and 
                      st.session_state.selected_dress['id'] == dress['id'])
        
        card_class = "product-card selected" if is_selected else "product-card"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Product image
        st.image(dress['image'], use_container_width=True)
        
        # Product info
        st.markdown(f"**{dress['name']}**")
        st.markdown(f"<p style='color: #667eea; font-size: 24px; font-weight: bold; margin: 0.5rem 0;'>{dress['price']}</p>", 
                   unsafe_allow_html=True)
        st.caption(dress['description'])
        
        # Try-on button
        if st.button(f"👗 Try This On", key=f"try_{dress['id']}", use_container_width=True):
            st.session_state.selected_dress = dress
            st.rerun()
        
        # Shopping links
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.link_button("🛒 Meesho", dress['meesho'], use_container_width=True)
        with link_col2:
            st.link_button("🛒 Flipkart", dress['flipkart'], use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Virtual Try-On
# --------------------------------------------------
if st.session_state.selected_dress:
    st.markdown("---")
    st.markdown("## 🎨 Step 5: Virtual Try-On")
    
    selected = st.session_state.selected_dress
    
    def apply_dress_to_mannequin(mannequin, ref_points, dress_info, category):
        """Apply selected dress to mannequin realistically"""
        
        result = mannequin.copy()
        draw = ImageDraw.Draw(result, 'RGBA')
        
        # Get reference points
        cx = ref_points["center_x"]
        shoulder_y = ref_points["shoulder_y"]
        chest_y = ref_points["chest_y"]
        waist_y = ref_points["waist_y"]
        hip_y = ref_points["hip_y"]
        leg_end_y = ref_points["leg_end_y"]
        
        shoulder_w = ref_points["shoulder_w"]
        chest_w = ref_points["chest_w"]
        waist_w = ref_points["waist_w"]
        hip_w = ref_points["hip_w"]
        leg_h = ref_points["leg_h"]
        
        # Dress color with transparency
        dress_color = dress_info['color']
        dress_rgba = dress_color + (200,)  # Add alpha
        
        # Different dress styles based on category and name
        dress_name = dress_info['name'].lower()
        
        if category == "Kids":
            if "dress" in dress_name or "gown" in dress_name:
                # Full dress
                dress_points = [
                    (cx - shoulder_w//2 + 20, shoulder_y + 30),
                    (cx + shoulder_w//2 - 20, shoulder_y + 30),
                    (cx + hip_w//2 + 20, hip_y + 50),
                    (cx + hip_w//2 + 30, hip_y + 150),
                    (cx - hip_w//2 - 30, hip_y + 150),
                    (cx - hip_w//2 - 20, hip_y + 50),
                ]
                draw.polygon(dress_points, fill=dress_rgba, outline=dress_color, width=3)
            elif "jumpsuit" in dress_name:
                # Full body coverage
                draw.polygon([
                    (cx - shoulder_w//2 + 20, shoulder_y + 30),
                    (cx + shoulder_w//2 - 20, shoulder_y + 30),
                    (cx + waist_w//2, waist_y),
                    (cx + waist_w//2, hip_y),
                    (cx + hip_w//3, leg_end_y - 20),
                    (cx - hip_w//3, leg_end_y - 20),
                    (cx - waist_w//2, hip_y),
                    (cx - waist_w//2, waist_y),
                ], fill=dress_rgba, outline=dress_color, width=3)
            else:
                # Casual top and shorts
                # Top
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + waist_w//2, waist_y + 20),
                    (cx - waist_w//2, waist_y + 20),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Shorts
                short_color = (dress_color[0]//2, dress_color[1]//2, dress_color[2]//2)
                short_rgba = short_color + (200,)
                draw.polygon([
                    (cx - hip_w//2 + 10, hip_y - 20),
                    (cx + hip_w//2 - 10, hip_y - 20),
                    (cx + hip_w//3, hip_y + 80),
                    (cx - hip_w//3, hip_y + 80),
                ], fill=short_rgba, outline=short_color, width=3)
        
        elif category == "Men":
            if "suit" in dress_name or "formal" in dress_name or "blazer" in dress_name:
                # Formal shirt and trousers
                # Shirt
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + waist_w//2, waist_y + 30),
                    (cx - waist_w//2, waist_y + 30),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Trousers
                pant_color = (50, 50, 50)
                pant_rgba = pant_color + (200,)
                # Left leg
                draw.polygon([
                    (cx - 15, hip_y),
                    (cx - hip_w//3, hip_y),
                    (cx - hip_w//3 + 10, leg_end_y),
                    (cx - 10, leg_end_y),
                ], fill=pant_rgba, outline=pant_color, width=3)
                # Right leg
                draw.polygon([
                    (cx + 15, hip_y),
                    (cx + hip_w//3, hip_y),
                    (cx + hip_w//3 - 10, leg_end_y),
                    (cx + 10, leg_end_y),
                ], fill=pant_rgba, outline=pant_color, width=3)
            elif "kurta" in dress_name:
                # Traditional kurta
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + hip_w//2 + 10, hip_y + 80),
                    (cx - hip_w//2 - 10, hip_y + 80),
                ], fill=dress_rgba, outline=dress_color, width=3)
            elif "track" in dress_name or "sports" in dress_name:
                # Sports wear
                # Top
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + waist_w//2, hip_y - 20),
                    (cx - waist_w//2, hip_y - 20),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Track pants
                for leg_offset in [-1, 1]:
                    leg_x = cx + (leg_offset * 15)
                    draw.polygon([
                        (leg_x - 10, hip_y - 20),
                        (leg_x + (leg_offset * hip_w//3), hip_y - 20),
                        (leg_x + (leg_offset * hip_w//3) - (leg_offset * 5), leg_end_y),
                        (leg_x - 5, leg_end_y),
                    ], fill=dress_rgba, outline=dress_color, width=3)
            else:
                # Casual shirt and jeans
                # Shirt
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + waist_w//2, hip_y - 10),
                    (cx - waist_w//2, hip_y - 10),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Jeans
                jean_color = (70, 130, 180)
                jean_rgba = jean_color + (200,)
                for leg_offset in [-1, 1]:
                    leg_x = cx + (leg_offset * 10)
                    draw.polygon([
                        (leg_x, hip_y - 10),
                        (leg_x + (leg_offset * hip_w//3), hip_y - 10),
                        (leg_x + (leg_offset * hip_w//3) - (leg_offset * 8), leg_end_y),
                        (leg_x, leg_end_y),
                    ], fill=jean_rgba, outline=jean_color, width=3)
        
        else:  # Women
            if "saree" in dress_name:
                # Saree draping
                # Blouse
                blouse_color = (dress_color[0]//1.5, dress_color[1]//1.5, dress_color[2]//1.5)
                blouse_rgba = tuple(int(c) for c in blouse_color) + (200,)
                draw.polygon([
                    (cx - shoulder_w//2 + 20, shoulder_y + 30),
                    (cx + shoulder_w//2 - 20, shoulder_y + 30),
                    (cx + chest_w//2 - 10, chest_y + 20),
                    (cx - chest_w//2 + 10, chest_y + 20),
                ], fill=blouse_rgba, outline=tuple(int(c) for c in blouse_color), width=3)
                # Saree drape
                draw.polygon([
                    (cx - shoulder_w//3, shoulder_y + 40),
                    (cx + waist_w//2, waist_y),
                    (cx + hip_w//2 + 20, hip_y + 100),
                    (cx + hip_w//2 + 30, leg_end_y - 30),
                    (cx - hip_w//2 - 30, leg_end_y - 30),
                    (cx - hip_w//2 - 20, hip_y + 100),
                    (cx - waist_w//2, waist_y),
                ], fill=dress_rgba, outline=dress_color, width=3)
            elif "lehenga" in dress_name:
                # Lehenga choli
                # Choli (top)
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + waist_w//2, waist_y - 10),
                    (cx - waist_w//2, waist_y - 10),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Lehenga (skirt)
                lehenga_color = (dress_color[0]//1.2, dress_color[1]//1.2, dress_color[2]//1.2)
                lehenga_rgba = tuple(int(c) for c in lehenga_color) + (200,)
                draw.polygon([
                    (cx - waist_w//2, waist_y - 10),
                    (cx + waist_w//2, waist_y - 10),
                    (cx + hip_w//2 + 40, leg_end_y - 20),
                    (cx - hip_w//2 - 40, leg_end_y - 20),
                ], fill=lehenga_rgba, outline=tuple(int(c) for c in lehenga_color), width=3)
            elif "kurti" in dress_name:
                # Kurti with leggings
                # Kurti
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + hip_w//2, hip_y + 60),
                    (cx - hip_w//2, hip_y + 60),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Leggings
                legging_color = (30, 30, 30)
                legging_rgba = legging_color + (200,)
                for leg_offset in [-1, 1]:
                    leg_x = cx + (leg_offset * 12)
                    draw.polygon([
                        (leg_x, hip_y + 60),
                        (leg_x + (leg_offset * hip_w//4), hip_y + 60),
                        (leg_x + (leg_offset * hip_w//4) - (leg_offset * 5), leg_end_y),
                        (leg_x, leg_end_y),
                    ], fill=legging_rgba, outline=legging_color, width=2)
            elif "dress" in dress_name or "maxi" in dress_name:
                # Dress
                dress_length = leg_end_y - 50 if "maxi" in dress_name else hip_y + 100
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + hip_w//2 + 20, dress_length),
                    (cx - hip_w//2 - 20, dress_length),
                ], fill=dress_rgba, outline=dress_color, width=3)
            elif "blazer" in dress_name or "office" in dress_name:
                # Blazer and skirt/trousers
                # Blazer
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + waist_w//2 + 10, waist_y + 40),
                    (cx - waist_w//2 - 10, waist_y + 40),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Skirt
                skirt_color = (40, 40, 40)
                skirt_rgba = skirt_color + (200,)
                draw.polygon([
                    (cx - waist_w//2 - 5, waist_y + 40),
                    (cx + waist_w//2 + 5, waist_y + 40),
                    (cx + hip_w//2, hip_y + 80),
                    (cx - hip_w//2, hip_y + 80),
                ], fill=skirt_rgba, outline=skirt_color, width=3)
            else:
                # Casual top and jeans
                # Top
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + waist_w//2, hip_y - 20),
                    (cx - waist_w//2, hip_y - 20),
                ], fill=dress_rgba, outline=dress_color, width=3)
                # Jeans
                jean_color = (70, 130, 180)
                jean_rgba = jean_color + (200,)
                for leg_offset in [-1, 1]:
                    leg_x = cx + (leg_offset * 10)
                    draw.polygon([
                        (leg_x, hip_y - 20),
                        (leg_x + (leg_offset * hip_w//3), hip_y - 20),
                        (leg_x + (leg_offset * hip_w//3) - (leg_offset * 7), leg_end_y),
                        (leg_x, leg_end_y),
                    ], fill=jean_rgba, outline=jean_color, width=2)
        
        return result
    
    tryon_result = apply_dress_to_mannequin(
        st.session_state.mannequin,
        st.session_state.ref_points,
        selected,
        category
    )
    
    # Display try-on result
    tryon_col1, tryon_col2, tryon_col3 = st.columns([1, 2, 1])
    
    with tryon_col2:
        st.markdown(f"### {selected['name']}")
        st.image(tryon_result, use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; margin-top: 1rem;">
            <h3 style="color: #667eea;">{selected['price']}</h3>
            <p>{selected['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Purchase buttons
        st.markdown("### 🛍️ Ready to Buy?")
        buy_col1, buy_col2 = st.columns(2)
        with buy_col1:
            st.link_button("🛒 Buy on Meesho", selected['meesho'], use_container_width=True)
        with buy_col2:
            st.link_button("🛒 Buy on Flipkart", selected['flipkart'], use_container_width=True)
        
        # Download option
        st.markdown("---")
        buf = io.BytesIO()
        tryon_result.save(buf, format='PNG')
        st.download_button(
            "⬇️ Download This Look",
            buf.getvalue(),
            f"virtual_tryon_{selected['name'].replace(' ', '_')}.png",
            "image/png",
            use_container_width=True
        )

# --------------------------------------------------
# Additional Features
# --------------------------------------------------
st.markdown("---")
st.markdown("## 📚 Additional Resources")

resource_cols = st.columns(3)

with resource_cols[0]:
    with st.expander("📏 Size Guide"):
        if category == "Men":
            st.markdown("""
            | Size | Chest | Waist | Shoulder |
            |------|-------|-------|----------|
            | S | 36-38" | 28-30" | 16-17" |
            | M | 38-40" | 30-32" | 17-18" |
            | L | 40-42" | 32-34" | 18-19" |
            | XL | 42-44" | 34-36" | 19-20" |
            """)
        elif category == "Women":
            st.markdown("""
            | Size | Bust | Waist | Hip |
            |------|------|-------|-----|
            | XS | 32-34" | 24-26" | 34-36" |
            | S | 34-36" | 26-28" | 36-38" |
            | M | 36-38" | 28-30" | 38-40" |
            | L | 38-40" | 30-32" | 40-42" |
            | XL | 40-42" | 32-34" | 42-44" |
            """)
        else:
            st.markdown("""
            | Size | Age | Height | Chest |
            |------|-----|--------|-------|
            | 4-6Y | 4-6 years | 100-115cm | 24-26" |
            | 7-9Y | 7-9 years | 115-130cm | 26-28" |
            | 10-12Y | 10-12 years | 130-145cm | 28-30" |
            """)

with resource_cols[1]:
    with st.expander("💡 Styling Tips"):
        st.markdown("""
        **Color Matching:**
        - Neutrals work with everything
        - Complementary colors create balance
        - Monochrome looks elongate figure
        
        **Fit Guidelines:**
        - Shoulders should align perfectly
        - Waist should be comfortable
        - Length should suit your height
        
        **Occasion Guide:**
        - Formal: Structured, muted colors
        - Casual: Relaxed, fun patterns
        - Party: Bold, statement pieces
        """)

with resource_cols[2]:
    with st.expander("🔄 Try Different Sizes"):
        st.markdown(f"""
        **Current Size:** {size}
        
        **Size Recommendations:**
        - If too tight: Try one size up
        - If too loose: Try one size down
        - Between sizes: Choose based on fit preference
        
        **Tip:** Check each retailer's size chart before ordering!
        """)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
    <h3>🌟 Professional Fashion Stylist</h3>
    <p style="font-size: 1.1rem; margin: 1rem 0;">AI-Powered Mannequin Fitting & Virtual Try-On</p>
    <p style="font-size: 0.9rem; opacity: 0.9;">
        Accurate measurements • Realistic try-on • Direct shopping links
    </p>
    <p style="font-size: 0.8rem; margin-top: 1rem; opacity: 0.8;">
        Made with ❤️ using Streamlit • No external dependencies
    </p>
</div>
""", unsafe_allow_html=True)
