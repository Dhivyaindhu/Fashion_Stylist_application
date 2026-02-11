import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io, math

# ============================
# CONFIG
# ============================
st.set_page_config(
    page_title="3D Fashion Stylist Pro",
    page_icon="🧸",
    layout="wide"
)

# ============================
# STYLES
# ============================
st.markdown("""
<style>
* { font-family: 'Poppins', sans-serif; }
.main-header {
background: linear-gradient(135deg,#667eea,#764ba2);
padding:3rem;border-radius:20px;color:white;text-align:center;
}
.body-type-card {
background:#e3f2fd;padding:2rem;border-radius:15px;
border:3px solid #2196f3;
}
.measurement-grid {
display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
gap:1rem;
}
.measure-item {
background:white;padding:1rem;border-radius:10px;
border-left:4px solid #667eea;text-align:center;
}
.product-card {
background:white;border:2px solid #ddd;border-radius:15px;
padding:1rem;text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
<h1>🧸 3D Fashion Stylist Pro</h1>
<p>Body Type • Skin Tone • Product Recommendation • Try-On</p>
</div>
""", unsafe_allow_html=True)

# ============================
# SESSION STATE
# ============================
for k in [
    "user_category","measurements","body_type",
    "skin_tone","size","toy","ref"
]:
    if k not in st.session_state:
        st.session_state[k] = None

# ============================
# UPLOAD USER IMAGE
# ============================
st.markdown("## 📤 Upload Full-Body Image")
uploaded = st.file_uploader("Upload Image", ["jpg","jpeg","png"])
if not uploaded:
    st.stop()

img = Image.open(uploaded).convert("RGB")
arr = np.array(img)
h, w = arr.shape[:2]

# ============================
# CATEGORY
# ============================
st.markdown("## 🎯 Select Category")
c1,c2,c3 = st.columns(3)
if c1.button("👶 Kids"): st.session_state.user_category="Kids"
if c2.button("👨 Men"): st.session_state.user_category="Men"
if c3.button("👩 Women"): st.session_state.user_category="Women"

if not st.session_state.user_category:
    st.warning("Select category")
    st.stop()

cat = st.session_state.user_category

# ============================
# SIMPLE BODY DETECTION
# ============================
gray = np.mean(arr, axis=2)
mask = gray > np.percentile(gray,25)
rows = np.any(mask,axis=1)
cols = np.any(mask,axis=0)
rmin,rmax = np.where(rows)[0][[0,-1]]
cmin,cmax = np.where(cols)[0][[0,-1]]
bh = rmax-rmin
bw = cmax-cmin

# ============================
# MEASUREMENTS
# ============================
avg_h = 162 if cat=="Women" else 175 if cat=="Men" else 120
px2cm = avg_h/bh

m = {
    "height_cm":round(bh*px2cm,1),
    "shoulder_cm":round(bw*0.42*px2cm,1),
    "waist_cm":round(bw*0.38*px2cm,1),
    "hip_cm":round(bw*0.44*px2cm,1),
}
st.session_state.measurements = m

# ============================
# BODY TYPE
# ============================
sh = m["shoulder_cm"]/m["hip_cm"]
wh = m["waist_cm"]/m["hip_cm"]

def body_type(cat):
    if cat=="Women":
        if abs(sh-1)<0.08 and wh<0.8: return "Hourglass"
        if sh<0.95: return "Pear"
        if sh>1.1: return "Inverted Triangle"
        return "Rectangle"
    if cat=="Men":
        return "Athletic" if sh>1.1 else "Rectangle"
    return "Kids"

st.session_state.body_type = body_type(cat)

# ============================
# SIZE
# ============================
if cat=="Women":
    st.session_state.size = "S" if m["waist_cm"]<70 else "M" if m["waist_cm"]<80 else "L"
elif cat=="Men":
    st.session_state.size = "M" if m["chest_cm"]<95 else "L"
else:
    st.session_state.size = "8-10Y"

# ============================
# SKIN TONE
# ============================
brightness = np.mean(arr[rmin:rmin+int(bh*0.25),cmin:cmax])
if brightness>210: tone="Fair"
elif brightness>180: tone="Light"
elif brightness>145: tone="Medium"
elif brightness>110: tone="Tan"
else: tone="Deep"
st.session_state.skin_tone = tone

# ============================
# DISPLAY USER INFO
# ============================
st.markdown("## 📊 Analysis")
st.markdown(f"""
<div class="body-type-card">
<h3>Body Type: {st.session_state.body_type}</h3>
<p>Size: <b>{st.session_state.size}</b></p>
<p>Skin Tone: <b>{st.session_state.skin_tone}</b></p>
</div>
""", unsafe_allow_html=True)

# ============================
# SKIN TONE COLOR MAP
# ============================
def skin_colors(t):
    return {
        "Fair":["Pastel Pink","Lavender","Mint"],
        "Light":["Peach","Teal","Coral"],
        "Medium":["Royal Blue","Emerald","Mustard"],
        "Tan":["Olive","Rust","Navy"],
        "Deep":["White","Gold","Cobalt"]
    }[t]

# ============================
# PRODUCT CATALOG (SAFE)
# ============================
PRODUCTS = [
    {
        "title":"A-Line Dress",
        "color":"Royal Blue",
        "sizes":["S","M","L"],
        "platform":"Amazon",
        "image":"https://m.media-amazon.com/images/I/71example.jpg",
        "link":"https://www.amazon.in/"
    },
    {
        "title":"Wrap Dress",
        "color":"Emerald",
        "sizes":["M","L","XL"],
        "platform":"Flipkart",
        "image":"https://rukminim2.flixcart.com/image/example.jpg",
        "link":"https://www.flipkart.com/"
    },
    {
        "title":"Casual Shirt",
        "color":"Navy",
        "sizes":["M","L"],
        "platform":"Amazon",
        "image":"https://m.media-amazon.com/images/I/72example.jpg",
        "link":"https://www.amazon.in/"
    }
]

# ============================
# RECOMMENDATIONS
# ============================
st.markdown("## 🛍️ Recommended Products")

allowed = skin_colors(st.session_state.skin_tone)
reco = [
    p for p in PRODUCTS
    if st.session_state.size in p["sizes"]
    and p["color"] in allowed
]

cols = st.columns(3)
for i,p in enumerate(reco):
    with cols[i%3]:
        st.image(p["image"], use_container_width=True)
        st.markdown(f"**{p['title']}**")
        st.markdown(f"🎨 {p['color']}")
        st.markdown(f"🛒 {p['platform']}")
        st.link_button("Open Product", p["link"])

st.info("👉 Open product → Save image → Upload below")

# ============================
# UPLOAD DRESS
# ============================
st.markdown("## 👗 Upload Dress Image")
dress = st.file_uploader("Upload Dress",["jpg","png","jpeg"])
if not dress:
    st.stop()

dress_img = Image.open(dress).convert("RGB")
st.image(dress_img,use_container_width=True)

# ============================
# SIMPLE TRY-ON
# ============================
toy = Image.new("RGB",(400,650),(245,245,250))
draw = ImageDraw.Draw(toy)
draw.rectangle([140,180,260,420],fill=np.median(np.array(dress_img),axis=(0,1)))

st.markdown("## 🎨 Virtual Try-On")
st.image(toy,use_container_width=True)

# ============================
# FIT VERDICT
# ============================
def fit_verdict(bt,size):
    if bt in ["Hourglass","Athletic"]: return "✅ Perfect Fit"
    if size in ["XS","S"]: return "⚠️ May be tight"
    return "👍 Comfortable"

st.success(f"📏 Fit Verdict: {fit_verdict(st.session_state.body_type, st.session_state.size)}")

# ============================
# DOWNLOAD
# ============================
buf = io.BytesIO()
toy.save(buf,"PNG")
st.download_button("⬇️ Download Try-On",buf.getvalue(),"tryon.png","image/png")
