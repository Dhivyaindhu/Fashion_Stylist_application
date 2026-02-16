#3d fashion stylist pro
#stylist app

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import io, math, urllib.parse
from typing import Optional, Tuple, Dict, List

# ── MediaPipe (optional) ─────────────────────────────────────────────────────
try:
    import mediapipe as mp
    _MP_POSE = mp.solutions.pose
    MEDIAPIPE = True
except Exception:
    MEDIAPIPE = False

# ── rembg (optional) ─────────────────────────────────────────────────────────
try:
    from rembg import remove as rembg_remove
    REMBG = True
except Exception:
    REMBG = False

# ════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG & CSS
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="3D Fashion Stylist Pro", page_icon="👗",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
*{font-family:'DM Sans',sans-serif;}
.hero{
  background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
  padding:3rem 2rem;border-radius:24px;color:#fff;
  text-align:center;margin-bottom:2rem;
  box-shadow:0 20px 60px rgba(48,43,99,.5);
}
.hero h1{font-family:'DM Serif Display',serif;font-size:2.8rem;margin:0;
         background:linear-gradient(90deg,#f8cdda,#1d9bf0);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero p{font-size:1.1rem;opacity:.8;margin-top:.5rem;}
.card{background:#fff;border-radius:16px;padding:1.5rem;
      box-shadow:0 4px 24px rgba(0,0,0,.08);margin:.5rem 0;}
.section-title{font-family:'DM Serif Display',serif;font-size:1.8rem;
               color:#302b63;margin:1.5rem 0 .8rem;}
.measure-box{background:linear-gradient(135deg,#667eea15,#764ba215);
             border:1.5px solid #667eea44;border-radius:12px;
             padding:1rem;text-align:center;}
.measure-box h4{color:#667eea;margin:0 0 .4rem;font-size:.85rem;
                text-transform:uppercase;letter-spacing:.05em;}
.measure-box .val{font-size:1.6rem;font-weight:700;color:#302b63;}
.measure-box .sub{font-size:.8rem;color:#888;}
.product-card{border:1.5px solid #e5e7eb;border-radius:16px;padding:1rem;
              text-align:center;transition:.3s;cursor:pointer;height:100%;}
.product-card:hover{transform:translateY(-6px);
                    box-shadow:0 12px 32px rgba(102,126,234,.3);
                    border-color:#667eea;}
.fit-badge-perfect{background:#d1fae5;color:#065f46;
                   padding:.3rem .8rem;border-radius:99px;font-weight:600;font-size:.85rem;}
.fit-badge-good{background:#dbeafe;color:#1e40af;
                padding:.3rem .8rem;border-radius:99px;font-weight:600;font-size:.85rem;}
.fit-badge-moderate{background:#fef3c7;color:#92400e;
                    padding:.3rem .8rem;border-radius:99px;font-weight:600;font-size:.85rem;}
.fit-badge-poor{background:#fee2e2;color:#991b1b;
                padding:.3rem .8rem;border-radius:99px;font-weight:600;font-size:.85rem;}
div[data-testid="stButton"]>button{
  border-radius:12px;font-weight:600;padding:.6rem 1.2rem;
  background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>👗 3D Fashion Stylist Pro</h1>
  <p>AI Body Analysis · 360° Mannequin · Smart Recommendations · Virtual Try-On</p>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
for k in ['category','size','skin_tone','measurements','body_type',
          'mannequin_views','rot_angle']:
    if k not in st.session_state:
        st.session_state[k] = None
if st.session_state.rot_angle is None:
    st.session_state.rot_angle = 0

# ════════════════════════════════════════════════════════════════════════════
#  COLOUR UTILITIES  (pure Python / NumPy — no cv2)
# ════════════════════════════════════════════════════════════════════════════

def rgb_to_lab(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """sRGB (0-255) → CIELAB. Pure math, no external libs."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    def lin(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    r, g, b = lin(r), lin(g), lin(b)
    X = r*0.4124564 + g*0.3575761 + b*0.1804375
    Y = r*0.2126729 + g*0.7151522 + b*0.0721750
    Z = r*0.0193339 + g*0.1191920 + b*0.9503041
    X, Y, Z = X/0.95047, Y/1.00000, Z/1.08883

    def f(t):
        return t**(1/3) if t > 0.008856 else 7.787*t + 16/116

    fx, fy, fz = f(X), f(Y), f(Z)
    return 116*fy - 16, 500*(fx - fy), 200*(fy - fz)


def numpy_kmeans(pixels: np.ndarray, k: int = 3,
                 iters: int = 20) -> np.ndarray:
    """K-means on Nx3 float32. Returns centroids sorted by cluster size."""
    rng     = np.random.default_rng(42)
    idx     = rng.choice(len(pixels), k, replace=False)
    centres = pixels[idx].astype(np.float64)
    labels  = np.zeros(len(pixels), dtype=int)
    for _ in range(iters):
        dists  = np.linalg.norm(pixels[:,None,:] - centres[None,:,:], axis=2)
        labels = np.argmin(dists, axis=1)
        new_c  = np.array([
            pixels[labels==j].mean(axis=0) if (labels==j).any() else centres[j]
            for j in range(k)
        ])
        if np.allclose(new_c, centres, atol=0.5):
            break
        centres = new_c
    counts = np.array([(labels==j).sum() for j in range(k)])
    return centres[np.argsort(-counts)].astype(np.uint8)

# ════════════════════════════════════════════════════════════════════════════
#  SKIN-TONE  (ITA angle method)
# ════════════════════════════════════════════════════════════════════════════
SKIN_TONES = {
    "Fair"  :{"range":(55,90), "hex":"#FAD9C1","label":"Fair / Ivory",
              "flattering":["Navy","Burgundy","Forest Green","Charcoal","Rose Pink","Lavender"],
              "avoid":["Neon Yellow","Neon Orange","Beige","Cream"]},
    "Light" :{"range":(28,55), "hex":"#F5C5A3","label":"Light / Beige",
              "flattering":["Teal","Coral","Dusty Rose","Olive","Slate Blue","Plum"],
              "avoid":["Very Pale Yellow","Very Pale Pink"]},
    "Medium":{"range":(10,28), "hex":"#D4956A","label":"Medium / Tan",
              "flattering":["Cobalt Blue","Gold","Burnt Orange","Deep Red","White","Emerald"],
              "avoid":["Muddy Brown","Dark Olive"]},
    "Tan"   :{"range":(-30,10),"hex":"#B07850","label":"Tan / Caramel",
              "flattering":["Jewel Tones","Bright Yellow","Fuchsia","Turquoise","Cream","Rust"],
              "avoid":["Dull Brown","Khaki"]},
    "Deep"  :{"range":(-90,-30),"hex":"#6B3D2A","label":"Deep / Ebony",
              "flattering":["Bright White","Royal Blue","Vivid Red","Mustard","Neon","Gold"],
              "avoid":["Very Dark Navy","Black-on-Black"]},
}
HEX_COLORS = {
    "Navy":"#1B2A6B","Burgundy":"#800020","Forest Green":"#228B22","Charcoal":"#36454F",
    "Rose Pink":"#FF66B2","Lavender":"#B57EDC","Teal":"#008080","Coral":"#FF6B6B",
    "Dusty Rose":"#DCAE96","Olive":"#808000","Slate Blue":"#6A7FDB","Plum":"#DDA0DD",
    "Cobalt Blue":"#0047AB","Gold":"#FFD700","Burnt Orange":"#CC5500","Deep Red":"#8B0000",
    "White":"#FFFFFF","Emerald":"#50C878","Bright Yellow":"#FFFF00","Fuchsia":"#FF00FF",
    "Turquoise":"#40E0D0","Cream":"#FFFDD0","Rust":"#B7410E","Royal Blue":"#4169E1",
    "Vivid Red":"#FF0000","Mustard":"#FFDB58","Neon":"#39FF14","Jewel Tones":"#4B0082",
}


def classify_skin_tone(img: Image.Image) -> Tuple[str, str]:
    w, h = img.size
    crop = img.crop((int(w*.30), int(h*.05), int(w*.70), int(h*.30)))
    arr  = np.asarray(crop).reshape(-1, 3).astype(float)
    if len(arr) == 0:
        return "Medium", "#D4956A"
    mr, mg, mb = float(np.median(arr[:,0])), float(np.median(arr[:,1])), float(np.median(arr[:,2]))
    L, _, bv   = rgb_to_lab(mr, mg, mb)
    ita        = math.degrees(math.atan((L-50)/bv)) if bv != 0 else 90.0
    for tone, info in SKIN_TONES.items():
        if info["range"][0] <= ita <= info["range"][1]:
            return tone, info["hex"]
    return "Medium", "#D4956A"

# ════════════════════════════════════════════════════════════════════════════
#  BODY TYPES
# ════════════════════════════════════════════════════════════════════════════
WOMEN_TYPES = {
    "Full Hourglass":{"desc":"Very balanced shoulders & hips, dramatically defined waist",
                      "styles":["Wrap dresses","Belted midi dresses","Bodycon dresses","Fit-and-flare"],
                      "avoid":["Boxy tops","Drop-waist dresses"]},
    "Hourglass":     {"desc":"Balanced shoulders & hips, defined waist",
                      "styles":["Fitted dresses","Pencil skirts","High-waist trousers"],
                      "avoid":["Shift dresses","Baggy clothing"]},
    "Pear":          {"desc":"Hips noticeably wider than shoulders",
                      "styles":["A-line skirts","Boat-neck tops","Off-shoulder"],
                      "avoid":["Skinny jeans with tight tops","Clingy hip-length tops"]},
    "Inverted Triangle":{"desc":"Shoulders broader than hips",
                      "styles":["A-line skirts","Wide-leg pants","Maxi dresses"],
                      "avoid":["Strapless tops","Shoulder pads","Puffed sleeves"]},
    "Apple":         {"desc":"Fuller midsection, narrower hips",
                      "styles":["Empire-waist dresses","Flowy tunics","Wrap tops"],
                      "avoid":["Cropped tops","Clingy waist fabrics"]},
    "Rectangle":     {"desc":"Shoulders, waist & hips almost equal width",
                      "styles":["Peplum tops","Belted dresses","Ruffles"],
                      "avoid":["Straight-cut dresses with no waist definition"]},
    "Column":        {"desc":"Slim straight proportions",
                      "styles":["Tailored blazers","Structured midi dresses"],
                      "avoid":["Oversized silhouettes"]},
    "Brick":         {"desc":"Square torso, minimal waist definition",
                      "styles":["Wrap dresses","Fit-and-flare","Belted looks"],
                      "avoid":["Straight-cut silhouettes"]},
}
MEN_TYPES = {
    "Inverted Triangle":{"desc":"V-shape – broad shoulders, narrow waist",
                      "styles":["Slim-fit trousers","V-neck tees","Straight-cut jeans"],
                      "avoid":["Shoulder pads","Bulky jackets"]},
    "Trapezoid":     {"desc":"Athletic – shoulders slightly wider than hips",
                      "styles":["Tailored shirts","Chinos","Fitted blazers"],
                      "avoid":["Baggy shapeless clothing"]},
    "Rectangle":     {"desc":"Balanced proportions throughout",
                      "styles":["Layered outfits","Structured jackets","Cargo pants"],
                      "avoid":["Extremely slim-fit everything"]},
    "Column":        {"desc":"Tall & lean, minimal width variation",
                      "styles":["Layered looks","Bootcut trousers"],
                      "avoid":["Vertical stripes","Very slim silhouettes"]},
    "Triangle":      {"desc":"Hips wider than shoulders",
                      "styles":["Structured blazers","Dark bottoms","Light tops"],
                      "avoid":["Baggy trousers","Wide-leg pants"]},
    "Oval":          {"desc":"Broader midsection",
                      "styles":["Vertical stripes","Dark monochrome","Open-collar shirts"],
                      "avoid":["Tight tops","Horizontal stripes"]},
    "Circle":        {"desc":"Rounder figure, weight distributed evenly",
                      "styles":["Long cardigans","Straight-leg trousers","Structured blazers"],
                      "avoid":["Clingy fabrics","Very slim cuts"]},
    "Square":        {"desc":"Similar shoulder & hip width, minimal waist",
                      "styles":["Slim-fit bottoms","V-necks","Contrast-colour tops"],
                      "avoid":["Box-cut shirts","Boxy blazers"]},
}


def classify_body_type(sh: float, wh: float, wd: float, cat: str) -> str:
    if cat == "Women":
        if abs(sh-1.0) < 0.07 and wh < 0.75 and wd > 14: return "Full Hourglass"
        if abs(sh-1.0) < 0.10 and wh < 0.82 and wd > 8:  return "Hourglass"
        if sh < 0.92: return "Pear"
        if sh > 1.15: return "Inverted Triangle"
        if wh > 0.87: return "Apple"
        if wh > 0.82: return "Brick"
        return "Rectangle"
    elif cat == "Men":
        if sh > 1.20: return "Inverted Triangle"
        if sh > 1.10: return "Trapezoid"
        if sh < 0.93: return "Triangle"
        if wh > 0.92: return "Oval" if sh > 0.98 else "Circle"
        if abs(sh-1.0) < 0.06 and wh > 0.85: return "Square"
        if abs(sh-1.0) < 0.06: return "Rectangle"
        return "Column"
    return "Kids Proportions"

# ════════════════════════════════════════════════════════════════════════════
#  BODY DETECTION
# ════════════════════════════════════════════════════════════════════════════

def analyse_mediapipe(img: Image.Image, cat: str) -> Dict:
    arr  = np.asarray(img)
    h, w = arr.shape[:2]
    with _MP_POSE.Pose(static_image_mode=True, model_complexity=2,
                       min_detection_confidence=0.5) as pose:
        out = pose.process(arr)
    if not out.pose_landmarks:
        return {}
    lm = out.pose_landmarks.landmark
    def px(i): return np.array([lm[i].x*w, lm[i].y*h])
    LS,RS = px(11),px(12); LH,RH = px(23),px(24)
    LA,RA = px(27),px(28); nose  = px(0)
    sh_w  = float(np.linalg.norm(LS-RS))
    hp_w  = float(np.linalg.norm(LH-RH))
    wt_w  = sh_w*0.82
    mid_sh= (LS+RS)/2; mid_hp= (LH+RH)/2; mid_an= (LA+RA)/2
    torso = float(np.linalg.norm(mid_sh-mid_hp))
    legs  = float(np.linalg.norm(mid_hp-mid_an))
    head  = float(np.linalg.norm(mid_sh-nose))*1.4
    body  = head+torso+legs
    avg   = 162 if cat=="Women" else (175 if cat=="Men" else 125)
    p2c   = avg/max(body,1)
    s,h_,wc = sh_w*p2c, hp_w*p2c, wt_w*p2c
    return {"method":"mediapipe",
            "height_cm":round(body*p2c,1),"height_in":round(body*p2c/2.54,1),
            "shoulder_cm":round(s,1),"chest_cm":round(s*1.05,1),
            "waist_cm":round(wc,1),"waist_in":round(wc/2.54,1),
            "hip_cm":round(h_,1),"hip_in":round(h_/2.54,1),
            "shoulder_hip":round(s/max(h_,1),3),"waist_hip":round(wc/max(h_,1),3),
            "waist_def_cm":round(((s+h_)/2)-wc,1),
            "sh_w_px":int(sh_w),"hp_w_px":int(hp_w),"full_h_px":int(body)}


def analyse_pil(img: Image.Image, cat: str) -> Dict:
    """Pure PIL+NumPy fallback — no cv2."""
    gray = ImageOps.grayscale(img)
    arr  = np.asarray(gray)
    h, w = arr.shape
    thr  = int(np.percentile(arr, 30))
    mask = arr > thr
    rows = np.any(mask, axis=1); cols = np.any(mask, axis=0)
    rmin = int(np.argmax(rows))                          if rows.any() else int(h*.05)
    rmax = int(len(rows)-1-np.argmax(rows[::-1]))        if rows.any() else int(h*.95)
    cmin = int(np.argmax(cols))                          if cols.any() else int(w*.15)
    cmax = int(len(cols)-1-np.argmax(cols[::-1]))        if cols.any() else int(w*.85)
    bh,bw= max(rmax-rmin,1), max(cmax-cmin,1)
    avg  = 162 if cat=="Women" else (175 if cat=="Men" else 125)
    p2c  = avg/bh
    s,wc,hc = bw*.42*p2c, bw*.37*p2c, bw*.44*p2c
    ht   = bh*p2c
    return {"method":"fallback",
            "height_cm":round(ht,1),"height_in":round(ht/2.54,1),
            "shoulder_cm":round(s,1),"chest_cm":round(s*1.05,1),
            "waist_cm":round(wc,1),"waist_in":round(wc/2.54,1),
            "hip_cm":round(hc,1),"hip_in":round(hc/2.54,1),
            "shoulder_hip":round(s/max(hc,1),3),"waist_hip":round(wc/max(hc,1),3),
            "waist_def_cm":round(((s+hc)/2)-wc,1),
            "sh_w_px":int(bw*.42),"hp_w_px":int(bw*.44),"full_h_px":bh}

# ════════════════════════════════════════════════════════════════════════════
#  SIZE CHART
# ════════════════════════════════════════════════════════════════════════════

def recommend_size(m: Dict, cat: str) -> str:
    bust = m.get("chest_cm", m.get("shoulder_cm",38)*1.05)
    if cat=="Women":
        return "XS" if bust<80 else ("S" if bust<88 else ("M" if bust<96 else ("L" if bust<104 else "XL")))
    elif cat=="Men":
        return "S" if bust<88 else ("M" if bust<96 else ("L" if bust<104 else ("XL" if bust<112 else "XXL")))
    else:
        h=m.get("height_cm",120)
        return "3-4Y" if h<105 else ("5-6Y" if h<115 else ("7-8Y" if h<125 else ("9-10Y" if h<135 else "11-12Y")))

# ════════════════════════════════════════════════════════════════════════════
#  PROFESSIONAL MANNEQUIN RENDERER  (PIL only)
# ════════════════════════════════════════════════════════════════════════════

def _col_shade(draw, x, y1, y2, cx, hw, base):
    """Draw one shaded vertical column of a body part."""
    if hw <= 0 or y2 <= y1: return
    t  = (x-cx)/hw           # -1 .. +1
    sh = 0.60 + 0.40*(1-t*t)
    hi = 0.14*max(0,1-t*t)
    c  = (min(255,int(base[0]*sh+255*hi)),
          min(255,int(base[1]*sh+255*hi)),
          min(255,int(base[2]*sh+255*hi)))
    draw.line([(x,y1),(x,y2)], fill=c)


def render_mannequin(m: Dict, cat: str,
                     angle: float = 0,
                     dress_color: Optional[Tuple] = None) -> Image.Image:
    W,H   = 420,760
    img   = Image.new("RGB",(W,H),(248,248,250))
    draw  = ImageDraw.Draw(img)
    cx    = W//2

    depth = abs(math.cos(math.radians(angle%360)))
    f     = max(depth, 0.22)

    skin      = (234,206,185)
    skin_mid  = (210,175,148)
    skin_dark = (175,135,105)

    sh_w = max(int(m.get("shoulder_cm",38)*3.2*f), 26)
    hp_w = max(int(m.get("hip_cm",    37)*3.2*f), 26)
    wt_w = max(int(m.get("waist_cm",  28)*3.2*f), 20)

    HEAD_R=30; NECK_H=22; TRS_H=200; PEL_H=38
    THI_H=118; KNE_H=18; SHN_H=128; FOT_H=22

    y = 30
    # floor shadow
    for o in range(20,0,-1):
        v=int(155*(1-o/20))
        draw.ellipse([cx-int(sh_w*1.3)-o,H-16,cx+int(sh_w*1.3)+o,H-4],fill=(v,v,v+8))
    draw.rounded_rectangle([cx-72,H-22,cx+72,H-4],radius=6,fill=(195,190,210))

    # HEAD
    for xi in range(cx-HEAD_R, cx+HEAD_R+1):
        dx=xi-cx
        if abs(dx)>HEAD_R: continue
        hy=int(HEAD_R*math.sqrt(max(0,1-(dx/HEAD_R)**2)))
        _col_shade(draw,xi,y,y+hy*2,cx,HEAD_R,skin)
    y+=HEAD_R*2+2

    # NECK
    for xi in range(cx-11,cx+12):
        _col_shade(draw,xi,y,y+NECK_H,cx,11,skin_mid)
    y+=NECK_H

    # TORSO (Bézier-like contour)
    tt=y
    for i in range(TRS_H):
        t=i/TRS_H
        if   t<0.32: hw=int(sh_w*.50+(sh_w*.54-sh_w*.50)*(t/.32))
        elif t<0.58: hw=int(sh_w*.54-(sh_w*.54-wt_w*.50)*((t-.32)/.26))
        else:        hw=int(wt_w*.50+(hp_w*.50-wt_w*.50)*((t-.58)/.42))
        ry=tt+i
        for xi in range(cx-hw,cx+hw+1): _col_shade(draw,xi,ry,ry+1,cx,max(hw,1),skin_mid)
    y=tt+TRS_H

    # PELVIS
    for i in range(PEL_H):
        hw=int(hp_w*.50-hp_w*.04*(i/PEL_H))
        for xi in range(cx-hw,cx+hw+1): _col_shade(draw,xi,y+i,y+i+1,cx,max(hw,1),skin_mid)
    y+=PEL_H

    # LEGS
    gap=max(5,int(hp_w*.12))
    for sg in (-1,1):
        lx=cx+sg*(int(hp_w*.26)+gap); ly=y
        for i in range(THI_H):
            r=max(5,int(hp_w*.21-hp_w*.07*(i/THI_H)))
            for xi in range(lx-r,lx+r+1): _col_shade(draw,xi,ly+i,ly+i+1,lx,r,skin)
        ly+=THI_H
        kw=int(hp_w*.13)
        for xi in range(lx-kw,lx+kw+1): _col_shade(draw,xi,ly,ly+KNE_H,lx,kw,skin_dark)
        ly+=KNE_H
        for i in range(SHN_H):
            r=max(4,int(hp_w*.12-hp_w*.04*(i/SHN_H)))
            for xi in range(lx-r,lx+r+1): _col_shade(draw,xi,ly+i,ly+i+1,lx,r,skin)
        ly+=SHN_H
        fw=int(hp_w*.15)
        draw.rounded_rectangle([lx-fw,ly,lx+fw+sg*5,ly+FOT_H],radius=7,fill=(75,65,60))

    # ARMS
    for sg in (-1,1):
        ax=cx+sg*int(sh_w*.54); ay=tt+10; alen=int(TRS_H*.86)
        for i in range(alen):
            ox=sg*int(sh_w*.14*(i/alen))
            r=max(5,int(sh_w*.14-sh_w*.06*(i/alen)))
            for xi in range(ax+ox-r,ax+ox+r+1): _col_shade(draw,xi,ay+i,ay+i+1,ax+ox,r,skin)

    # DRESS OVERLAY
    if dress_color:
        dr,dg,db=dress_color
        d_top=tt+4; d_bot=tt+TRS_H+PEL_H+int(THI_H*.65); dh2=d_bot-d_top
        for i in range(dh2):
            t=i/dh2
            if   t<0.32: hw=int(sh_w*.55+(sh_w*.57-sh_w*.55)*(t/.32))
            elif t<0.58: hw=int(sh_w*.57-(sh_w*.57-wt_w*.53)*((t-.32)/.26))
            else:        hw=int(wt_w*.53+(hp_w*.65-wt_w*.53)*((t-.58)/.42))
            ry=d_top+i
            for xi in range(cx-hw,cx+hw+1):
                tx=(xi-cx)/max(hw,1); sh=0.72+0.28*(1-tx*tx)
                c=(min(255,int(dr*sh+25*(1-tx*tx))),
                   min(255,int(dg*sh+18*(1-tx*tx))),
                   min(255,int(db*sh+18*(1-tx*tx))))
                draw.point((xi,ry),fill=c)

    return img.filter(ImageFilter.SMOOTH_MORE)


def build_rotation_views(m, cat, dress_color=None):
    return [render_mannequin(m, cat, a, dress_color) for a in range(0,360,45)]

# ════════════════════════════════════════════════════════════════════════════
#  DRESS SEGMENTATION  (PIL only, no cv2)
# ════════════════════════════════════════════════════════════════════════════

def _pil_bg_remove(img: Image.Image) -> Image.Image:
    """Corner-sample background colour → distance mask → RGBA."""
    rgba = img.convert("RGBA")
    arr  = np.asarray(rgba).astype(np.int32)
    h,w  = arr.shape[:2]
    corners = np.concatenate([arr[:10,:10,:3].reshape(-1,3),
                               arr[:10,-10:,:3].reshape(-1,3),
                               arr[-10:,:10,:3].reshape(-1,3),
                               arr[-10:,-10:,:3].reshape(-1,3)],axis=0)
    bg   = corners.mean(axis=0)
    diff = arr[:,:,:3].astype(float)-bg
    dist = np.sqrt((diff**2).sum(axis=2))
    alpha= np.where(dist>55,255,0).astype(np.uint8)
    am   = Image.fromarray(alpha,"L")
    am   = am.filter(ImageFilter.MinFilter(3))
    am   = am.filter(ImageFilter.MaxFilter(5))
    am   = am.filter(ImageFilter.SMOOTH)
    r,g,b,_ = rgba.split()
    return Image.merge("RGBA",(r,g,b,am))


def extract_dress_color(img: Image.Image) -> Tuple[Tuple,Image.Image]:
    processed = rembg_remove(img).convert("RGBA") if REMBG else _pil_bg_remove(img)
    arr = np.asarray(processed)
    fg  = arr[arr[:,:,3]>128][:,:3] if arr.shape[2]==4 else arr.reshape(-1,3)
    if len(fg)<3: return (180,180,195), processed
    step  = max(1,len(fg)//3000)
    ctrs  = numpy_kmeans(fg[::step].astype(np.float32),k=3,iters=25)
    return tuple(int(c) for c in ctrs[0]), processed

# ════════════════════════════════════════════════════════════════════════════
#  FIT PREDICTION
# ════════════════════════════════════════════════════════════════════════════

def predict_fit(dw,dh,sh_px,h_px) -> Dict:
    d_asp=dw/max(dh,1); m_asp=sh_px*2/max(h_px,1)
    wr=d_asp/max(m_asp,.01); lr=dh/max(h_px,1)
    wv=(("Loose","poor") if wr>1.22 else
        ("Slightly Loose","moderate") if wr>1.09 else
        ("Perfect Fit","perfect") if wr>0.91 else
        ("Slightly Tight","moderate") if wr>0.79 else ("Tight","poor"))
    lv=(("Floor Length","good") if lr>.80 else
        ("Midi","perfect")       if lr>.65 else
        ("Knee Length","perfect")if lr>.50 else
        ("Mini","good")          if lr>.38 else ("Crop / Very Short","moderate"))
    sc={"perfect":3,"good":2,"moderate":1,"poor":0}
    avg=(sc[wv[1]]+sc[lv[1]])/2
    ov=(("✅ Great Fit","perfect")    if avg>=2.5 else
        ("👍 Good Fit","good")        if avg>=1.5 else
        ("⚠️ Needs Alteration","moderate") if avg>=.8 else ("❌ Poor Fit","poor"))
    return {"width":wv,"length":lv,"overall":ov}

# ════════════════════════════════════════════════════════════════════════════
#  VIRTUAL TRY-ON  (PIL only)
# ════════════════════════════════════════════════════════════════════════════

def virtual_tryon(mannequin: Image.Image,
                  dress_rgba: Image.Image, m: Dict) -> Image.Image:
    result = mannequin.copy().convert("RGBA")
    W,H=result.size; cx=W//2
    sh_w=int(m.get("shoulder_cm",38)*3.2)
    hp_w=int(m.get("hip_cm",37)*3.2)
    x1=cx-int(sh_w*.56); x2=cx+int(sh_w*.56)
    y1=int(H*.15);        y2=int(H*.72)
    dw2,dh2=x2-x1,y2-y1
    dress_r=dress_rgba.resize((dw2,dh2),Image.LANCZOS)
    # hip-flare warp (PIL only)
    darr=np.asarray(dress_r).astype(np.float32)
    oarr=np.zeros_like(darr)
    for row in range(dh2):
        flare=1.0+0.12*(row/dh2)**2
        for col in range(dw2):
            src=int((col/dw2)*dw2*(1/flare)+(dw2*(1-1/flare)/2))
            src=max(0,min(src,dw2-1))
            oarr[row,col]=darr[row,src]
    dw3=Image.fromarray(oarr.astype(np.uint8))
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    if dw3.mode=="RGBA":
        overlay.paste(dw3,(x1,y1),mask=dw3.split()[3])
    else:
        overlay.paste(dw3.convert("RGBA"),(x1,y1))
    return Image.alpha_composite(result,overlay).convert("RGB")

# ════════════════════════════════════════════════════════════════════════════
#  RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════
STYLE_TERMS = {
    "Full Hourglass":["wrap dress women","belted midi dress","bodycon dress"],
    "Hourglass"     :["fit and flare dress","fitted dress women","pencil skirt"],
    "Pear"          :["a-line skirt women","boat neck top","flared trousers women"],
    "Inverted Triangle":["a-line maxi dress","wide leg pants women","flowy skirt"],
    "Apple"         :["empire waist dress","flowy tunic top","wrap blouse women"],
    "Rectangle"     :["peplum top women","belted dress","ruffle hem dress"],
    "Column"        :["tailored blazer women","straight leg trousers","structured dress"],
    "Brick"         :["wrap dress women","fit and flare dress","belted midi dress"],
    "Trapezoid"     :["tailored shirt men","chinos men","fitted blazer men"],
    "Triangle"      :["structured blazer men","padded shoulder jacket","light top dark bottom"],
    "Oval"          :["vertical stripe shirt men","dark monochrome suit","slim trousers men"],
    "Circle"        :["long cardigan men","straight leg trousers men","dark blazer men"],
    "Square"        :["belted jacket men","v-neck sweater men","slim fit chinos men"],
    "Kids Proportions":["kids comfortable dress","kids casual outfit","kids summer dress"],
}

def rec_cards(bt,skin_tone,fav):
    terms=STYLE_TERMS.get(bt,["dress","outfit","clothing"])
    colour=fav[0].lower() if fav else ""
    cards=[]
    for t in terms[:6]:
        q=f"{colour} {t}".strip()
        cards.append({"title":t.title(),"desc":f"{bt} · {skin_tone} palette",
                      "amazon":f"https://www.amazon.in/s?k={urllib.parse.quote_plus(q)}",
                      "flipkart":f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(q)}"})
    return cards

# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛠️ AI Engine")
    st.success("✅ PIL + NumPy (always active — no cv2)")
    st.success("✅ MediaPipe BlazePose") if MEDIAPIPE else st.warning("⚠️ MediaPipe not found\n`pip install mediapipe`")
    st.success("✅ rembg U²-Net") if REMBG else st.info("ℹ️ rembg not found → PIL BG removal\n`pip install rembg`")

# ════════════════════════════════════════════════════════════════════════════
#  STEP 1 — UPLOAD PHOTO
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">📸 Step 1 — Upload Your Photo</p>', unsafe_allow_html=True)
st.caption("Full-body photo with good lighting and a plain background works best.")
uploaded = st.file_uploader("", type=["jpg","jpeg","png"], key="person")
if not uploaded:
    st.info("👆 Upload a full-body photo to begin."); st.stop()
person_img = Image.open(uploaded).convert("RGB")

# ════════════════════════════════════════════════════════════════════════════
#  STEP 2 — CATEGORY
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">👥 Step 2 — Select Category</p>', unsafe_allow_html=True)
c1,c2,c3=st.columns(3)
with c1:
    if st.button("👶  Children",use_container_width=True): st.session_state.category="Kids"; st.rerun()
with c2:
    if st.button("👨  Men",     use_container_width=True): st.session_state.category="Men";  st.rerun()
with c3:
    if st.button("👩  Women",   use_container_width=True): st.session_state.category="Women";st.rerun()
category=st.session_state.category
if not category: st.warning("⚠️ Please select a category above."); st.stop()
st.success(f"Selected: **{category}**")

# ════════════════════════════════════════════════════════════════════════════
#  STEP 3 — ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🔬 Step 3 — Body Analysis</p>', unsafe_allow_html=True)
with st.spinner("🧠 Analysing…"):
    m = analyse_mediapipe(person_img,category) if MEDIAPIPE else {}
    if not m: m = analyse_pil(person_img,category)
    skin_tone,skin_hex = classify_skin_tone(person_img)
    bt   = classify_body_type(m["shoulder_hip"],m["waist_hip"],m["waist_def_cm"],category)
    size = recommend_size(m,category)
    views= build_rotation_views(m,category)
    st.session_state.update({"measurements":m,"skin_tone":skin_tone,
                              "body_type":bt,"size":size,"mannequin_views":views})

ca,cb,cc = st.columns(3)
with ca:
    st.markdown("#### 📷 Your Photo"); st.image(person_img,use_container_width=True)

tone_info = SKIN_TONES.get(skin_tone,SKIN_TONES["Medium"])
bt_info   = (MEN_TYPES if category=="Men" else WOMEN_TYPES).get(bt,
             {"desc":"Balanced","styles":["All styles"],"avoid":[]})

with cb:
    sty = "".join(f"<span style='background:#667eea18;border-radius:8px;padding:.2rem .6rem;margin:2px;display:inline-block;font-size:.85rem'>{s}</span>" for s in bt_info["styles"])
    avd = "".join(f"<span style='background:#fee2e218;border-radius:8px;padding:.2rem .6rem;margin:2px;display:inline-block;font-size:.85rem'>{s}</span>" for s in bt_info["avoid"])
    st.markdown(f"<div class='card'><h4 style='color:#302b63;margin-top:0'>🎯 Body Type</h4><h2 style='color:#667eea;margin:.2rem 0'>{bt}</h2><p style='color:#555;font-size:.9rem'>{bt_info['desc']}</p><hr style='margin:.8rem 0;border:0;border-top:1px solid #eee'><h4 style='color:#302b63'>👗 Flattering Styles</h4>{sty}<h4 style='color:#e53e3e;margin-top:1rem'>✗ Avoid</h4>{avd}</div>",unsafe_allow_html=True)

with cc:
    def _chip(c):
        bg = HEX_COLORS.get(c, "#ccc")
        return f"<span class='color-chip' style='background:{bg}' title='{c}'></span>"
    chips        = "".join(_chip(c) for c in tone_info["flattering"][:8])
    flat_str     = "  ·  ".join(tone_info["flattering"][:6])
    avoid_str    = "  ·  ".join(tone_info["avoid"])
    tone_label   = tone_info["label"]
    st.markdown(
        f"<div class='card'>"
        f"<h4 style='color:#302b63;margin-top:0'>🎨 Skin Tone</h4>"
        f"<div style='display:flex;align-items:center;gap:1rem;margin:.5rem 0'>"
        f"<div style='width:56px;height:56px;border-radius:50%;background:{skin_hex};"
        f"border:3px solid #eee;box-shadow:0 2px 8px rgba(0,0,0,.15)'></div>"
        f"<div><strong style='font-size:1.2rem'>{tone_label}</strong><br>"
        f"<span style='color:#888;font-size:.85rem'>ITA method</span></div></div>"
        f"<hr style='margin:.8rem 0;border:0;border-top:1px solid #eee'>"
        f"<h5 style='color:#28a745'>✅ Flattering</h5>{chips}"
        f"<div style='margin-top:.4rem;font-size:.8rem;color:#555'>{flat_str}</div>"
        f"<h5 style='color:#e53e3e;margin-top:.8rem'>✗ Avoid</h5>"
        f"<div style='font-size:.85rem;color:#888'>{avoid_str}</div></div>",
        unsafe_allow_html=True)

st.markdown("#### 📏 Estimated Measurements")
inch = '"'   # inch symbol — avoids backslash-in-f-string on older Python
for col,(lab,val,sub) in zip(st.columns(6),[
    ("Height",   f"{m.get('height_cm','—')} cm",  f"{m.get('height_in','—')}{inch}"),
    ("Shoulder", f"{m.get('shoulder_cm','—')} cm", ""),
    ("Chest",    f"{m.get('chest_cm','—')} cm",    ""),
    ("Waist",    f"{m.get('waist_cm','—')} cm",    f"{m.get('waist_in','—')}{inch}"),
    ("Hip",      f"{m.get('hip_cm','—')} cm",      f"{m.get('hip_in','—')}{inch}"),
    ("Size",     size,                             "Recommended"),
]):
    col.markdown(f"<div class='measure-box'><h4>{lab}</h4><div class='val'>{val}</div><div class='sub'>{sub}</div></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  STEP 4 — 360° MANNEQUIN
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-title">🧍 Step 4 — 360° Mannequin</p>', unsafe_allow_html=True)
views=st.session_state.mannequin_views or []
if views:
    angle=st.slider("🔄 Rotate",0,315,st.session_state.rot_angle,step=45,format="%d°")
    st.session_state.rot_angle=angle
    _,mc,_=st.columns([1,2,1])
    with mc:
        st.image(views[(angle//45)%8],caption=f"{angle}°  ·  {bt}  ·  Size {size}",use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
#  STEP 5 — RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-title">🛍️ Step 5 — Personalised Recommendations</p>', unsafe_allow_html=True)
cards=rec_cards(bt,skin_tone,tone_info["flattering"])
for i in range(0,len(cards),3):
    row=cards[i:i+3]
    for col,card in zip(st.columns(len(row)),row):
        with col:
            st.markdown(f"<div class='product-card'><div style='font-size:2.5rem'>👗</div><h4 style='color:#302b63;margin:.5rem 0 .2rem'>{card['title']}</h4><p style='font-size:.8rem;color:#777;margin:0 0 1rem'>{card['desc']}</p><a href='{card['amazon']}' target='_blank' style='display:block;background:linear-gradient(135deg,#ff9900,#e47911);color:#fff;padding:.5rem;border-radius:8px;text-decoration:none;font-weight:600;font-size:.85rem;margin-bottom:.4rem'>🛒 Amazon India</a><a href='{card['flipkart']}' target='_blank' style='display:block;background:linear-gradient(135deg,#2874f0,#1652b5);color:#fff;padding:.5rem;border-radius:8px;text-decoration:none;font-weight:600;font-size:.85rem'>🛍️ Flipkart</a></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  STEP 6 — VIRTUAL TRY-ON
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<p class="section-title">👗 Step 6 — Virtual Try-On</p>', unsafe_allow_html=True)
st.caption("Upload any dress image — product listing, model photo, or flat lay.")
dress_file=st.file_uploader("",type=["jpg","jpeg","png"],key="dress",label_visibility="collapsed")
if dress_file:
    dress_img=Image.open(dress_file).convert("RGB"); dw,dh=dress_img.size
    with st.spinner("✂️ Segmenting garment…"):
        dress_color,dress_rgba=extract_dress_color(dress_img)
    d1,d2,d3=st.columns(3)
    with d1:
        st.markdown("#### 🖼️ Dress Input"); st.image(dress_img,use_container_width=True)
    with d2:
        st.markdown("#### ✂️ Segmented"); st.image(dress_rgba.convert("RGB"),use_container_width=True)
        dr,dg,db=dress_color
        st.markdown(f"<div style='text-align:center;margin-top:.5rem'><div style='width:50px;height:50px;border-radius:50%;background:rgb({dr},{dg},{db});margin:.5rem auto;border:3px solid #eee;box-shadow:0 2px 8px rgba(0,0,0,.2)'></div><span style='font-size:.85rem;color:#555'>RGB({dr},{dg},{db})</span></div>",unsafe_allow_html=True)
    with st.spinner("🎨 Rendering try-on…"):
        base=render_mannequin(m,category,0)
        tryon=virtual_tryon(base,dress_rgba,m)
    with d3:
        st.markdown("#### 🧍 Try-On Result"); st.image(tryon,use_container_width=True)

    st.markdown("---"); st.markdown("### 📐 Fit Prediction")
    fit=predict_fit(dw,dh,m.get("sh_w_px",120),m.get("full_h_px",400))
    badges={"perfect":"fit-badge-perfect","good":"fit-badge-good","moderate":"fit-badge-moderate","poor":"fit-badge-poor"}
    for col,(label,verdict) in zip(st.columns(3),[("Width Fit",fit["width"]),("Length",fit["length"]),("Overall",fit["overall"])]):
        col.markdown(f"<div class='card' style='text-align:center'><h4 style='color:#302b63'>{label}</h4><span class='{badges[verdict[1]]}'>{verdict[0]}</span></div>",unsafe_allow_html=True)

    buf=io.BytesIO(); tryon.save(buf,format="PNG")
    st.download_button("⬇️ Download Try-On Image",buf.getvalue(),"virtual_tryon.png","image/png",use_container_width=True)

st.markdown("---")
st.markdown("<div style='text-align:center;padding:2rem;background:linear-gradient(135deg,#0f0c29,#302b63);border-radius:20px;color:#fff;'><h3 style='font-family:\"DM Serif Display\",serif;margin:0'>👗 3D Fashion Stylist Pro</h3><p style='opacity:.7;margin:.5rem 0 0'>PIL · NumPy · ITA Skin Analysis · 360° Mannequin · Virtual Try-On</p></div>",unsafe_allow_html=True)
#stylist fashion stylist app got updated...



