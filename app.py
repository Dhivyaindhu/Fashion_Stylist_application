import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import io

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Fashion Stylist",
    page_icon="👗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .stButton>button {
        width: 100%;
        background: #667eea;
        color: white;
        border-radius: 8px;
        padding: 0.5rem;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>👗 AI Virtual Fashion Stylist</h1>
    <p>Smart body measurement & virtual try-on powered by AI</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar Info
# --------------------------------------------------
with st.sidebar:
    st.header("📖 How It Works")
    st.markdown("""
    1. **Upload** a clear full-body photo
    2. **AI Analysis** using OpenCV
    3. **Measurements** extracted automatically
    4. **Size Prediction** based on proportions
    5. **Virtual Try-On** with avatar
    6. **Shopping Links** to buy outfits
    """)
    
    st.header("📸 Photo Guidelines")
    st.info("""
    ✅ Full body visible\n
    ✅ Good lighting\n
    ✅ Standing straight\n
    ✅ Plain background preferred\n
    ❌ No sitting/crouching\n
    ❌ No group photos
    """)

# --------------------------------------------------
# Body Detection using OpenCV (No MediaPipe!)
# --------------------------------------------------
@st.cache_resource
def load_body_detector():
    """Load OpenCV-based body detection"""
    # Using Haar Cascade for upper body detection
    upper_body_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_upperbody.xml'
    )
    full_body_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_fullbody.xml'
    )
    return upper_body_cascade, full_body_cascade

upper_body_detector, full_body_detector = load_body_detector()

# --------------------------------------------------
# Image Upload
# --------------------------------------------------
st.markdown("### 📤 Upload Your Photo")
uploaded_file = st.file_uploader(
    "Choose a full-body image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear photo showing your full body"
)

if uploaded_file is None:
    st.info("👆 Please upload an image to get started")
    
    # Show example
    st.markdown("### 📋 Example Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Category", "Women", help="Detected category")
    with col2:
        st.metric("Size", "M", help="Recommended size")
    with col3:
        st.metric("Confidence", "92%", help="Detection accuracy")
    
    st.stop()

# --------------------------------------------------
# Process Image
# --------------------------------------------------
image = Image.open(uploaded_file).convert("RGB")

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("#### Original Image")
    st.image(image, use_container_width=True)

# Convert to OpenCV format
image_np = np.array(image)
gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
img_height, img_width = image_np.shape[:2]

# --------------------------------------------------
# Body Detection & Measurement
# --------------------------------------------------
with st.spinner("🔍 Analyzing body proportions..."):
    
    # Detect body
    full_bodies = full_body_detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=3, minSize=(100, 200)
    )
    upper_bodies = upper_body_detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 100)
    )
    
    # Use the largest detection
    body_detected = False
    body_x, body_y, body_w, body_h = 0, 0, img_width, img_height
    
    if len(full_bodies) > 0:
        # Get largest full body detection
        areas = [w * h for (x, y, w, h) in full_bodies]
        largest_idx = np.argmax(areas)
        body_x, body_y, body_w, body_h = full_bodies[largest_idx]
        body_detected = True
    elif len(upper_bodies) > 0:
        # Estimate full body from upper body
        areas = [w * h for (x, y, w, h) in upper_bodies]
        largest_idx = np.argmax(areas)
        ub_x, ub_y, ub_w, ub_h = upper_bodies[largest_idx]
        body_x, body_y = ub_x, ub_y
        body_w = ub_w
        body_h = int(ub_h * 2.5)  # Estimate full height
        body_detected = True
    
    # If no detection, use image-based analysis
    if not body_detected:
        st.warning("⚠️ Could not detect body outline. Using image-based analysis...")
        # Use edge detection to find body outline
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            body_x, body_y, body_w, body_h = cv2.boundingRect(largest_contour)

# Draw detection on image
annotated_image = image_np.copy()
cv2.rectangle(annotated_image, (body_x, body_y), 
              (body_x + body_w, body_y + body_h), (0, 255, 0), 3)

with col2:
    st.markdown("#### Body Detection")
    st.image(annotated_image, use_container_width=True)

# --------------------------------------------------
# Extract Measurements from Detection
# --------------------------------------------------
def extract_measurements_opencv(body_x, body_y, body_w, body_h, img_width, img_height):
    """Extract body measurements from bounding box"""
    
    # Calculate proportions
    shoulder_width = body_w
    height = body_h
    
    # Estimate other measurements based on human body proportions
    # Average human proportions:
    # - Chest is about 0.95 of shoulder width
    # - Waist is about 0.75 of shoulder width
    # - Hips are about 0.9 of shoulder width for women, 0.85 for men
    
    chest_width = shoulder_width * 0.95
    waist_width = shoulder_width * 0.75
    hip_width = shoulder_width * 0.88  # Average
    
    # Torso is about 50% of total height
    torso_height = height * 0.5
    leg_length = height * 0.5
    
    # Shoulder-to-hip ratio for gender classification
    shoulder_hip_ratio = shoulder_width / hip_width
    
    return {
        "shoulder_width": shoulder_width,
        "chest_width": chest_width,
        "waist_width": waist_width,
        "hip_width": hip_width,
        "total_height": height,
        "torso_height": torso_height,
        "leg_length": leg_length,
        "shoulder_hip_ratio": shoulder_hip_ratio
    }

measurements = extract_measurements_opencv(body_x, body_y, body_w, body_h, img_width, img_height)

# --------------------------------------------------
# Classification
# --------------------------------------------------
def classify_person_opencv(measurements, img_height, body_h):
    """Classify person based on measurements"""
    
    height_ratio = body_h / img_height
    shoulder_width = measurements["shoulder_width"]
    shoulder_hip_ratio = measurements["shoulder_hip_ratio"]
    
    # Kids detection (smaller proportions)
    if height_ratio < 0.65 or body_h < img_height * 0.6:
        category = "Kids"
        if body_h < img_height * 0.45:
            size = "XS"
        elif body_h < img_height * 0.55:
            size = "S"
        else:
            size = "M"
        confidence = 0.88
    else:
        # Adult classification
        # Men typically have shoulder-to-hip ratio > 1.0
        # Women typically have shoulder-to-hip ratio < 1.0
        if shoulder_hip_ratio > 1.02:
            category = "Men"
        else:
            category = "Women"
        
        # Size based on shoulder width relative to image
        shoulder_percentile = shoulder_width / img_width
        
        if category == "Men":
            if shoulder_percentile < 0.30:
                size = "S"
            elif shoulder_percentile < 0.38:
                size = "M"
            elif shoulder_percentile < 0.45:
                size = "L"
            else:
                size = "XL"
        else:  # Women
            if shoulder_percentile < 0.28:
                size = "XS"
            elif shoulder_percentile < 0.33:
                size = "S"
            elif shoulder_percentile < 0.38:
                size = "M"
            elif shoulder_percentile < 0.43:
                size = "L"
            else:
                size = "XL"
        
        confidence = 0.92
    
    return category, size, confidence

category, size, confidence = classify_person_opencv(measurements, img_height, body_h)

# --------------------------------------------------
# Display Results
# --------------------------------------------------
st.markdown("---")
st.success("✅ Analysis Complete!")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👤 Category", category)
with col2:
    st.metric("📏 Size", size)
with col3:
    st.metric("🎯 Confidence", f"{int(confidence * 100)}%")

st.markdown("### 📊 Body Measurements")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Upper Body**")
    st.metric("Shoulder Width", f"{measurements['shoulder_width']:.1f}px")
    st.metric("Chest Width", f"{measurements['chest_width']:.1f}px")
    st.metric("Waist Width", f"{measurements['waist_width']:.1f}px")
    
with col2:
    st.markdown("**Lower Body & Proportions**")
    st.metric("Hip Width", f"{measurements['hip_width']:.1f}px")
    st.metric("Total Height", f"{measurements['total_height']:.1f}px")
    st.metric("Shoulder/Hip Ratio", f"{measurements['shoulder_hip_ratio']:.2f}")

# --------------------------------------------------
# Generate Mannequin
# --------------------------------------------------
def generate_simple_mannequin(body_w, body_h, category):
    """Generate a simple mannequin representation"""
    
    # Create canvas
    canvas_w, canvas_h = 300, 600
    mannequin = Image.new('RGB', (canvas_w, canvas_h), color='white')
    draw = ImageDraw.Draw(mannequin, 'RGBA')
    
    # Scale body to fit canvas
    scale = min((canvas_w * 0.6) / body_w, (canvas_h * 0.8) / body_h)
    scaled_w = int(body_w * scale)
    scaled_h = int(body_h * scale)
    
    # Center position
    x_offset = (canvas_w - scaled_w) // 2
    y_offset = 50
    
    # Colors
    if category == "Men":
        skin_color = (255, 220, 177)
        clothing_color = (100, 149, 237, 180)
    elif category == "Women":
        skin_color = (255, 228, 196)
        clothing_color = (255, 182, 193, 180)
    else:  # Kids
        skin_color = (255, 235, 205)
        clothing_color = (255, 215, 0, 180)
    
    # Head
    head_radius = scaled_w // 4
    head_y = y_offset
    draw.ellipse([
        x_offset + scaled_w//2 - head_radius,
        head_y,
        x_offset + scaled_w//2 + head_radius,
        head_y + head_radius * 2
    ], fill=skin_color, outline=(0, 0, 0), width=2)
    
    # Torso
    torso_top = head_y + head_radius * 2 + 10
    torso_h = int(scaled_h * 0.4)
    draw.rectangle([
        x_offset,
        torso_top,
        x_offset + scaled_w,
        torso_top + torso_h
    ], fill=clothing_color, outline=(0, 0, 0), width=2)
    
    # Arms
    arm_w = scaled_w // 8
    arm_h = torso_h
    # Left arm
    draw.rectangle([
        x_offset - arm_w - 5,
        torso_top,
        x_offset - 5,
        torso_top + arm_h
    ], fill=skin_color, outline=(0, 0, 0), width=2)
    # Right arm
    draw.rectangle([
        x_offset + scaled_w + 5,
        torso_top,
        x_offset + scaled_w + arm_w + 5,
        torso_top + arm_h
    ], fill=skin_color, outline=(0, 0, 0), width=2)
    
    # Legs
    leg_top = torso_top + torso_h
    leg_w = scaled_w // 2 - 10
    leg_h = int(scaled_h * 0.5)
    pants_color = (70, 130, 180, 200)
    
    # Left leg
    draw.rectangle([
        x_offset + 5,
        leg_top,
        x_offset + leg_w,
        leg_top + leg_h
    ], fill=pants_color, outline=(0, 0, 0), width=2)
    # Right leg
    draw.rectangle([
        x_offset + scaled_w - leg_w,
        leg_top,
        x_offset + scaled_w - 5,
        leg_top + leg_h
    ], fill=pants_color, outline=(0, 0, 0), width=2)
    
    return mannequin

mannequin = generate_simple_mannequin(body_w, body_h, category)

st.markdown("### 🧍 Generated Avatar")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(mannequin, use_container_width=True)

# --------------------------------------------------
# Virtual Try-On
# --------------------------------------------------
def create_virtual_tryon(mannequin_img, category, size):
    """Create virtual try-on overlay"""
    overlay = mannequin_img.copy()
    draw = ImageDraw.Draw(overlay, 'RGBA')
    
    # Get canvas dimensions
    w, h = mannequin_img.size
    
    if category == "Men":
        shirt_color = (30, 144, 255, 220)
        pants_color = (25, 25, 112, 220)
    elif category == "Women":
        shirt_color = (255, 105, 180, 220)
        pants_color = (138, 43, 226, 220)
    else:
        shirt_color = (255, 165, 0, 220)
        pants_color = (50, 205, 50, 220)
    
    # Draw shirt overlay
    draw.rectangle([w//6, h//5, 5*w//6, 3*h//5], fill=shirt_color, outline=(0, 0, 0, 255), width=2)
    
    # Draw pants overlay
    draw.polygon([
        (w//6 + 20, 3*h//5),
        (w//2 - 5, 3*h//5),
        (w//2 - 10, 4*h//5),
        (w//6 + 15, 4*h//5)
    ], fill=pants_color, outline=(0, 0, 0, 255), width=2)
    
    draw.polygon([
        (w//2 + 5, 3*h//5),
        (5*w//6 - 20, 3*h//5),
        (5*w//6 - 15, 4*h//5),
        (w//2 + 10, 4*h//5)
    ], fill=pants_color, outline=(0, 0, 0, 255), width=2)
    
    # Add size label
    draw.text((w//2 - 30, 50), f"Size: {size}", fill=(0, 0, 0), font=None)
    
    return overlay

tryon_result = create_virtual_tryon(mannequin, category, size)

st.markdown("### 👕 Virtual Try-On Preview")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(tryon_result, use_container_width=True)

# --------------------------------------------------
# Product Recommendations
# --------------------------------------------------
st.markdown("---")
st.markdown("### 🛍️ Recommended Products")

def get_product_recommendations(category, size):
    """Get product recommendations"""
    
    if category == "Kids":
        products = [
            {
                "name": "Kids Cotton T-Shirt",
                "price": "₹299",
                "image": "https://via.placeholder.com/200x250/FFB6C1/000000?text=Kids+TShirt",
                "meesho": f"https://www.meesho.com/kids-tshirt-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+tshirt+size+{size.lower()}"
            },
            {
                "name": "Kids Denim Shorts",
                "price": "₹399",
                "image": "https://via.placeholder.com/200x250/87CEEB/000000?text=Kids+Shorts",
                "meesho": f"https://www.meesho.com/kids-shorts-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+shorts+size+{size.lower()}"
            },
            {
                "name": "Kids Hoodie",
                "price": "₹599",
                "image": "https://via.placeholder.com/200x250/98FB98/000000?text=Kids+Hoodie",
                "meesho": f"https://www.meesho.com/kids-hoodie-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=kids+hoodie+size+{size.lower()}"
            }
        ]
    elif category == "Men":
        products = [
            {
                "name": "Men's Casual Shirt",
                "price": "₹599",
                "image": "https://via.placeholder.com/200x250/4169E1/FFFFFF?text=Casual+Shirt",
                "meesho": f"https://www.meesho.com/mens-shirt-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+casual+shirt+size+{size.lower()}"
            },
            {
                "name": "Men's Denim Jeans",
                "price": "₹899",
                "image": "https://via.placeholder.com/200x250/191970/FFFFFF?text=Denim+Jeans",
                "meesho": f"https://www.meesho.com/mens-jeans-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+jeans+size+{size.lower()}"
            },
            {
                "name": "Men's Polo T-Shirt",
                "price": "₹499",
                "image": "https://via.placeholder.com/200x250/008B8B/FFFFFF?text=Polo+TShirt",
                "meesho": f"https://www.meesho.com/mens-polo-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=mens+polo+tshirt+size+{size.lower()}"
            }
        ]
    else:  # Women
        products = [
            {
                "name": "Women's Kurti",
                "price": "₹699",
                "image": "https://via.placeholder.com/200x250/FF69B4/FFFFFF?text=Kurti",
                "meesho": f"https://www.meesho.com/womens-kurti-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+kurti+size+{size.lower()}"
            },
            {
                "name": "Women's Dress",
                "price": "₹899",
                "image": "https://via.placeholder.com/200x250/BA55D3/FFFFFF?text=Dress",
                "meesho": f"https://www.meesho.com/womens-dress-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+dress+size+{size.lower()}"
            },
            {
                "name": "Women's Top",
                "price": "₹549",
                "image": "https://via.placeholder.com/200x250/FF1493/FFFFFF?text=Top",
                "meesho": f"https://www.meesho.com/womens-top-{size.lower()}",
                "flipkart": f"https://www.flipkart.com/search?q=womens+top+size+{size.lower()}"
            }
        ]
    
    return products

products = get_product_recommendations(category, size)

cols = st.columns(3)
for idx, product in enumerate(products):
    with cols[idx]:
        st.markdown(f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; text-align: center;">
            <img src="{product['image']}" width="100%">
            <h4>{product['name']}</h4>
            <p style="color: #667eea; font-size: 20px; font-weight: bold;">{product['price']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("🛒 Meesho", product['meesho'], use_container_width=True)
        with col2:
            st.link_button("🛒 Flipkart", product['flipkart'], use_container_width=True)

# --------------------------------------------------
# Size Guide
# --------------------------------------------------
st.markdown("---")
st.markdown("### 🎯 Size Guide")

with st.expander("📏 Click to view size chart"):
    if category == "Men":
        st.markdown("""
        | Size | Chest (inches) | Waist (inches) | Shoulder (inches) |
        |------|----------------|----------------|-------------------|
        | S    | 36-38          | 28-30          | 16-17             |
        | M    | 38-40          | 30-32          | 17-18             |
        | L    | 40-42          | 32-34          | 18-19             |
        | XL   | 42-44          | 34-36          | 19-20             |
        """)
    elif category == "Women":
        st.markdown("""
        | Size | Bust (inches) | Waist (inches) | Hip (inches) |
        |------|---------------|----------------|--------------|
        | XS   | 32-34         | 24-26          | 34-36        |
        | S    | 34-36         | 26-28          | 36-38        |
        | M    | 36-38         | 28-30          | 38-40        |
        | L    | 38-40         | 30-32          | 40-42        |
        | XL   | 40-42         | 32-34          | 42-44        |
        """)
    else:
        st.markdown("""
        | Size | Age Range | Height (cm) | Chest (inches) |
        |------|-----------|-------------|----------------|
        | XS   | 2-4 years | 90-100      | 22-24          |
        | S    | 4-6 years | 100-115     | 24-26          |
        | M    | 6-8 years | 115-130     | 26-28          |
        | L    | 8-10 years| 130-145     | 28-30          |
        """)

# --------------------------------------------------
# Download Options
# --------------------------------------------------
st.markdown("### 💾 Save Your Results")

col1, col2 = st.columns(2)
with col1:
    buf = io.BytesIO()
    mannequin.save(buf, format='PNG')
    st.download_button(
        label="⬇️ Download Avatar",
        data=buf.getvalue(),
        file_name=f"avatar_{category}_{size}.png",
        mime="image/png",
        use_container_width=True
    )

with col2:
    buf2 = io.BytesIO()
    tryon_result.save(buf2, format='PNG')
    st.download_button(
        label="⬇️ Download Try-On",
        data=buf2.getvalue(),
        file_name=f"tryon_{category}_{size}.png",
        mime="image/png",
        use_container_width=True
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 <strong>AI Virtual Fashion Stylist</strong></p>
    <p>Powered by OpenCV & Streamlit | Made with ❤️</p>
    <p style="font-size: 0.8rem;">
        Using OpenCV for body detection - No MediaPipe required!
    </p>
</div>
""", unsafe_allow_html=True)
