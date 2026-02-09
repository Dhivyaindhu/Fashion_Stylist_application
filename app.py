import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mediapipe as mp
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

# Custom CSS for better UI
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
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
    2. **AI Detection** using MediaPipe
    3. **Measurements** extracted automatically
    4. **Size Prediction** based on body metrics
    5. **Virtual Try-On** with mannequin
    6. **Shopping Links** to buy recommended outfits
    """)
    
    st.header("📸 Photo Guidelines")
    st.info("""
    ✅ Full body visible\n
    ✅ Good lighting\n
    ✅ Standing straight\n
    ✅ Arms slightly away from body\n
    ❌ No sitting/crouching\n
    ❌ No group photos
    """)

# --------------------------------------------------
# Initialize MediaPipe
# --------------------------------------------------
@st.cache_resource
def load_pose_detector():
    return mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        min_detection_confidence=0.5
    )

mp_pose = load_pose_detector()
mp_drawing = mp.solutions.drawing_utils

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
        st.metric("Confidence", "95%", help="Detection accuracy")
    
    st.stop()

# --------------------------------------------------
# Process Uploaded Image
# --------------------------------------------------
image = Image.open(uploaded_file).convert("RGB")

# Display original image
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("#### Original Image")
    st.image(image, use_container_width=True)

# Convert to numpy array for processing
image_np = np.array(image)
image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

# --------------------------------------------------
# Pose Detection
# --------------------------------------------------
with st.spinner("🔍 Analyzing body pose..."):
    results = mp_pose.process(image_rgb)

if not results.pose_landmarks:
    st.error("❌ Could not detect full body. Please upload a clearer image showing your entire body.")
    st.stop()

# Draw pose landmarks
annotated_image = image_np.copy()
mp_drawing.draw_landmarks(
    annotated_image,
    results.pose_landmarks,
    mp.solutions.pose.POSE_CONNECTIONS,
    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
)

with col2:
    st.markdown("#### Pose Detection")
    st.image(annotated_image, use_container_width=True)

landmarks = results.pose_landmarks.landmark

# --------------------------------------------------
# Body Measurements Extraction
# --------------------------------------------------
def calculate_distance(point1, point2, img_width, img_height):
    """Calculate Euclidean distance between two landmarks"""
    x1, y1 = point1.x * img_width, point1.y * img_height
    x2, y2 = point2.x * img_width, point2.y * img_height
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def extract_detailed_measurements(landmarks, img_width, img_height):
    """Extract comprehensive body measurements"""
    
    # Key landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    NOSE = 0
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    
    # Shoulder width
    shoulder_width = calculate_distance(
        landmarks[LEFT_SHOULDER],
        landmarks[RIGHT_SHOULDER],
        img_width, img_height
    )
    
    # Hip width
    hip_width = calculate_distance(
        landmarks[LEFT_HIP],
        landmarks[RIGHT_HIP],
        img_width, img_height
    )
    
    # Chest width (approximate - shoulder to elbow midpoint)
    chest_width = shoulder_width * 1.2  # Approximation
    
    # Total height (nose to ankle midpoint)
    left_ankle_y = landmarks[LEFT_ANKLE].y * img_height
    right_ankle_y = landmarks[RIGHT_ANKLE].y * img_height
    ankle_avg_y = (left_ankle_y + right_ankle_y) / 2
    
    nose_y = landmarks[NOSE].y * img_height
    total_height = ankle_avg_y - nose_y
    
    # Torso height (shoulder to hip)
    shoulder_y = (landmarks[LEFT_SHOULDER].y + landmarks[RIGHT_SHOULDER].y) / 2 * img_height
    hip_y = (landmarks[LEFT_HIP].y + landmarks[RIGHT_HIP].y) / 2 * img_height
    torso_height = hip_y - shoulder_y
    
    # Leg length (hip to ankle)
    leg_length = ankle_avg_y - hip_y
    
    # Waist approximation (between chest and hip)
    waist_width = (chest_width + hip_width) / 2 * 0.85
    
    return {
        "shoulder_width": shoulder_width,
        "chest_width": chest_width,
        "waist_width": waist_width,
        "hip_width": hip_width,
        "total_height": total_height,
        "torso_height": torso_height,
        "leg_length": leg_length,
        "shoulder_hip_ratio": shoulder_width / hip_width if hip_width > 0 else 1.0
    }

img_height, img_width = image_np.shape[:2]
measurements = extract_detailed_measurements(landmarks, img_width, img_height)

# --------------------------------------------------
# Size & Category Classification
# --------------------------------------------------
def classify_person_advanced(measurements, img_height):
    """Advanced classification based on multiple measurements"""
    
    total_height = measurements["total_height"]
    shoulder_hip_ratio = measurements["shoulder_hip_ratio"]
    shoulder_width = measurements["shoulder_width"]
    hip_width = measurements["hip_width"]
    
    # Normalize by image height
    height_ratio = total_height / img_height
    
    # Kids detection (smaller proportions)
    if height_ratio < 0.55 or total_height < img_height * 0.6:
        category = "Kids"
        # Size based on height
        if total_height < img_height * 0.45:
            size = "XS"
        elif total_height < img_height * 0.52:
            size = "S"
        else:
            size = "M"
        return category, size, 0.90
    
    # Adult classification based on shoulder-hip ratio
    if shoulder_hip_ratio > 1.05:  # Shoulders wider than hips
        category = "Men"
    else:
        category = "Women"
    
    # Size determination based on shoulder width
    shoulder_percentile = shoulder_width / img_width
    
    if category == "Men":
        if shoulder_percentile < 0.28:
            size = "S"
        elif shoulder_percentile < 0.34:
            size = "M"
        elif shoulder_percentile < 0.40:
            size = "L"
        else:
            size = "XL"
    else:  # Women
        if shoulder_percentile < 0.25:
            size = "XS"
        elif shoulder_percentile < 0.30:
            size = "S"
        elif shoulder_percentile < 0.35:
            size = "M"
        elif shoulder_percentile < 0.40:
            size = "L"
        else:
            size = "XL"
    
    # Confidence based on visibility and proportion
    confidence = min(0.95, 0.75 + (height_ratio * 0.3))
    
    return category, size, confidence

category, size, confidence = classify_person_advanced(measurements, img_height)

# --------------------------------------------------
# Display Results
# --------------------------------------------------
st.markdown("---")
st.success("✅ Analysis Complete!")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👤 Category", category, help="Detected clothing category")
with col2:
    st.metric("📏 Recommended Size", size, help="Best fit size")
with col3:
    st.metric("🎯 Confidence", f"{int(confidence * 100)}%", help="Detection accuracy")

# Detailed measurements
st.markdown("### 📊 Detailed Body Measurements")

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
# Generate Mannequin/Avatar
# --------------------------------------------------
def generate_mannequin(img, landmarks, img_width, img_height, category):
    """Generate a stylized mannequin from the detected pose"""
    
    # Create a white canvas
    mannequin = Image.new('RGB', (300, 600), color='white')
    draw = ImageDraw.Draw(mannequin, 'RGBA')
    
    # Scale factor
    scale_x = 300 / img_width
    scale_y = 600 / img_height
    
    # Get key points
    points = {}
    for idx, lm in enumerate(landmarks):
        points[idx] = (int(lm.x * img_width * scale_x), int(lm.y * img_height * scale_y))
    
    # Colors based on category
    if category == "Men":
        skin_color = (255, 220, 177)
        clothing_color = (100, 149, 237)  # Cornflower blue
    elif category == "Women":
        skin_color = (255, 228, 196)
        clothing_color = (255, 182, 193)  # Light pink
    else:  # Kids
        skin_color = (255, 235, 205)
        clothing_color = (255, 215, 0)  # Gold
    
    # Draw body parts (simplified mannequin)
    # Head
    if 0 in points:
        draw.ellipse([points[0][0]-20, points[0][1]-20, 
                     points[0][0]+20, points[0][1]+20], 
                    fill=skin_color, outline=(0,0,0), width=2)
    
    # Torso (rectangle between shoulders and hips)
    if 11 in points and 12 in points and 23 in points and 24 in points:
        torso_points = [
            points[11], points[12], points[24], points[23]
        ]
        draw.polygon(torso_points, fill=clothing_color, outline=(0,0,0), width=2)
    
    # Arms
    arm_points = [(11, 13), (13, 15), (12, 14), (14, 16)]  # Shoulders to elbows to wrists
    for start, end in arm_points:
        if start in points and end in points:
            draw.line([points[start], points[end]], fill=skin_color, width=8)
            draw.line([points[start], points[end]], fill=(0,0,0), width=2)
    
    # Legs
    leg_points = [(23, 25), (25, 27), (24, 26), (26, 28)]  # Hips to knees to ankles
    for start, end in leg_points:
        if start in points and end in points:
            draw.line([points[start], points[end]], fill=(70, 130, 180), width=10)
            draw.line([points[start], points[end]], fill=(0,0,0), width=2)
    
    # Add joints
    for idx in [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]:
        if idx in points:
            draw.ellipse([points[idx][0]-5, points[idx][1]-5,
                         points[idx][0]+5, points[idx][1]+5],
                        fill=(0,0,0))
    
    return mannequin

mannequin = generate_mannequin(image, landmarks, img_width, img_height, category)

st.markdown("### 🧍 Generated Mannequin")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(mannequin, use_container_width=True)

# --------------------------------------------------
# Virtual Try-On Simulation
# --------------------------------------------------
def create_virtual_tryon(mannequin_img, category, size):
    """Overlay clothing on mannequin"""
    
    overlay = mannequin_img.copy()
    draw = ImageDraw.Draw(overlay, 'RGBA')
    
    # Clothing colors by category
    if category == "Men":
        shirt_color = (30, 144, 255, 200)  # Dodger blue
        pants_color = (25, 25, 112, 200)  # Midnight blue
    elif category == "Women":
        shirt_color = (255, 105, 180, 200)  # Hot pink
        pants_color = (138, 43, 226, 200)  # Blue violet
    else:  # Kids
        shirt_color = (255, 165, 0, 200)  # Orange
        pants_color = (50, 205, 50, 200)  # Lime green
    
    # Draw shirt/top
    draw.rectangle([60, 100, 240, 280], fill=shirt_color, outline=(0,0,0,255), width=2)
    
    # Draw pants/bottom
    # Left leg
    draw.polygon([(90, 280), (120, 280), (125, 500), (85, 500)], 
                 fill=pants_color, outline=(0,0,0,255), width=2)
    # Right leg
    draw.polygon([(180, 280), (210, 280), (215, 500), (175, 500)], 
                 fill=pants_color, outline=(0,0,0,255), width=2)
    
    # Add size label
    try:
        # Try to use a font, fallback to default if not available
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((120, 50), f"Size: {size}", fill=(0,0,0), font=font)
    
    return overlay

tryon_result = create_virtual_tryon(mannequin, category, size)

st.markdown("### 👕 Virtual Try-On Preview")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(tryon_result, use_container_width=True)

st.info("💡 This is a simplified preview. Select products below to see specific outfits!")

# --------------------------------------------------
# Product Recommendations
# --------------------------------------------------
st.markdown("---")
st.markdown("### 🛍️ Recommended Products")

def get_product_recommendations(category, size):
    """Get product recommendations with real shopping links"""
    
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

# Display products in columns
cols = st.columns(3)
for idx, product in enumerate(products):
    with cols[idx]:
        st.markdown(f"""
        <div class="product-card">
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
# Additional Features
# --------------------------------------------------
st.markdown("---")
st.markdown("### 🎯 Size Guide")

with st.expander("📏 Click to view detailed size chart"):
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
    else:  # Kids
        st.markdown("""
        | Size | Age Range | Height (cm) | Chest (inches) |
        |------|-----------|-------------|----------------|
        | XS   | 2-4 years | 90-100      | 22-24          |
        | S    | 4-6 years | 100-115     | 24-26          |
        | M    | 6-8 years | 115-130     | 26-28          |
        | L    | 8-10 years| 130-145     | 28-30          |
        """)

# --------------------------------------------------
# Download & Share Options
# --------------------------------------------------
st.markdown("### 💾 Save Your Results")

col1, col2 = st.columns(2)
with col1:
    # Create a summary image
    buf = io.BytesIO()
    mannequin.save(buf, format='PNG')
    st.download_button(
        label="⬇️ Download Mannequin",
        data=buf.getvalue(),
        file_name=f"mannequin_{category}_{size}.png",
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
    <p>Powered by MediaPipe & Streamlit | Made with ❤️</p>
    <p style="font-size: 0.8rem;">
        This is a demo application. Actual measurements may vary. 
        Always check size charts before purchasing.
    </p>
</div>
""", unsafe_allow_html=True)
