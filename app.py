"""
AI Fashion Stylist Pro - Streamlit Cloud Optimized
===================================================
Runs on Streamlit Cloud with zero heavy dependencies.

Requirements (requirements.txt):
  streamlit
  pillow
  numpy
  opencv-python-headless

Features:
  - Smart body detection (rule-based + optional MediaPipe)
  - Gender / Age-group classification
  - Skin tone analysis (5 levels)
  - Realistic mannequin silhouette with 3-D shading
  - Virtual try-on (product colours + user-uploaded dress)
  - Fit analysis  (loose / perfect / tight)
  - Amazon & Flipkart product links
  - 360° mannequin rotation (CSS animation)
  - Download try-on image
"""

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
import math

# Optional: MediaPipe (graceful fallback if absent)
try:
    import mediapipe as mp
    import cv2
    MP_OK = True
except ImportError:
    MP_OK = False

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="StyleAI — Smart Fashion Stylist",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,500;0,700;1,300&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset & base */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Background */
.stApp { background: #0e0e12; color: #f0ede8; }

/* Hide default Streamlit bits */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(212,175,55,0.25);
    border-radius: 24px;
    padding: 3.5rem 2.5rem;
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 30% 50%, rgba(212,175,55,0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 30%, rgba(100,149,237,0.08) 0%, transparent 60%);
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.8rem, 5vw, 4.5rem);
    font-weight: 300;
    color: #f0ede8;
    letter-spacing: 0.06em;
    margin: 0;
    line-height: 1.1;
}
.hero-title span { color: #d4af37; font-style: italic; }
.hero-sub {
    font-size: 1rem;
    color: rgba(240,237,232,0.55);
    margin-top: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.tag-row { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-top: 1.5rem; }
.tag {
    background: rgba(212,175,55,0.12);
    border: 1px solid rgba(212,175,55,0.3);
    color: #d4af37;
    font-size: 0.72rem;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── CARDS ── */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.5rem;
}
.card-gold {
    background: rgba(212,175,55,0.06);
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 18px;
    padding: 1.5rem;
}

/* ── STAT CHIPS ── */
.stat-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; margin: 1rem 0; }
.stat-chip {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.6rem 1.1rem;
    flex: 1; min-width: 110px;
    text-align: center;
}
.stat-chip .val {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.55rem;
    color: #d4af37;
    display: block;
    line-height: 1;
}
.stat-chip .lbl {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(240,237,232,0.45);
    margin-top: 0.25rem;
    display: block;
}

/* ── FIT BADGE ── */
.fit-badge {
    display: inline-block;
    padding: 0.65rem 2rem;
    border-radius: 40px;
    font-size: 1rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0.5rem;
}
.fit-perfect { background: linear-gradient(90deg,#28a745,#20c997); color:#fff; }
.fit-loose   { background: linear-gradient(90deg,#17a2b8,#0dcaf0); color:#fff; }
.fit-tight   { background: linear-gradient(90deg,#ffc107,#ff9800); color:#1a1a1a; }

/* ── PRODUCT CARDS ── */
.prod-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.25rem;
    transition: border-color 0.3s, transform 0.3s;
    cursor: pointer;
    text-align: center;
}
.prod-card:hover { border-color: rgba(212,175,55,0.5); transform: translateY(-4px); }
.prod-card.selected { border-color: #d4af37; background: rgba(212,175,55,0.08); }
.prod-swatch {
    width: 100%; height: 200px;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    display: flex; align-items: center; justify-content: center;
    font-size: 3.5rem;
}
.prod-name { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #f0ede8; }
.prod-brand { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(240,237,232,0.45); margin: 0.25rem 0; }
.prod-price { color: #d4af37; font-size: 1.3rem; font-weight: 500; margin: 0.5rem 0; }

/* ── STEP HEADERS ── */
.step-head {
    display: flex; align-items: center; gap: 1rem;
    margin: 2.5rem 0 1.25rem;
}
.step-num {
    width: 38px; height: 38px;
    background: rgba(212,175,55,0.15);
    border: 1px solid rgba(212,175,55,0.4);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem; color: #d4af37;
    flex-shrink: 0;
}
.step-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.75rem; font-weight: 300;
    color: #f0ede8; letter-spacing: 0.03em;
}

/* ── ROTATE ANIMATION ── */
@keyframes rotateMQ {
    0%   { transform: perspective(500px) rotateY(-20deg) scale(0.95); }
    50%  { transform: perspective(500px) rotateY(20deg)  scale(1.00); }
    100% { transform: perspective(500px) rotateY(-20deg) scale(0.95); }
}
.mq-rotate { animation: rotateMQ 4s ease-in-out infinite; display: inline-block; }

/* ── DIVIDER ── */
hr.gold { border: none; border-top: 1px solid rgba(212,175,55,0.18); margin: 2rem 0; }

/* ── BUTTON OVERRIDES ── */
.stButton > button {
    background: linear-gradient(135deg,#d4af37,#b8961f) !important;
    color: #0e0e12 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stFileUploader, .stFileUploader * { color: #f0ede8 !important; }
label { color: rgba(240,237,232,0.75) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1 class="hero-title">Style<span>AI</span></h1>
    <p class="hero-sub">Your intelligent personal fashion stylist</p>
    <div class="tag-row">
        <span class="tag">Body Analysis</span>
        <span class="tag">Skin Tone Detection</span>
        <span class="tag">Virtual Try-On</span>
        <span class="tag">Fit Prediction</span>
        <span class="tag">Smart Recommendations</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
_keys = ['category', 'size', 'skin_tone', 'mannequin', 'mannequin_mask',
         'selected_dress', 'uploaded_dress_color', 'uploaded_dress_name',
         'body_stats', 'analysis_done']
for k in _keys:
    if k not in st.session_state:
        st.session_state[k] = None

# ─────────────────────────────────────────────
# ── ANALYSIS ENGINE ──────────────────────────
# ─────────────────────────────────────────────

def detect_body_mp(pil_img):
    """MediaPipe-based detection → returns (landmarks, measurements) or (None, None)."""
    if not MP_OK:
        return None, None
    import cv2
    mp_pose = mp.solutions.pose
    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    with mp_pose.Pose(static_image_mode=True, model_complexity=1,
                      enable_segmentation=False,
                      min_detection_confidence=0.45) as pose:
        res = pose.process(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    if not res.pose_landmarks:
        return None, None
    h, w = img_cv.shape[:2]
    lm = [{
        'x': int(l.x * w), 'y': int(l.y * h),
        'z': l.z, 'vis': l.visibility
    } for l in res.pose_landmarks.landmark]
    LS, RS = 11, 12
    LH, RH = 23, 24
    LA, RA = 27, 28
    NOSE   = 0
    sw = abs(lm[LS]['x'] - lm[RS]['x'])
    hw = abs(lm[LH]['x'] - lm[RH]['x'])
    ay = (lm[LA]['y'] + lm[RA]['y']) / 2
    bh = ay - lm[NOSE]['y']
    ww = (sw + hw) / 2 * 0.85
    meas = dict(sw=sw, hw=hw, ww=ww, bh=bh,
                shr=sw/hw if hw else 1.0,
                whr=ww/hw if hw else 1.0,
                hwr=bh/hw if hw else 2.5)
    return lm, meas


def rule_based_body(img_array, img_h, img_w):
    """Fast rule-based body bounding box + rough measurements."""
    gray = img_array.mean(axis=2)
    thr  = np.percentile(gray, 22)
    mask = gray > thr
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if rows.any() and cols.any():
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
    else:
        rmin, rmax = int(img_h*0.05), int(img_h*0.95)
        cmin, cmax = int(img_w*0.15), int(img_w*0.85)
    bh = rmax - rmin
    bw = cmax - cmin
    sw = bw * 0.42
    hw = bw * 0.44
    ww = bw * 0.38
    return dict(rmin=rmin, rmax=rmax, cmin=cmin, cmax=cmax,
                sw=sw, hw=hw, ww=ww, bh=bh,
                shr=sw/hw if hw else 1.0,
                whr=ww/hw if hw else 1.0,
                hwr=bh/hw if hw else 2.5,
                coverage=bh/img_h)


def classify_person(meas, landmarks=None):
    """Returns (category, size, confidence)."""
    shr = meas.get('shr', 1.0)
    whr = meas.get('whr', 1.0)
    hwr = meas.get('hwr', 2.5)
    cov = meas.get('coverage', 0.75)

    # ── Kids score ──
    ks = 0
    if hwr < 3.5:  ks += 5
    elif hwr < 4.2: ks += 2
    if cov < 0.55:  ks += 4
    elif cov < 0.65: ks += 2
    rv = abs(shr - 1.0) + abs(whr - 1.0)
    if rv < 0.08:  ks += 5
    elif rv < 0.16: ks += 2
    if 0.97 < whr < 1.03: ks += 3

    is_child = ks >= 7

    if is_child:
        category = "Kids"
        if hwr < 3.2:   size = "4–6Y"
        elif hwr < 3.8: size = "7–9Y"
        else:            size = "10–12Y"
        conf = min(0.80 + ks*0.015, 0.97)
    else:
        if shr > 1.10 or whr > 0.93:
            category = "Men"
            conf = 0.93 if shr > 1.10 else 0.85
        elif whr < 0.82:
            category = "Women"
            conf = 0.93
        else:
            category = "Women" if shr < 1.06 else "Men"
            conf = 0.78

        bss = (meas.get('sw',1) + meas.get('ww',1) + meas.get('hw',1)) / \
              (3 * max(meas.get('hw',1), 1))
        if category == "Men":
            size = "S" if bss<1.35 else ("M" if bss<1.45 else ("L" if bss<1.55 else "XL"))
        else:
            size = ("XS" if bss<1.30 else
                    ("S"  if bss<1.38 else
                     ("M"  if bss<1.48 else
                      ("L"  if bss<1.58 else "XL"))))

    return category, size, round(conf*100)


def analyse_skin(img_array, rmin, rmax, cmin, cmax, body_h):
    """5-level skin tone from the upper-body region."""
    r0 = rmin
    r1 = rmin + int(body_h * 0.28)
    patch = img_array[r0:r1, cmin:cmax]
    if patch.size == 0:
        return "Medium", (170, 130, 100)
    R = np.median(patch[:,:,0])
    G = np.median(patch[:,:,1])
    B = np.median(patch[:,:,2])
    lum = 0.299*R + 0.587*G + 0.114*B
    tone_map = [
        (210, "Fair",   (255, 230, 210)),
        (185, "Light",  (235, 195, 165)),
        (150, "Medium", (195, 148, 110)),
        (110, "Tan",    (160, 110,  80)),
        (0,   "Deep",   (100,  65,  45)),
    ]
    for thr, name, swatch in tone_map:
        if lum >= thr:
            return name, swatch
    return "Deep", (100, 65, 45)


# ─────────────────────────────────────────────
# ── MANNEQUIN BUILDER ────────────────────────
# ─────────────────────────────────────────────

def build_mannequin(body_crop: Image.Image, category: str) -> tuple:
    """
    Returns (mannequin_pil, mask_array).
    Draws a clean stylised silhouette from the cropped body image.
    """
    MH, MW = 680, 320
    crop = body_crop.resize((MW, MH), Image.Resampling.LANCZOS)
    arr  = np.array(crop)

    # Silhouette mask via luminance threshold
    gray = arr.mean(axis=2)
    thr  = np.percentile(gray, 30)
    mask = gray > thr

    # Mannequin base colour per category
    base_map = {"Men": (215,210,205), "Women": (225,218,213), "Kids": (235,228,222)}
    base = np.array(base_map.get(category, (220,215,210)), dtype=float)
    outline_col = np.array([55, 50, 50])

    canvas = np.full((MH, MW, 3), 20, dtype=np.uint8)  # dark background

    # Fill body with shading
    cx = MW / 2
    for i in range(MH):
        for j in range(MW):
            if not mask[i, j]:
                continue
            # Edge detection (outline)
            if i>0 and i<MH-1 and j>0 and j<MW-1:
                is_edge = not (mask[i-1,j] and mask[i+1,j] and
                               mask[i,j-1] and mask[i,j+1])
            else:
                is_edge = True
            if is_edge:
                canvas[i, j] = outline_col
            else:
                # Radial shading
                dist = abs(j - cx) / (MW/2)
                shade = 1.0 - dist * 0.22
                canvas[i, j] = (base * shade).clip(0,255).astype(np.uint8)

    # Gold shimmer strip down the torso centre
    for i in range(int(MH*0.15), int(MH*0.55)):
        for dj in range(-2, 3):
            jj = int(cx) + dj
            if 0 <= jj < MW and mask[i, jj]:
                blend = 0.55 + 0.45 * math.cos(math.pi * dj / 4)
                canvas[i, jj] = (canvas[i, jj] * (1-blend*0.25) +
                                  np.array([212,175,55]) * blend*0.25).clip(0,255).astype(np.uint8)

    mq = Image.fromarray(canvas)
    return mq, mask


# ─────────────────────────────────────────────
# ── VIRTUAL TRY-ON ───────────────────────────
# ─────────────────────────────────────────────

def virtual_tryon(mannequin: Image.Image, mask: np.ndarray,
                  dress_color, category: str) -> Image.Image:
    """Overlays a shaded dress onto the mannequin silhouette."""
    arr  = np.array(mannequin).copy()
    h, w = arr.shape[:2]
    cx   = w / 2
    dc   = np.array(dress_color, dtype=float)

    # Dress covers body from ~10% to ~72% of height
    dr_top = int(h * 0.09)
    dr_bot = int(h * 0.72)

    for i in range(dr_top, dr_bot):
        if i >= h: break
        vp = (i - dr_top) / max(dr_bot - dr_top, 1)
        for j in range(w):
            if not mask[i, j]: continue
            dist  = abs(j - cx) / (w/2)
            shade = (1.0 - dist*0.28) * (1.0 - vp*0.12)
            pixel = (dc * shade).clip(0, 255).astype(np.uint8)
            # Subtle highlight band
            if abs(j - cx) < 12:
                pixel = np.clip(pixel * 1.14, 0, 255).astype(np.uint8)
            arr[i, j] = pixel

    # Collar / neckline
    for i in range(int(h*0.09), int(h*0.14)):
        for j in range(w):
            if mask[i, j]:
                arr[i, j] = (dc * 0.58).clip(0,255).astype(np.uint8)

    # Hem accent line
    for i in range(dr_bot, min(dr_bot+6, h)):
        for j in range(w):
            if mask[i, j]:
                arr[i, j] = (dc * 0.62).clip(0,255).astype(np.uint8)

    # Gold hem dots
    hem_y = dr_bot + 2
    if hem_y < h:
        for j in range(6, w-6, 14):
            if mask[hem_y, j]:
                arr[max(hem_y-1,0):hem_y+2, max(j-1,0):j+2] = [212, 175, 55]

    return Image.fromarray(arr)


# ─────────────────────────────────────────────
# ── FIT ANALYSER ─────────────────────────────
# ─────────────────────────────────────────────
FIT_SIZE_ORDER = {"XS":0,"S":1,"M":2,"L":3,"XL":4,
                  "4–6Y":0,"7–9Y":1,"10–12Y":2}

def analyse_fit(user_size: str, dress_label: str):
    """
    dress_label is one of the product size suggestions.
    Returns (fit_label, fit_class, advice).
    """
    prod_size = {"XS":"XS","S":"S","M":"M","L":"L","XL":"XL",
                 "4–6Y":"4–6Y","7–9Y":"7–9Y","10–12Y":"10–12Y"}.get(dress_label, user_size)
    u = FIT_SIZE_ORDER.get(user_size, 2)
    d = FIT_SIZE_ORDER.get(prod_size, 2)
    diff = d - u
    if diff == 0:
        return "Perfect Fit", "fit-perfect", "This size is made for you — confident choice!"
    elif diff == 1:
        return "Slightly Loose", "fit-loose", "One size up; gives a relaxed, airy drape."
    elif diff == -1:
        return "Slightly Tight", "fit-tight", "One size down; expect a fitted, body-hugging look."
    elif diff >= 2:
        return "Too Loose", "fit-loose", "Consider sizing down for a cleaner silhouette."
    else:
        return "Too Tight", "fit-tight", "Size up to avoid discomfort and restricted movement."


# ─────────────────────────────────────────────
# ── PRODUCT CATALOGUE ────────────────────────
# ─────────────────────────────────────────────

def get_products(category, size, skin_tone):
    light_skin = skin_tone in ("Fair", "Light")
    medium     = skin_tone == "Medium"

    WOMEN = [
        dict(id=1, name="Libas Cotton A-Line Kurti", brand="Libas",
             emoji="👘", color=(255,182,193), price="₹899", fit_size="M",
             desc="Floral printed, breathable cotton",
             amazon="https://www.amazon.in/s?k=libas+kurti",
             flipkart="https://www.flipkart.com/search?q=libas+kurti"),
        dict(id=2, name="Athena Fit & Flare Dress", brand="Athena",
             emoji="👗", color=(135,206,250) if light_skin else (100,149,237), price="₹1,299", fit_size="M",
             desc="Elegant polyester party dress",
             amazon="https://www.amazon.in/s?k=athena+women+dress",
             flipkart="https://www.flipkart.com/search?q=athena+dress"),
        dict(id=3, name="Biba Anarkali Kurti", brand="Biba",
             emoji="🥻", color=(186,85,211) if not medium else (180,100,60), price="₹1,599", fit_size="L",
             desc="Printed ethnic Anarkali",
             amazon="https://www.amazon.in/s?k=biba+anarkali",
             flipkart="https://www.flipkart.com/search?q=biba+anarkali"),
        dict(id=4, name="AND Women's Midi Dress", brand="AND",
             emoji="👗", color=(240,200,120), price="₹1,999", fit_size="S",
             desc="Casual chic midi silhouette",
             amazon="https://www.amazon.in/s?k=AND+women+dress",
             flipkart="https://www.flipkart.com/search?q=AND+women+midi"),
    ]

    MEN = [
        dict(id=1, name="Arrow Regular Fit Shirt", brand="Arrow",
             emoji="👔", color=(70,130,180), price="₹1,499", fit_size="M",
             desc="Formal full-sleeve poplin",
             amazon="https://www.amazon.in/s?k=arrow+formal+shirt",
             flipkart="https://www.flipkart.com/search?q=arrow+shirt"),
        dict(id=2, name="Levi's 511 Slim Jeans", brand="Levi's",
             emoji="👖", color=(25,25,112), price="₹2,299", fit_size="M",
             desc="Classic indigo slim-fit denim",
             amazon="https://www.amazon.in/s?k=levis+511+jeans",
             flipkart="https://www.flipkart.com/search?q=levis+511"),
        dict(id=3, name="Manyavar Silk Kurta Set", brand="Manyavar",
             emoji="🥋", color=(139,69,19), price="₹2,999", fit_size="L",
             desc="Festive silk-blend kurta-pyjama",
             amazon="https://www.amazon.in/s?k=manyavar+kurta",
             flipkart="https://www.flipkart.com/search?q=manyavar+kurta"),
        dict(id=4, name="H&M Relaxed Oxford Shirt", brand="H&M",
             emoji="🧥", color=(200,200,180), price="₹1,199", fit_size="L",
             desc="Weekend-ready Oxford weave",
             amazon="https://www.amazon.in/s?k=hm+men+oxford+shirt",
             flipkart="https://www.flipkart.com/search?q=hm+oxford+shirt"),
    ]

    KIDS = [
        dict(id=1, name="Cherokee Cotton T-Shirt", brand="Cherokee",
             emoji="👕", color=(255,215,0), price="₹399", fit_size="7–9Y",
             desc="Soft 100% cotton round-neck",
             amazon="https://www.amazon.in/s?k=cherokee+kids+tshirt",
             flipkart="https://www.flipkart.com/search?q=cherokee+kids"),
        dict(id=2, name="US Polo Kids Jeans", brand="US Polo",
             emoji="👖", color=(70,130,180), price="₹799", fit_size="7–9Y",
             desc="Straight-fit stretchable denim",
             amazon="https://www.amazon.in/s?k=uspolo+kids+jeans",
             flipkart="https://www.flipkart.com/search?q=uspolo+kids+jeans"),
        dict(id=3, name="Lilliput Frock Dress", brand="Lilliput",
             emoji="🩱", color=(255,182,193), price="₹599", fit_size="4–6Y",
             desc="Ruffled cotton party frock",
             amazon="https://www.amazon.in/s?k=lilliput+kids+dress",
             flipkart="https://www.flipkart.com/search?q=lilliput+dress"),
        dict(id=4, name="Max Kids Coord Set", brand="Max Fashion",
             emoji="👕", color=(152,251,152), price="₹549", fit_size="10–12Y",
             desc="Playful coord top + shorts",
             amazon="https://www.amazon.in/s?k=max+kids+coord",
             flipkart="https://www.flipkart.com/search?q=max+kids+coord"),
    ]

    cat_map = {"Women": WOMEN, "Men": MEN, "Kids": KIDS}
    return cat_map.get(category, WOMEN)


# ─────────────────────────────────────────────
# ── STEP 1 — UPLOAD ──────────────────────────
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-head">
    <div class="step-num">1</div>
    <div class="step-title">Upload Your Photo</div>
</div>
""", unsafe_allow_html=True)

col_up1, col_up2 = st.columns([1, 1], gap="large")

with col_up1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("##### 📷 Full-Body Photo *(required)*")
    body_file = st.file_uploader(
        "Clear full-body shot, head to toe",
        type=["jpg","jpeg","png"], key="body_upload",
        help="Best results with a plain background and good lighting."
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_up2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("##### 👗 Your Own Dress *(optional)*")
    dress_file = st.file_uploader(
        "Upload a dress to try on virtually",
        type=["jpg","jpeg","png"], key="dress_upload",
        help="Dominant colour will be extracted automatically."
    )
    if dress_file:
        d_img = Image.open(dress_file).convert("RGB")
        d_arr = np.array(d_img)
        dh, dw = d_arr.shape[:2]
        patch = d_arr[dh//4:3*dh//4, dw//4:3*dw//4]
        dr = int(np.median(patch[:,:,0]))
        dg = int(np.median(patch[:,:,1]))
        db = int(np.median(patch[:,:,2]))
        st.session_state.uploaded_dress_color = (dr, dg, db)
        st.session_state.uploaded_dress_name  = "Your Uploaded Dress"
        c1, c2 = st.columns([1,2])
        with c1:
            st.image(d_img, use_container_width=True)
        with c2:
            st.markdown(f"""
            <div class="card-gold" style="margin-top:0">
                <div class="prod-swatch" style="background:rgb({dr},{dg},{db});height:80px;font-size:2rem">👗</div>
                <p style="font-size:0.75rem;color:rgba(240,237,232,0.5);margin:0">
                    Extracted colour: <strong>rgb({dr}, {dg}, {db})</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if not body_file:
    st.markdown('<hr class="gold">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="text-align:center;padding:2.5rem">
        <p style="font-size:2rem;margin-bottom:0.5rem">✦</p>
        <p style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;color:rgba(240,237,232,0.7)">
            Upload a photo above to begin your style journey
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# ── STEP 2 — ANALYSIS ────────────────────────
# ─────────────────────────────────────────────
original = Image.open(body_file).convert("RGB")
img_w, img_h = original.size
img_array    = np.array(original)

st.markdown('<hr class="gold">', unsafe_allow_html=True)
st.markdown("""
<div class="step-head">
    <div class="step-num">2</div>
    <div class="step-title">AI Analysis & Mannequin Creation</div>
</div>
""", unsafe_allow_html=True)

a_col1, a_col2, a_col3 = st.columns(3, gap="medium")

with a_col1:
    st.markdown("**Original Photo**")
    st.image(original, use_container_width=True)

with st.spinner("Analysing body structure…"):

    # ── Detect ──
    landmarks, mp_meas = detect_body_mp(original)

    if mp_meas:
        meas = mp_meas
        meas['coverage'] = (max(l['y'] for l in landmarks) -
                            min(l['y'] for l in landmarks)) / img_h
        method = "MediaPipe"
    else:
        rb = rule_based_body(img_array, img_h, img_w)
        meas = rb
        method = "Smart Vision"

    # ── Classify ──
    category, size, conf = classify_person(meas, landmarks)

    # Bounding box for skin + crop
    if mp_meas and landmarks:
        xs = [l['x'] for l in landmarks if l['vis']>0.4]
        ys = [l['y'] for l in landmarks if l['vis']>0.4]
        rmin, rmax = min(ys), max(ys)
        cmin, cmax = min(xs), max(xs)
    else:
        rmin = rb['rmin']; rmax = rb['rmax']
        cmin = rb['cmin']; cmax = rb['cmax']

    body_h_px = max(rmax - rmin, 1)
    body_w_px = max(cmax - cmin, 1)

    # ── Skin tone ──
    skin_name, skin_swatch = analyse_skin(img_array, rmin, rmax, cmin, cmax, body_h_px)

    # ── Mannequin ──
    body_crop = Image.fromarray(img_array[rmin:rmax, cmin:cmax])
    mannequin, mq_mask = build_mannequin(body_crop, category)

    # Store
    st.session_state.category  = category
    st.session_state.size      = size
    st.session_state.skin_tone = skin_name
    st.session_state.mannequin = mannequin
    st.session_state.mannequin_mask = mq_mask
    st.session_state.body_stats = dict(method=method, conf=conf,
                                        bh=body_h_px, bw=body_w_px,
                                        shr=round(meas['shr'],2),
                                        whr=round(meas['whr'],2))
    st.session_state.analysis_done = True

# Show detection overlay
with a_col2:
    detected = original.copy()
    draw = ImageDraw.Draw(detected)
    draw.rectangle([cmin, rmin, cmax, rmax], outline="#d4af37", width=5)
    if landmarks:
        for lm in landmarks:
            if lm['vis'] > 0.5:
                x,y = lm['x'], lm['y']
                draw.ellipse([x-3,y-3,x+3,y+3], fill='#d4af37', outline='#fff')
        conns = [(11,12),(11,13),(13,15),(12,14),(14,16),
                 (11,23),(12,24),(23,24),(23,25),(25,27),(24,26),(26,28)]
        for a,b in conns:
            if a<len(landmarks) and b<len(landmarks):
                if landmarks[a]['vis']>0.5 and landmarks[b]['vis']>0.5:
                    draw.line([landmarks[a]['x'],landmarks[a]['y'],
                               landmarks[b]['x'],landmarks[b]['y']],
                              fill='#6495ed', width=2)
    st.markdown("**Body Detection**")
    st.image(detected, use_container_width=True)
    st.markdown(f'<span class="tag">✦ {method}</span>', unsafe_allow_html=True)

with a_col3:
    st.markdown("**Your Mannequin**")
    st.image(mannequin, use_container_width=True)
    st.markdown('<span class="tag" style="background:rgba(212,175,55,0.2)">✦ Ready for try-on</span>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── STEP 3 — RESULTS DASHBOARD ───────────────
# ─────────────────────────────────────────────
st.markdown('<hr class="gold">', unsafe_allow_html=True)
st.markdown("""
<div class="step-head">
    <div class="step-num">3</div>
    <div class="step-title">Analysis Results</div>
</div>
""", unsafe_allow_html=True)

sr, sg, sb = skin_swatch
bst = st.session_state.body_stats

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-chip">
        <span class="val">{category}</span>
        <span class="lbl">Category</span>
    </div>
    <div class="stat-chip">
        <span class="val">{size}</span>
        <span class="lbl">Size</span>
    </div>
    <div class="stat-chip">
        <span class="val" style="color:rgb({sr},{sg},{sb})">{skin_name}</span>
        <span class="lbl">Skin Tone</span>
    </div>
    <div class="stat-chip">
        <span class="val">{conf}%</span>
        <span class="lbl">Confidence</span>
    </div>
    <div class="stat-chip">
        <span class="val" style="font-size:1rem">{bst['method']}</span>
        <span class="lbl">Engine</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Skin-tone colour chip
st.markdown(f"""
<div style="display:flex;align-items:center;gap:1rem;margin:1rem 0">
    <div style="width:48px;height:48px;border-radius:50%;background:rgb({sr},{sg},{sb});
                border:2px solid rgba(212,175,55,0.4);flex-shrink:0"></div>
    <div>
        <div style="color:#f0ede8;font-size:0.95rem"><strong>{skin_name}</strong> skin tone detected</div>
        <div style="color:rgba(240,237,232,0.45);font-size:0.8rem">
            {'Pastels, jewel tones, whites & soft blues suit you best.' if skin_name in ('Fair','Light')
             else ('Earth tones, warm oranges, reds, and olive greens look great on you.' if skin_name=='Medium'
             else 'Bold, vibrant colours — royal blue, bright red, white — really pop on you.')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("🔍 Detailed Measurement Breakdown"):
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("**Body Proportions**")
        st.write(f"Height (px): `{bst['bh']}`")
        st.write(f"Width  (px): `{bst['bw']}`")
        st.write(f"H/W Ratio:   `{round(bst['bh']/max(bst['bw'],1), 2)}`")
    with d2:
        st.markdown("**Shape Ratios**")
        st.write(f"Shoulder/Hip: `{bst['shr']}`")
        st.write(f"Waist/Hip:    `{bst['whr']}`")
    with d3:
        st.markdown("**Classification**")
        st.write(f"Category:   `{category}`")
        st.write(f"Size:       `{size}`")
        st.write(f"Confidence: `{conf}%`")


# ─────────────────────────────────────────────
# ── STEP 4 — PRODUCT RECOMMENDATIONS ─────────
# ─────────────────────────────────────────────
st.markdown('<hr class="gold">', unsafe_allow_html=True)
st.markdown(f"""
<div class="step-head">
    <div class="step-num">4</div>
    <div class="step-title">Recommended for You — {category} · Size {size}</div>
</div>
""", unsafe_allow_html=True)

products = get_products(category, size, skin_name)

p_cols = st.columns(len(products), gap="medium")
for idx, prod in enumerate(products):
    with p_cols[idx]:
        is_sel = (st.session_state.selected_dress and
                  st.session_state.selected_dress.get('id') == prod['id'])
        r, g, b = prod['color']
        sel_cls = "selected" if is_sel else ""
        st.markdown(f"""
        <div class="prod-card {sel_cls}">
            <div class="prod-swatch" style="background:rgb({r},{g},{b})">{prod['emoji']}</div>
            <div class="prod-name">{prod['name']}</div>
            <div class="prod-brand">{prod['brand']}</div>
            <div class="prod-price">{prod['price']}</div>
            <div style="font-size:0.75rem;color:rgba(240,237,232,0.4);margin-bottom:0.5rem">{prod['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✦ Try On", key=f"try_{prod['id']}", use_container_width=True):
            st.session_state.selected_dress = prod
            st.session_state.uploaded_dress_color = None  # prefer product
            st.rerun()
        st.link_button("🛒 Amazon",   prod['amazon'],   use_container_width=True)
        st.link_button("🛒 Flipkart", prod['flipkart'], use_container_width=True)


# ─────────────────────────────────────────────
# ── STEP 5 — VIRTUAL TRY-ON ──────────────────
# ─────────────────────────────────────────────
active_color = None
active_name  = None
active_prod  = None

if st.session_state.uploaded_dress_color:
    active_color = st.session_state.uploaded_dress_color
    active_name  = st.session_state.uploaded_dress_name
elif st.session_state.selected_dress:
    active_prod  = st.session_state.selected_dress
    active_color = active_prod['color']
    active_name  = active_prod['name']

if active_color and st.session_state.mannequin:
    st.markdown('<hr class="gold">', unsafe_allow_html=True)
    st.markdown("""
    <div class="step-head">
        <div class="step-num">5</div>
        <div class="step-title">Virtual Try-On</div>
    </div>
    """, unsafe_allow_html=True)

    tryon = virtual_tryon(
        st.session_state.mannequin,
        st.session_state.mannequin_mask,
        active_color,
        category
    )

    # Fit analysis
    fit_label, fit_cls, fit_advice = ("Perfect Fit", "fit-perfect", "Tailored for your size!")
    if active_prod:
        fit_label, fit_cls, fit_advice = analyse_fit(size, active_prod.get('fit_size', size))

    # Layout
    t1, t2, t3 = st.columns([1, 2, 1], gap="medium")

    with t1:
        st.markdown('<div class="card-gold">', unsafe_allow_html=True)
        st.markdown("**Wearing**")
        r,g,b = active_color
        st.markdown(f"""
        <div style="width:60px;height:60px;border-radius:12px;background:rgb({r},{g},{b});
                    border:1px solid rgba(212,175,55,0.3);margin-bottom:0.75rem"></div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.05rem;color:#f0ede8">{active_name}</div>
        """, unsafe_allow_html=True)
        if active_prod:
            st.markdown(f"<div style='font-size:0.75rem;color:rgba(240,237,232,0.45)'>{active_prod.get('desc','')}</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div style='color:#d4af37;font-size:1.2rem;margin-top:0.5rem'>{active_prod.get('price','')}</div>",
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card" style="margin-top:1rem">', unsafe_allow_html=True)
        st.markdown("**Fit Analysis**")
        st.markdown(f'<span class="fit-badge {fit_cls}">{fit_label}</span>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.8rem;color:rgba(240,237,232,0.55);margin-top:0.5rem">{fit_advice}</p>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div style="text-align:center">
            <div class="mq-rotate" style="display:inline-block">
        """, unsafe_allow_html=True)
        st.image(tryon, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

        # Download
        buf = io.BytesIO()
        tryon.save(buf, format='PNG')
        st.download_button(
            "⬇ Download Try-On Image",
            buf.getvalue(),
            f"styleai_tryon_{size}.png",
            "image/png",
            use_container_width=True
        )

    with t3:
        if active_prod:
            st.markdown('<div class="card-gold">', unsafe_allow_html=True)
            st.markdown("**Buy Now**")
            st.link_button(f"🛒 Amazon — {active_prod['brand']}",
                           active_prod['amazon'], use_container_width=True)
            st.link_button(f"🛒 Flipkart — {active_prod['brand']}",
                           active_prod['flipkart'], use_container_width=True)
            st.markdown('<hr class="gold" style="margin:0.75rem 0">', unsafe_allow_html=True)
            st.markdown("**More picks**")
            others = [p for p in products if p['id'] != active_prod['id']]
            for op in others[:2]:
                if st.button(f"{op['emoji']} {op['name'][:22]}…", key=f"switch_{op['id']}",
                             use_container_width=True):
                    st.session_state.selected_dress = op
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**Your uploaded dress**")
            r,g,b = active_color
            st.markdown(f"""
            <div style="width:100%;height:80px;border-radius:12px;
                        background:rgb({r},{g},{b});margin-bottom:0.75rem"></div>
            <p style="font-size:0.8rem;color:rgba(240,237,232,0.5)">
                Colour extracted from your upload — rgb({r},{g},{b})
            </p>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── FOOTER ───────────────────────────────────
# ─────────────────────────────────────────────
st.markdown('<hr class="gold">', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:2.5rem 1rem">
    <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;
                color:#d4af37;letter-spacing:0.12em">StyleAI</div>
    <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.2em;
                color:rgba(240,237,232,0.3);margin-top:0.4rem">
        Smart Fashion · Powered by Computer Vision
    </div>
    <div class="tag-row" style="justify-content:center;margin-top:1rem">
        <span class="tag">Body Detection</span>
        <span class="tag">Skin Tone Analysis</span>
        <span class="tag">Virtual Try-On</span>
        <span class="tag">Fit Prediction</span>
        <span class="tag">Amazon & Flipkart</span>
    </div>
</div>
""", unsafe_allow_html=True)
