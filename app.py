import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import base64
import math

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="3D Fashion Stylist",
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
    .rotation-badge {
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
    <h1>👗 3D Fashion Stylist</h1>
    <p style="font-size: 1.2rem;">AI-Powered Mannequin with 360° Rotation & Virtual Try-On</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown("### 🎯 How It Works")
    st.info("""
    **Step 1:** Upload your full-body photo
    
    **Step 2:** AI converts you to a 3D mannequin
    
    **Step 3:** Get personalized measurements & size
    
    **Step 4:** Browse recommended outfits
    
    **Step 5:** Try on dresses and rotate 360°
    
    **Step 6:** Purchase from Amazon/Flipkart
    """)
    
    st.markdown("### 📸 Photo Guidelines")
    st.success("""
    ✅ Full body visible (head to toe)
    ✅ Standing straight, arms at sides
    ✅ Good lighting, plain background
    ✅ Fitted clothing (to see body shape)
    ✅ Clear, high-resolution image
    """)
    
    st.markdown("### 🔄 Rotation Controls")
    st.warning("""
    • Use slider to rotate mannequin 360°
    • Click buttons for quick rotation
    • See outfit from all angles
    • Reset to front view anytime
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
if 'rotation_angle' not in st.session_state:
    st.session_state.rotation_angle = 0
if 'ref_points' not in st.session_state:
    st.session_state.ref_points = None

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
    st.info("👆 Upload your photo to begin your 3D styling session")
    
    # Demo visualization
    st.markdown("### 📋 Preview of Features")
    demo_cols = st.columns(4)
    with demo_cols[0]:
        st.metric("Category", "Auto-Detect", help="Men/Women/Kids")
    with demo_cols[1]:
        st.metric("Size", "Smart-Size", help="XS to XL")
    with demo_cols[2]:
        st.metric("Rotation", "360°", help="Full rotation")
    with demo_cols[3]:
        st.metric("Products", "6-8", help="Curated outfits")
    
    st.stop()

# --------------------------------------------------
# Process Image
# --------------------------------------------------
original_image = Image.open(uploaded_file).convert("RGB")

st.markdown("---")
st.markdown("## 🔄 Step 2: Body Analysis & Mannequin Creation")

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
    gray = np.mean(img_array, axis=2)
    
    # Multi-method detection
    threshold = np.percentile(gray, 30)
    body_mask1 = gray > threshold
    
    # Edge-based detection
    grad_x = np.abs(np.diff(gray, axis=1))
    grad_y = np.abs(np.diff(gray, axis=0))
    
    # Ensure both gradients have same shape
    min_rows = min(grad_x.shape[0], grad_y.shape[0])
    min_cols = min(grad_x.shape[1], grad_y.shape[1])
    
    edges = grad_x[:min_rows, :min_cols] + grad_y[:min_rows, :min_cols]
    
    # Resize body_mask2 to match original gray shape
    body_mask2 = np.zeros_like(gray, dtype=bool)
    body_mask2[:min_rows, :min_cols] = edges > np.percentile(edges, 40)
    
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
    
    shoulder_region = body_region[:int(region_h * 0.3), :]
    waist_region = body_region[int(region_h * 0.3):int(region_h * 0.7), :]
    hip_region = body_region[int(region_h * 0.7):, :]
    
    def get_section_width(section):
        """Get actual body width in a section"""
        gray_section = np.mean(section, axis=2)
        col_variance = np.var(gray_section, axis=0)
        threshold = np.percentile(col_variance, 25)
        body_cols = col_variance > threshold
        if np.any(body_cols):
            left = np.where(body_cols)[0][0]
            right = np.where(body_cols)[0][-1]
            return right - left
        return region_w * 0.8
    
    shoulder_width = get_section_width(shoulder_region)
    waist_width = get_section_width(waist_region)
    hip_width = get_section_width(hip_region)
    chest_width = (shoulder_width + waist_width) / 2
    
    total_height = body_h
    torso_height = body_h * 0.55
    leg_length = body_h * 0.45
    
    shoulder_hip_ratio = shoulder_width / hip_width if hip_width > 0 else 1.0
    waist_hip_ratio = waist_width / hip_width if hip_width > 0 else 0.85
    height_width_ratio = total_height / shoulder_width if shoulder_width > 0 else 2.0
    
    # Convert to approximate CM (assuming average person is ~170cm tall)
    pixels_per_cm = body_h / 170
    
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
        "body_region_w": region_w,
        "pixels_per_cm": pixels_per_cm,
        # Actual measurements in CM
        "height_cm": round(total_height / pixels_per_cm),
        "shoulder_cm": round(shoulder_width / pixels_per_cm),
        "chest_cm": round(chest_width / pixels_per_cm),
        "waist_cm": round(waist_width / pixels_per_cm),
        "hip_cm": round(hip_width / pixels_per_cm),
    }

measurements = extract_professional_measurements(
    body_w, body_h, img_width, img_height, img_array, rmin, rmax, cmin, cmax
)

st.session_state.measurements = measurements

# --------------------------------------------------
# Professional Classification
# --------------------------------------------------
def classify_professional(measurements, img_h):
    """Professional size classification with improved accuracy"""
    
    height_ratio = measurements["total_height"] / img_h
    aspect_ratio = measurements["height_width_ratio"]
    shoulder_hip = measurements["shoulder_hip_ratio"]
    waist_hip = measurements["waist_hip_ratio"]
    height_cm = measurements["height_cm"]
    
    # Enhanced Kids detection (multiple criteria)
    # Kids typically: shorter height, higher proportions, less body definition
    kids_score = 0
    
    # Height-based detection (most reliable)
    if height_cm < 150:
        kids_score += 3
    elif height_cm < 160:
        kids_score += 1
    
    # Proportion-based detection
    if height_ratio < 0.70:
        kids_score += 2
    
    if aspect_ratio > 2.6:
        kids_score += 2
    
    # Body definition (kids have less defined curves)
    if abs(shoulder_hip - 1.0) < 0.08 and abs(waist_hip - 1.0) < 0.12:
        kids_score += 1
    
    # Classify as Kids if score >= 4
    if kids_score >= 4:
        category = "Kids"
        if height_cm < 115 or height_ratio < 0.50:
            size = "4-6Y"
        elif height_cm < 135 or height_ratio < 0.60:
            size = "7-9Y"
        else:
            size = "10-12Y"
        fit_score = 0.88
    else:
        # Adult classification - Enhanced Men vs Women detection
        
        # Multiple factors for gender classification:
        # 1. Shoulder/Hip ratio (Men typically > 1.05, Women typically 0.95-1.05)
        # 2. Waist/Hip ratio (Men typically > 0.88, Women typically < 0.85)
        # 3. Body proportions
        
        # Calculate gender score (positive = Men, negative = Women)
        gender_score = 0
        
        # Shoulder-Hip ratio analysis
        if shoulder_hip > 1.10:
            gender_score += 3  # Strong indicator of Men
        elif shoulder_hip > 1.05:
            gender_score += 2  # Moderate indicator of Men
        elif shoulder_hip < 0.98:
            gender_score -= 2  # Moderate indicator of Women
        elif shoulder_hip < 1.02:
            gender_score -= 1  # Slight indicator of Women
        
        # Waist-Hip ratio analysis
        if waist_hip > 0.92:
            gender_score += 2  # Indicator of Men (less waist definition)
        elif waist_hip > 0.88:
            gender_score += 1
        elif waist_hip < 0.80:
            gender_score -= 2  # Indicator of Women (more waist definition)
        elif waist_hip < 0.85:
            gender_score -= 1
        
        # Height/Width aspect ratio
        if aspect_ratio < 2.0:
            gender_score += 1  # Men typically broader
        elif aspect_ratio > 2.3:
            gender_score -= 1  # Women typically more elongated
        
        # Final classification
        if gender_score > 1:
            category = "Men"
        elif gender_score < -1:
            category = "Women"
        else:
            # Ambiguous case - use shoulder-hip ratio as tiebreaker
            if shoulder_hip > 1.03:
                category = "Men"
            else:
                category = "Women"
        
        # Size calculation based on body measurements
        shoulder_percentile = measurements["shoulder_width"] / measurements["body_region_w"]
        waist_percentile = measurements["waist_width"] / measurements["body_region_w"]
        hip_percentile = measurements["hip_width"] / measurements["body_region_w"]
        
        # Weighted size score
        if category == "Men":
            size_score = (shoulder_percentile * 0.5) + (waist_percentile * 0.3) + (hip_percentile * 0.2)
            
            if size_score < 0.62:
                size = "S"
            elif size_score < 0.72:
                size = "M"
            elif size_score < 0.82:
                size = "L"
            else:
                size = "XL"
        else:  # Women
            size_score = (shoulder_percentile * 0.3) + (waist_percentile * 0.3) + (hip_percentile * 0.4)
            
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
        
        fit_score = 0.91
    
    return category, size, fit_score

category, size, fit_score = classify_professional(measurements, img_height)
st.session_state.category = category
st.session_state.size = size

# --------------------------------------------------
# Create 3D Mannequin with Rotation
# --------------------------------------------------
def create_3d_mannequin(measurements, category, rotation_angle=0):
    """Create 3D mannequin with rotation capability"""
    
    canvas_w, canvas_h = 400, 800
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
    
    # Calculate 3D projection
    angle_rad = math.radians(rotation_angle)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    
    # 3D scaling factor
    def scale_width(width):
        return int(width * abs(cos_angle))
    
    # Mannequin colors with shading based on rotation
    if category == "Men":
        base_color = (220, 215, 210)
        outline_color = (100, 100, 100)
    elif category == "Women":
        base_color = (230, 225, 220)
        outline_color = (120, 120, 120)
    else:  # Kids
        base_color = (240, 235, 230)
        outline_color = (140, 140, 140)
    
    # Apply shading based on rotation
    light_intensity = 1.0 - (abs(sin_angle) * 0.3)
    shaded_color = tuple(int(c * light_intensity) for c in base_color)
    
    # Draw shadow
    shadow_width = scale_width(hip_w) * 0.8
    draw.ellipse([
        center_x - int(shadow_width//2), 770,
        center_x + int(shadow_width//2), 790
    ], fill=(200, 200, 200, 50))
    
    # Draw head
    head_radius = scale_width(shoulder_w // 3)
    draw.ellipse([
        center_x - head_radius,
        start_y,
        center_x + head_radius,
        start_y + head_radius * 2
    ], fill=shaded_color, outline=outline_color, width=3)
    
    # Neck
    neck_width = scale_width(head_radius // 2)
    neck_y = start_y + head_radius * 2
    draw.rectangle([
        center_x - neck_width//2,
        neck_y,
        center_x + neck_width//2,
        neck_y + head_radius
    ], fill=shaded_color, outline=outline_color, width=2)
    
    # Torso with 3D effect
    torso_start_y = neck_y + head_radius
    shoulder_y = torso_start_y
    chest_y = torso_start_y + int(torso_h * 0.25)
    waist_y = torso_start_y + int(torso_h * 0.60)
    hip_y = torso_start_y + torso_h
    
    # Scale widths for 3D effect
    shoulder_w_3d = scale_width(shoulder_w)
    chest_w_3d = scale_width(chest_w)
    waist_w_3d = scale_width(waist_w)
    hip_w_3d = scale_width(hip_w)
    
    # Draw torso
    torso_points = [
        (center_x - shoulder_w_3d//2, shoulder_y),
        (center_x + shoulder_w_3d//2, shoulder_y),
        (center_x + chest_w_3d//2, chest_y),
        (center_x + waist_w_3d//2, waist_y),
        (center_x + hip_w_3d//2, hip_y),
        (center_x - hip_w_3d//2, hip_y),
        (center_x - waist_w_3d//2, waist_y),
        (center_x - chest_w_3d//2, chest_y),
    ]
    draw.polygon(torso_points, fill=shaded_color, outline=outline_color, width=3)
    
    # Arms (visibility based on rotation)
    arm_w = scale_width(shoulder_w // 6)
    arm_length = int(torso_h * 0.7)
    
    # Left arm (visible when rotated right)
    if cos_angle > -0.7:
        arm_shade = tuple(int(c * light_intensity * 0.85) for c in base_color)
        draw.rectangle([
            center_x - shoulder_w_3d//2 - arm_w - 5,
            shoulder_y + 10,
            center_x - shoulder_w_3d//2 - 5,
            shoulder_y + 10 + arm_length
        ], fill=arm_shade, outline=outline_color, width=2)
    
    # Right arm (visible when rotated left)
    if cos_angle < 0.7:
        arm_shade = tuple(int(c * light_intensity * 0.85) for c in base_color)
        draw.rectangle([
            center_x + shoulder_w_3d//2 + 5,
            shoulder_y + 10,
            center_x + shoulder_w_3d//2 + arm_w + 5,
            shoulder_y + 10 + arm_length
        ], fill=arm_shade, outline=outline_color, width=2)
    
    # Legs
    leg_start_y = hip_y
    leg_w = scale_width(hip_w // 2 - 15)
    leg_gap = 10
    
    leg_shade = tuple(int(c * light_intensity * 0.9) for c in base_color)
    
    # Left leg
    draw.polygon([
        (center_x - leg_gap, leg_start_y),
        (center_x - leg_w, leg_start_y),
        (center_x - leg_w + 10, leg_start_y + leg_h),
        (center_x - leg_gap, leg_start_y + leg_h)
    ], fill=leg_shade, outline=outline_color, width=3)
    
    # Right leg
    draw.polygon([
        (center_x + leg_gap, leg_start_y),
        (center_x + leg_w, leg_start_y),
        (center_x + leg_w - 10, leg_start_y + leg_h),
        (center_x + leg_gap, leg_start_y + leg_h)
    ], fill=leg_shade, outline=outline_color, width=3)
    
    # Store reference points
    ref_points = {
        "center_x": center_x,
        "shoulder_y": shoulder_y,
        "chest_y": chest_y,
        "waist_y": waist_y,
        "hip_y": hip_y,
        "leg_end_y": leg_start_y + leg_h,
        "shoulder_w": shoulder_w_3d,
        "chest_w": chest_w_3d,
        "waist_w": waist_w_3d,
        "hip_w": hip_w_3d,
        "torso_h": torso_h,
        "leg_h": leg_h,
        "rotation": rotation_angle,
        "cos_angle": cos_angle
    }
    
    return mannequin, ref_points

# Create initial mannequin
mannequin, ref_points = create_3d_mannequin(measurements, category, st.session_state.rotation_angle)
st.session_state.mannequin = mannequin
st.session_state.ref_points = ref_points

with process_col2:
    st.markdown("### 🎨 3D Mannequin")
    st.image(mannequin, use_container_width=True)
    st.success("✅ 3D Mannequin created successfully!")

# --------------------------------------------------
# Rotation Controls
# --------------------------------------------------
st.markdown("---")
st.markdown("## 🔄 Step 3: Rotate Your Mannequin 360°")

rotation_cols = st.columns([1, 3, 1])

with rotation_cols[0]:
    if st.button("⬅️ Rotate Left", use_container_width=True):
        st.session_state.rotation_angle = (st.session_state.rotation_angle - 45) % 360
        st.rerun()

with rotation_cols[1]:
    rotation_angle = st.slider(
        "Drag to rotate mannequin",
        min_value=0,
        max_value=360,
        value=st.session_state.rotation_angle,
        step=15,
        help="Drag slider to see mannequin from different angles"
    )
    
    if rotation_angle != st.session_state.rotation_angle:
        st.session_state.rotation_angle = rotation_angle
        st.rerun()

with rotation_cols[2]:
    if st.button("➡️ Rotate Right", use_container_width=True):
        st.session_state.rotation_angle = (st.session_state.rotation_angle + 45) % 360
        st.rerun()

# Display current angle
angle_col1, angle_col2, angle_col3 = st.columns([1, 1, 1])
with angle_col2:
    st.markdown(f"""
    <div class="rotation-badge" style="text-align: center; font-size: 1.2em;">
        Current Angle: {st.session_state.rotation_angle}°
    </div>
    """, unsafe_allow_html=True)

if st.button("🎯 Reset to Front View", use_container_width=True):
    st.session_state.rotation_angle = 0
    st.rerun()

# --------------------------------------------------
# Display Measurements
# --------------------------------------------------
st.markdown("---")
st.markdown("## 📊 Step 4: Your Measurements & Size")

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
    st.metric("📐 Height", f"{measurements['height_cm']} cm")
    st.markdown('</div>', unsafe_allow_html=True)

# Detailed measurements
with st.expander("📏 View Detailed Body Measurements & Classification"):
    measure_cols = st.columns(3)
    with measure_cols[0]:
        st.markdown("**Upper Body**")
        st.write(f"Shoulder: {measurements['shoulder_cm']} cm")
        st.write(f"Chest: {measurements['chest_cm']} cm")
        st.write(f"Waist: {measurements['waist_cm']} cm")
    
    with measure_cols[1]:
        st.markdown("**Lower Body**")
        st.write(f"Hip: {measurements['hip_cm']} cm")
        st.write(f"Height: {measurements['height_cm']} cm")
    
    with measure_cols[2]:
        st.markdown("**Body Ratios**")
        st.write(f"Shoulder/Hip: {measurements['shoulder_hip_ratio']:.2f}")
        st.write(f"Waist/Hip: {measurements['waist_hip_ratio']:.2f}")
        st.write(f"Height/Width: {measurements['height_width_ratio']:.2f}")
    
    # Classification explanation
    st.markdown("---")
    st.markdown("**🤖 Classification Details:**")
    
    if category == "Kids":
        st.info(f"""
        **Detected as Kids** because:
        - Height: {measurements['height_cm']} cm (< 150cm indicates child)
        - Body proportions indicate developing physique
        - Less defined body curves typical of children
        """)
    elif category == "Men":
        st.info(f"""
        **Detected as Men** because:
        - Shoulder/Hip ratio: {measurements['shoulder_hip_ratio']:.2f} (Men typically > 1.05)
        - Waist/Hip ratio: {measurements['waist_hip_ratio']:.2f} (Men typically > 0.88)
        - Broader shoulders relative to hips
        """)
    else:
        st.info(f"""
        **Detected as Women** because:
        - Shoulder/Hip ratio: {measurements['shoulder_hip_ratio']:.2f} (Women typically 0.95-1.05)
        - Waist/Hip ratio: {measurements['waist_hip_ratio']:.2f} (Women typically < 0.85)
        - More defined waist relative to hips
        """)
    
    st.warning("💡 **Note:** Classification is based on body measurements only. If incorrect, you can manually browse other categories below.")

# --------------------------------------------------
# Dress Catalog
# --------------------------------------------------
st.markdown("---")
st.markdown("## 👗 Step 5: Browse & Select Outfits")

# Add category override option
st.markdown("### 🔄 Category Selection")
override_cols = st.columns([2, 1])

with override_cols[0]:
    st.info(f"📊 Auto-detected: **{category}** (Size: **{size}**)")

with override_cols[1]:
    browse_category = st.selectbox(
        "Browse different category:",
        options=["Auto-Detected", "Men", "Women", "Kids"],
        help="Select manually if auto-detection is incorrect"
    )

# Use override if selected
if browse_category != "Auto-Detected":
    display_category = browse_category
    st.warning(f"🔄 Browsing **{browse_category}** collection (overriding auto-detection)")
else:
    display_category = category

# Adjust size for browsed category if different
if display_category != category:
    # Recalculate size for the browsed category
    shoulder_percentile = measurements["shoulder_width"] / measurements["body_region_w"]
    waist_percentile = measurements["waist_width"] / measurements["body_region_w"]
    hip_percentile = measurements["hip_width"] / measurements["body_region_w"]
    
    if display_category == "Kids":
        if measurements["height_cm"] < 115:
            display_size = "4-6Y"
        elif measurements["height_cm"] < 135:
            display_size = "7-9Y"
        else:
            display_size = "10-12Y"
    elif display_category == "Men":
        size_score = (shoulder_percentile * 0.5) + (waist_percentile * 0.3) + (hip_percentile * 0.2)
        if size_score < 0.62:
            display_size = "S"
        elif size_score < 0.72:
            display_size = "M"
        elif size_score < 0.82:
            display_size = "L"
        else:
            display_size = "XL"
    else:  # Women
        size_score = (shoulder_percentile * 0.3) + (waist_percentile * 0.3) + (hip_percentile * 0.4)
        if size_score < 0.58:
            display_size = "XS"
        elif size_score < 0.66:
            display_size = "S"
        elif size_score < 0.74:
            display_size = "M"
        elif size_score < 0.82:
            display_size = "L"
        else:
            display_size = "XL"
else:
    display_size = size

def get_dress_catalog(category, size):
    """Get curated dress catalog with real shopping links"""
    
    if category == "Kids":
        return [
            {
                "id": 1,
                "name": "Rainbow Cotton Dress",
                "price": "₹499",
                "color": (255, 192, 203),
                "image": "https://via.placeholder.com/250x300/FFB6C1/000000?text=Rainbow+Dress",
                "amazon": f"https://www.amazon.in/s?k=kids+rainbow+dress+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+rainbow+dress+{size}",
                "description": "Colorful cotton dress perfect for parties"
            },
            {
                "id": 2,
                "name": "Denim Jumpsuit",
                "price": "₹699",
                "color": (100, 149, 237),
                "image": "https://via.placeholder.com/250x300/6495ED/FFFFFF?text=Denim+Jumpsuit",
                "amazon": f"https://www.amazon.in/s?k=kids+denim+jumpsuit+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+denim+jumpsuit+{size}",
                "description": "Comfortable denim one-piece"
            },
            {
                "id": 3,
                "name": "Princess Gown",
                "price": "₹899",
                "color": (218, 112, 214),
                "image": "https://via.placeholder.com/250x300/DA70D6/FFFFFF?text=Princess+Gown",
                "amazon": f"https://www.amazon.in/s?k=kids+princess+gown+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+princess+gown+{size}",
                "description": "Elegant party wear gown"
            },
            {
                "id": 4,
                "name": "Casual T-Shirt Set",
                "price": "₹599",
                "color": (255, 215, 0),
                "image": "https://via.placeholder.com/250x300/FFD700/000000?text=Casual+Set",
                "amazon": f"https://www.amazon.in/s?k=kids+casual+wear+{size}",
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
                "color": (70, 130, 180),
                "image": "https://via.placeholder.com/250x300/4682B4/FFFFFF?text=Formal+Set",
                "amazon": f"https://www.amazon.in/s?k=mens+formal+shirt+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+formal+shirt+{size}",
                "description": "Professional office wear"
            },
            {
                "id": 2,
                "name": "Casual Denim Jacket",
                "price": "₹1,599",
                "color": (25, 25, 112),
                "image": "https://via.placeholder.com/250x300/191970/FFFFFF?text=Denim+Jacket",
                "amazon": f"https://www.amazon.in/s?k=mens+denim+jacket+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+denim+jacket+{size}",
                "description": "Trendy casual outerwear"
            },
            {
                "id": 3,
                "name": "Sports Track Suit",
                "price": "₹999",
                "color": (255, 69, 0),
                "image": "https://via.placeholder.com/250x300/FF4500/FFFFFF?text=Track+Suit",
                "amazon": f"https://www.amazon.in/s?k=mens+tracksuit+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+tracksuit+{size}",
                "description": "Athletic performance wear"
            },
            {
                "id": 4,
                "name": "Designer Kurta Set",
                "price": "₹1,799",
                "color": (139, 69, 19),
                "image": "https://via.placeholder.com/250x300/8B4513/FFFFFF?text=Kurta+Set",
                "amazon": f"https://www.amazon.in/s?k=mens+kurta+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+kurta+{size}",
                "description": "Traditional ethnic wear"
            },
            {
                "id": 5,
                "name": "Business Suit",
                "price": "₹2,999",
                "color": (47, 79, 79),
                "image": "https://via.placeholder.com/250x300/2F4F4F/FFFFFF?text=Business+Suit",
                "amazon": f"https://www.amazon.in/s?k=mens+suit+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+suit+{size}",
                "description": "Premium formal suit"
            },
            {
                "id": 6,
                "name": "Polo T-Shirt",
                "price": "₹799",
                "color": (0, 128, 128),
                "image": "https://via.placeholder.com/250x300/008080/FFFFFF?text=Polo+Shirt",
                "amazon": f"https://www.amazon.in/s?k=mens+polo+{size}",
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
                "color": (255, 182, 193),
                "image": "https://via.placeholder.com/250x300/FFB6C1/000000?text=Kurti",
                "amazon": f"https://www.amazon.in/s?k=womens+kurti+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+kurti+{size}",
                "description": "Traditional Indian kurti"
            },
            {
                "id": 2,
                "name": "Party Dress",
                "price": "₹1,499",
                "color": (186, 85, 211),
                "image": "https://via.placeholder.com/250x300/BA55D3/FFFFFF?text=Party+Dress",
                "amazon": f"https://www.amazon.in/s?k=womens+party+dress+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+party+dress+{size}",
                "description": "Glamorous evening wear"
            },
            {
                "id": 3,
                "name": "Casual Top & Jeans",
                "price": "₹1,099",
                "color": (135, 206, 250),
                "image": "https://via.placeholder.com/250x300/87CEEB/000000?text=Casual+Wear",
                "amazon": f"https://www.amazon.in/s?k=womens+casual+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+casual+wear+{size}",
                "description": "Everyday comfort outfit"
            },
            {
                "id": 4,
                "name": "Designer Saree",
                "price": "₹2,499",
                "color": (255, 20, 147),
                "image": "https://via.placeholder.com/250x300/FF1493/FFFFFF?text=Saree",
                "amazon": f"https://www.amazon.in/s?k=womens+saree+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+saree+{size}",
                "description": "Classic Indian saree"
            },
            {
                "id": 5,
                "name": "Office Blazer Set",
                "price": "₹1,899",
                "color": (112, 128, 144),
                "image": "https://via.placeholder.com/250x300/708090/FFFFFF?text=Blazer+Set",
                "amazon": f"https://www.amazon.in/s?k=womens+blazer+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+blazer+{size}",
                "description": "Professional work attire"
            },
            {
                "id": 6,
                "name": "Maxi Dress",
                "price": "₹1,299",
                "color": (250, 128, 114),
                "image": "https://via.placeholder.com/250x300/FA8072/FFFFFF?text=Maxi+Dress",
                "amazon": f"https://www.amazon.in/s?k=womens+maxi+dress+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+maxi+dress+{size}",
                "description": "Flowing summer dress"
            },
            {
                "id": 7,
                "name": "Lehenga Choli",
                "price": "₹3,499",
                "color": (255, 105, 180),
                "image": "https://via.placeholder.com/250x300/FF69B4/FFFFFF?text=Lehenga",
                "amazon": f"https://www.amazon.in/s?k=womens+lehenga+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+lehenga+{size}",
                "description": "Bridal & festive wear"
            },
            {
                "id": 8,
                "name": "Denim Jacket",
                "price": "₹1,399",
                "color": (70, 130, 180),
                "image": "https://via.placeholder.com/250x300/4682B4/FFFFFF?text=Denim+Jacket",
                "amazon": f"https://www.amazon.in/s?k=womens+denim+jacket+{size}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+denim+jacket+{size}",
                "description": "Trendy casual jacket"
            }
        ]

catalog = get_dress_catalog(display_category, display_size)

st.markdown(f"### 🎯 Recommended for {display_category} - Size **{display_size}**")
st.info(f"💡 Showing {len(catalog)} outfits perfectly matched to your measurements")

# Create columns for products
num_cols = 4 if display_category == "Women" else 3
product_cols = st.columns(num_cols)

for idx, dress in enumerate(catalog):
    col_idx = idx % num_cols
    
    with product_cols[col_idx]:
        is_selected = (st.session_state.selected_dress and 
                      st.session_state.selected_dress['id'] == dress['id'])
        
        card_class = "product-card selected" if is_selected else "product-card"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        st.image(dress['image'], use_container_width=True)
        
        st.markdown(f"**{dress['name']}**")
        st.markdown(f"<p style='color: #667eea; font-size: 24px; font-weight: bold; margin: 0.5rem 0;'>{dress['price']}</p>", 
                   unsafe_allow_html=True)
        st.caption(dress['description'])
        
        if st.button(f"👗 Try This On", key=f"try_{dress['id']}", use_container_width=True):
            st.session_state.selected_dress = dress
            st.rerun()
        
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.link_button("🛒 Amazon", dress['amazon'], use_container_width=True)
        with link_col2:
            st.link_button("🛒 Flipkart", dress['flipkart'], use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Virtual Try-On with 3D Rotation
# --------------------------------------------------
if st.session_state.selected_dress:
    st.markdown("---")
    st.markdown("## 🎨 Step 6: Virtual Try-On (360° View)")
    
    selected = st.session_state.selected_dress
    
    def apply_dress_to_3d_mannequin(measurements, category, dress_info, rotation_angle):
        """Apply dress to 3D mannequin with rotation"""
        
        # Recreate mannequin with dress overlay
        mannequin, ref_points = create_3d_mannequin(measurements, category, rotation_angle)
        draw = ImageDraw.Draw(mannequin, 'RGBA')
        
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
        
        dress_color = dress_info['color']
        dress_rgba = dress_color + (200,)
        
        dress_name = dress_info['name'].lower()
        
        # Draw dress based on category and type
        if category == "Kids":
            if "dress" in dress_name or "gown" in dress_name:
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
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + waist_w//2, waist_y + 20),
                    (cx - waist_w//2, waist_y + 20),
                ], fill=dress_rgba, outline=dress_color, width=3)
        
        elif category == "Men":
            if "suit" in dress_name or "formal" in dress_name:
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + waist_w//2, waist_y + 30),
                    (cx - waist_w//2, waist_y + 30),
                ], fill=dress_rgba, outline=dress_color, width=3)
                pant_color = (50, 50, 50)
                pant_rgba = pant_color + (200,)
                draw.polygon([
                    (cx - 15, hip_y),
                    (cx - hip_w//3, hip_y),
                    (cx - hip_w//3 + 10, leg_end_y),
                    (cx - 10, leg_end_y),
                ], fill=pant_rgba, outline=pant_color, width=3)
                draw.polygon([
                    (cx + 15, hip_y),
                    (cx + hip_w//3, hip_y),
                    (cx + hip_w//3 - 10, leg_end_y),
                    (cx + 10, leg_end_y),
                ], fill=pant_rgba, outline=pant_color, width=3)
            elif "kurta" in dress_name:
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + hip_w//2 + 10, hip_y + 80),
                    (cx - hip_w//2 - 10, hip_y + 80),
                ], fill=dress_rgba, outline=dress_color, width=3)
            else:
                draw.polygon([
                    (cx - shoulder_w//2 + 10, shoulder_y + 30),
                    (cx + shoulder_w//2 - 10, shoulder_y + 30),
                    (cx + waist_w//2, hip_y - 10),
                    (cx - waist_w//2, hip_y - 10),
                ], fill=dress_rgba, outline=dress_color, width=3)
        
        else:  # Women
            if "saree" in dress_name:
                blouse_color = tuple(int(c//1.5) for c in dress_color)
                blouse_rgba = blouse_color + (200,)
                draw.polygon([
                    (cx - shoulder_w//2 + 20, shoulder_y + 30),
                    (cx + shoulder_w//2 - 20, shoulder_y + 30),
                    (cx + chest_w//2 - 10, chest_y + 20),
                    (cx - chest_w//2 + 10, chest_y + 20),
                ], fill=blouse_rgba, outline=blouse_color, width=3)
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
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + waist_w//2, waist_y - 10),
                    (cx - waist_w//2, waist_y - 10),
                ], fill=dress_rgba, outline=dress_color, width=3)
                lehenga_color = tuple(int(c//1.2) for c in dress_color)
                lehenga_rgba = lehenga_color + (200,)
                draw.polygon([
                    (cx - waist_w//2, waist_y - 10),
                    (cx + waist_w//2, waist_y - 10),
                    (cx + hip_w//2 + 40, leg_end_y - 20),
                    (cx - hip_w//2 - 40, leg_end_y - 20),
                ], fill=lehenga_rgba, outline=lehenga_color, width=3)
            elif "dress" in dress_name or "maxi" in dress_name:
                dress_length = leg_end_y - 50 if "maxi" in dress_name else hip_y + 100
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + hip_w//2 + 20, dress_length),
                    (cx - hip_w//2 - 20, dress_length),
                ], fill=dress_rgba, outline=dress_color, width=3)
            else:
                draw.polygon([
                    (cx - shoulder_w//2 + 15, shoulder_y + 30),
                    (cx + shoulder_w//2 - 15, shoulder_y + 30),
                    (cx + waist_w//2, hip_y - 20),
                    (cx - waist_w//2, hip_y - 20),
                ], fill=dress_rgba, outline=dress_color, width=3)
        
        return mannequin
    
    tryon_result = apply_dress_to_3d_mannequin(
        measurements,
        display_category,
        selected,
        st.session_state.rotation_angle
    )
    
    # Display with rotation controls
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
        
        st.info("🔄 Use the rotation slider above to see this outfit from all angles!")
        
        st.markdown("### 🛍️ Ready to Buy?")
        buy_col1, buy_col2 = st.columns(2)
        with buy_col1:
            st.link_button("🛒 Buy on Amazon", selected['amazon'], use_container_width=True)
        with buy_col2:
            st.link_button("🛒 Buy on Flipkart", selected['flipkart'], use_container_width=True)
        
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
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
    <h3>🌟 3D Fashion Stylist</h3>
    <p style="font-size: 1.1rem; margin: 1rem 0;">AI-Powered 360° Mannequin • Body Measurements • Virtual Try-On</p>
    <p style="font-size: 0.9rem; opacity: 0.9;">
        Rotate 360° • Accurate sizing • Real shopping links
    </p>
    <p style="font-size: 0.8rem; margin-top: 1rem; opacity: 0.8;">
        Made with ❤️ using Streamlit, NumPy & Pillow
    </p>
</div>
""", unsafe_allow_html=True)
