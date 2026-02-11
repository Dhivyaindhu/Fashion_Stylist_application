import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import math

st.set_page_config(page_title="3D Fashion Stylist Pro", page_icon="👗", layout="wide")

# ══════════════════════════════════════════════════════════════
#  CSS  — luxury editorial dark theme
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:      #0a0a0f;
  --surface: #12121a;
  --card:    #1a1a26;
  --border:  #2a2a40;
  --accent:  #c9a96e;
  --accent2: #e8c99a;
  --text:    #f0ede8;
  --muted:   #888;
  --success: #4caf83;
  --info:    #5b9bd5;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 3rem !important; max-width: 1400px !important; }

/* ── hero ── */
.hero {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a1230 50%, #0d0d1a 100%);
  border: 1px solid #2a2050;
  border-radius: 20px;
  padding: 3.5rem 2rem;
  text-align: center;
  margin: 1.5rem 0 2rem;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(201,169,110,.12) 0%, transparent 70%);
}
.hero h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.2rem; font-weight: 300; letter-spacing: .04em;
  color: var(--accent2); margin-bottom: .5rem;
}
.hero p { font-size: 1rem; color: var(--muted); letter-spacing: .12em; text-transform: uppercase; }

/* ── section headers ── */
.sec-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.8rem; font-weight: 400;
  color: var(--accent2);
  border-bottom: 1px solid var(--border);
  padding-bottom: .5rem; margin: 2rem 0 1.25rem;
  letter-spacing: .03em;
}

/* ── cards ── */
.glass-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.25rem;
}

/* ── measurement pills ── */
.measure-grid {
  display: flex; flex-wrap: wrap; gap: .75rem; margin: 1rem 0;
}
.measure-pill {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .6rem 1rem;
  text-align: center; min-width: 110px;
}
.measure-pill .label { font-size: .68rem; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); }
.measure-pill .val { font-size: 1.2rem; font-weight: 600; color: var(--accent2); }

/* ── body type badge ── */
.body-type-badge {
  display: inline-block;
  background: linear-gradient(135deg, #c9a96e22, #e8c99a22);
  border: 1.5px solid var(--accent);
  color: var(--accent2);
  border-radius: 99px;
  padding: .4rem 1.2rem;
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem; letter-spacing: .08em;
}

/* ── skin tone dot ── */
.skin-row { display: flex; align-items: center; gap: .75rem; margin: .5rem 0; }
.skin-dot {
  width: 28px; height: 28px; border-radius: 50%;
  border: 2px solid var(--border); flex-shrink: 0;
}

/* ── product cards ── */
.product-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  transition: border-color .25s, transform .25s;
}
.product-card:hover { border-color: var(--accent); transform: translateY(-4px); }
.product-badge {
  display: inline-block;
  font-size: .65rem; font-weight: 600; text-transform: uppercase; letter-spacing: .1em;
  padding: .2rem .6rem; border-radius: 4px; margin-bottom: .4rem;
}
.badge-amazon  { background: #ff9900; color: #000; }
.badge-flipkart{ background: #2874f0; color: #fff; }
.badge-jiomart { background: #ef4444; color: #fff; }
.badge-meesho  { background: #9c27b0; color: #fff; }

/* ── mannequin stage ── */
.mannequin-stage {
  background: linear-gradient(160deg, #0f0f1e, #1a1530);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.5rem;
  text-align: center;
  min-height: 460px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}

/* ── color swatches ── */
.swatch-row { display: flex; flex-wrap: wrap; gap: .5rem; margin: .6rem 0; }
.swatch {
  width: 36px; height: 36px; border-radius: 8px;
  border: 2px solid var(--border);
  display: inline-block; cursor: default;
  transition: transform .2s;
}
.swatch:hover { transform: scale(1.15); border-color: var(--accent); }

/* ── buttons ── */
.stButton>button {
  background: linear-gradient(135deg, #c9a96e, #a07840) !important;
  color: #0a0a0f !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: .65rem 1.2rem !important;
  letter-spacing: .04em !important;
}
.stButton>button:hover { opacity: .88 !important; }

/* ── category buttons ── */
.cat-btn button {
  background: var(--card) !important;
  color: var(--text) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--muted) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--accent2) !important;
  border-bottom-color: var(--accent) !important;
}

/* ── divider ── */
hr { border-color: var(--border) !important; }

/* ── info boxes ── */
.info-box {
  background: rgba(91,155,213,.08);
  border: 1px solid rgba(91,155,213,.25);
  border-radius: 10px;
  padding: .85rem 1rem;
  font-size: .88rem;
  color: #a8c8e8;
  margin: .75rem 0;
}

.tip-box {
  background: rgba(201,169,110,.08);
  border: 1px solid rgba(201,169,110,.25);
  border-radius: 10px;
  padding: .85rem 1rem;
  font-size: .88rem;
  color: var(--accent2);
  margin: .75rem 0;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DATA  — products, colors, body type logic
# ══════════════════════════════════════════════════════════════

COLOR_HEX = {
    "Ivory White":    "#FFFFF0",
    "Pastel Pink":    "#FFD1DC",
    "Lavender":       "#E6D0FF",
    "Mint Green":     "#AAFFDD",
    "Sky Blue":       "#87CEEB",
    "Soft Peach":     "#FFDAB9",
    "Butter Yellow":  "#FFFACD",
    "Blush Rose":     "#FFB6C1",
    "Warm Coral":     "#FF7F50",
    "Terracotta":     "#E07050",
    "Dusty Mauve":    "#C09090",
    "Warm Caramel":   "#C68642",
    "Olive Green":    "#708238",
    "Burnt Orange":   "#CC5500",
    "Teal":           "#008080",
    "Royal Blue":     "#4169E1",
    "Emerald":        "#50C878",
    "Mustard":        "#FFDB58",
    "Deep Burgundy":  "#800020",
    "Navy":           "#001F5B",
    "Pure White":     "#FFFFFF",
    "Bright Gold":    "#FFD700",
    "Cobalt":         "#0047AB",
    "Fuchsia":        "#FF00FF",
    "Electric Teal":  "#00CED1",
    "Crimson":        "#DC143C",
    "Jade":           "#00A86B",
    "Caramel":        "#C68642",
    "Deep Plum":      "#5B2C6F",
    "Rust":           "#B7410E",
}

SKIN_PALETTE = {
    "Fair": {
        "best":     ["Pastel Pink", "Lavender", "Mint Green", "Sky Blue", "Ivory White", "Blush Rose", "Butter Yellow"],
        "avoid":    ["Pure White", "Pale Yellow"],
        "neutral":  ["Soft Peach", "Warm Coral"],
    },
    "Light": {
        "best":     ["Soft Peach", "Dusty Mauve", "Warm Coral", "Blush Rose", "Terracotta", "Sky Blue", "Lavender"],
        "avoid":    ["Very light pastels"],
        "neutral":  ["Ivory White", "Mint Green"],
    },
    "Medium": {
        "best":     ["Royal Blue", "Emerald", "Mustard", "Teal", "Burnt Orange", "Warm Caramel", "Olive Green"],
        "avoid":    ["Washed-out pastels"],
        "neutral":  ["Deep Burgundy", "Terracotta"],
    },
    "Tan": {
        "best":     ["Cobalt", "Deep Burgundy", "Fuchsia", "Electric Teal", "Navy", "Crimson", "Jade"],
        "avoid":    ["Brown tones"],
        "neutral":  ["Mustard", "Emerald"],
    },
    "Deep": {
        "best":     ["Pure White", "Bright Gold", "Cobalt", "Fuchsia", "Electric Teal", "Crimson", "Jade"],
        "avoid":    ["Dark brown"],
        "neutral":  ["Caramel", "Deep Plum", "Rust"],
    },
}

BODY_TYPE_DATA = {
    # Women
    "Hourglass":         {"icon": "⌛", "desc": "Balanced shoulders & hips, defined waist", "tips": ["Wrap dresses", "Belted styles", "Fit & flare", "Bodycon dresses"]},
    "Pear":              {"icon": "🍐", "desc": "Hips wider than shoulders", "tips": ["A-line skirts", "Empire waist", "Boat neck tops", "Dark bottoms"]},
    "Apple":             {"icon": "🍎", "desc": "Fuller midsection, narrower hips", "tips": ["Empire waist", "V-necklines", "Flowy tops", "Straight-leg trousers"]},
    "Inverted Triangle": {"icon": "🔻", "desc": "Broader shoulders, narrower hips", "tips": ["A-line skirts", "Wide-leg trousers", "Peplum tops", "Full skirts"]},
    "Rectangle":         {"icon": "▭",  "desc": "Shoulders, waist & hips similar width", "tips": ["Peplum styles", "Ruffles", "Wrap dresses", "Belted outfits"]},
    "Full Hourglass":    {"icon": "💎", "desc": "Curvaceous with balanced proportions", "tips": ["Structured dresses", "Wrap styles", "High-waist trousers", "V-necks"]},
    "Petite":            {"icon": "🌸", "desc": "Smaller overall frame", "tips": ["Monochromatic looks", "Vertical stripes", "Mini lengths", "Fitted styles"]},
    # Men
    "Column":            {"icon": "🏛", "desc": "Uniform width top to bottom", "tips": ["Layered looks", "Horizontal stripes", "Textured fabrics", "Slim trousers"]},
    "Trapezium":         {"icon": "🔷", "desc": "Broader shoulders tapering to hips", "tips": ["Slim chinos", "Fitted shirts", "Straight-leg jeans"]},
    "Circle":            {"icon": "⭕", "desc": "Rounder midsection", "tips": ["Vertical stripes", "Dark solids", "Longer shirts/jackets", "Straight trousers"]},
    "Oval":              {"icon": "🥚", "desc": "Wider mid-section, narrower extremities", "tips": ["V-necklines", "Structured blazers", "Dark tones"]},
    "Square":            {"icon": "⬛", "desc": "Equal shoulder & hip width, fuller waist", "tips": ["Vertical details", "Open collars", "Slim-fit styles"]},
    "Triangle":          {"icon": "🔺", "desc": "Wider hips than shoulders", "tips": ["Blazers", "Shoulder structure", "Dark-bottom light-top"]},
    # Kids
    "Petite (Kids)":     {"icon": "🌟", "desc": "Smaller frame for age", "tips": ["Bright colours", "Fun patterns", "Comfortable fits"]},
    "Tall (Kids)":       {"icon": "🌈", "desc": "Taller for age", "tips": ["Age-appropriate lengths", "Adjustable waistbands"]},
}

PRODUCTS = [
    # ── WOMEN ──────────────────────────────────────────────────────────
    {"title": "A-Line Ethnic Kurta", "category": "Women", "colors": ["Pastel Pink", "Lavender", "Mint Green"],
     "sizes": ["XS","S","M","L","XL"], "platform": "Amazon",
     "link": "https://www.amazon.in/s?k=women+a-line+kurta&tag=fashion-stylist",
     "body_types": ["Pear", "Rectangle", "Petite"]},
    {"title": "Wrap Maxi Dress", "category": "Women", "colors": ["Royal Blue", "Emerald", "Warm Coral"],
     "sizes": ["S","M","L","XL"], "platform": "Flipkart",
     "link": "https://www.flipkart.com/search?q=wrap+maxi+dress+women",
     "body_types": ["Hourglass", "Full Hourglass", "Apple"]},
    {"title": "Peplum Ethnic Set", "category": "Women", "colors": ["Mustard", "Burnt Orange", "Teal"],
     "sizes": ["S","M","L"], "platform": "Meesho",
     "link": "https://www.meesho.com/s?q=peplum+ethnic+set+women",
     "body_types": ["Inverted Triangle", "Rectangle"]},
    {"title": "Anarkali Salwar Suit", "category": "Women", "colors": ["Deep Burgundy", "Cobalt", "Emerald"],
     "sizes": ["S","M","L","XL","XXL"], "platform": "JioMart",
     "link": "https://www.jiomart.com/search/women+anarkali+salwar+suit",
     "body_types": ["Apple", "Pear", "Full Hourglass"]},
    {"title": "Fit & Flare Dress", "category": "Women", "colors": ["Blush Rose", "Sky Blue", "Mint Green"],
     "sizes": ["XS","S","M","L"], "platform": "Amazon",
     "link": "https://www.amazon.in/s?k=women+fit+flare+dress",
     "body_types": ["Hourglass", "Pear", "Rectangle"]},
    {"title": "Bodycon Party Dress", "category": "Women", "colors": ["Pure White", "Crimson", "Cobalt"],
     "sizes": ["XS","S","M","L"], "platform": "Meesho",
     "link": "https://www.meesho.com/s?q=bodycon+dress+women",
     "body_types": ["Hourglass", "Full Hourglass"]},
    {"title": "Empire Waist Dress", "category": "Women", "colors": ["Lavender", "Soft Peach", "Ivory White"],
     "sizes": ["S","M","L","XL"], "platform": "Flipkart",
     "link": "https://www.flipkart.com/search?q=empire+waist+dress+women",
     "body_types": ["Apple", "Pear", "Petite"]},
    {"title": "Palazzo Suit Set", "category": "Women", "colors": ["Electric Teal", "Fuchsia", "Bright Gold"],
     "sizes": ["S","M","L","XL","XXL"], "platform": "JioMart",
     "link": "https://www.jiomart.com/search/women+palazzo+suit",
     "body_types": ["Inverted Triangle", "Pear"]},

    # ── MEN ───────────────────────────────────────────────────────────
    {"title": "Slim Fit Formal Shirt", "category": "Men", "colors": ["Royal Blue", "Ivory White", "Cobalt"],
     "sizes": ["S","M","L","XL","XXL"], "platform": "Amazon",
     "link": "https://www.amazon.in/s?k=men+slim+fit+formal+shirt",
     "body_types": ["Column", "Trapezium"]},
    {"title": "Structured Blazer", "category": "Men", "colors": ["Navy", "Deep Burgundy", "Olive Green"],
     "sizes": ["S","M","L","XL"], "platform": "Flipkart",
     "link": "https://www.flipkart.com/search?q=men+structured+blazer",
     "body_types": ["Triangle", "Circle", "Oval"]},
    {"title": "Vertical Stripe Kurta", "category": "Men", "colors": ["Teal", "Mustard", "Terracotta"],
     "sizes": ["S","M","L","XL","XXL"], "platform": "Meesho",
     "link": "https://www.meesho.com/s?q=men+kurta+vertical+stripe",
     "body_types": ["Circle", "Oval", "Square"]},
    {"title": "Chino Slim Trousers", "category": "Men", "colors": ["Warm Caramel", "Olive Green", "Navy"],
     "sizes": ["28","30","32","34","36"], "platform": "JioMart",
     "link": "https://www.jiomart.com/search/men+slim+chino+trousers",
     "body_types": ["Trapezium", "Column", "Square"]},
    {"title": "Casual Linen Shirt", "category": "Men", "colors": ["Sky Blue", "Mint Green", "Ivory White"],
     "sizes": ["S","M","L","XL"], "platform": "Amazon",
     "link": "https://www.amazon.in/s?k=men+linen+casual+shirt",
     "body_types": ["Column", "Trapezium", "Rectangle"]},
    {"title": "Embroidered Kurta", "category": "Men", "colors": ["Deep Plum", "Rust", "Caramel"],
     "sizes": ["S","M","L","XL","XXL"], "platform": "Meesho",
     "link": "https://www.meesho.com/s?q=men+embroidered+kurta",
     "body_types": ["Oval", "Circle", "Square"]},

    # ── KIDS ──────────────────────────────────────────────────────────
    {"title": "Colourful Cotton Frock", "category": "Kids", "colors": ["Pastel Pink", "Mint Green", "Butter Yellow"],
     "sizes": ["2-4Y","4-6Y","6-8Y","8-10Y"], "platform": "Amazon",
     "link": "https://www.amazon.in/s?k=kids+cotton+frock",
     "body_types": ["Petite (Kids)", "Tall (Kids)"]},
    {"title": "Kids Ethnic Kurta Set", "category": "Kids", "colors": ["Royal Blue", "Crimson", "Emerald"],
     "sizes": ["2-4Y","4-6Y","6-8Y","8-10Y","10-12Y"], "platform": "Flipkart",
     "link": "https://www.flipkart.com/search?q=kids+ethnic+kurta+set",
     "body_types": ["Petite (Kids)", "Tall (Kids)"]},
    {"title": "Kids Casual Tracksuit", "category": "Kids", "colors": ["Sky Blue", "Mint Green", "Warm Coral"],
     "sizes": ["4-6Y","6-8Y","8-10Y","10-12Y"], "platform": "JioMart",
     "link": "https://www.jiomart.com/search/kids+tracksuit",
     "body_types": ["Petite (Kids)", "Tall (Kids)"]},
]

PLATFORM_COLORS = {
    "Amazon":  ("badge-amazon",   "Amazon"),
    "Flipkart":("badge-flipkart", "Flipkart"),
    "JioMart": ("badge-jiomart",  "JioMart"),
    "Meesho":  ("badge-meesho",   "Meesho"),
}

# ══════════════════════════════════════════════════════════════
#  MANNEQUIN DRAWING
# ══════════════════════════════════════════════════════════════

def draw_mannequin(shoulder_cm, waist_cm, hip_cm, height_cm, rotation_deg=0,
                   skin_hex="#c8956c", dress_img=None):
    """
    Draw a professional front-facing mannequin proportioned to measurements.
    rotation_deg  → simulates 3-D rotation by squishing width (cos projection).
    dress_img     → PIL Image overlaid on the mannequin torso area.
    """
    W, H = 380, 560
    img  = Image.new("RGBA", (W, H), (18, 18, 28, 255))
    draw = ImageDraw.Draw(img)

    # ── projection factor ─────────────────────────────────────
    rad   = math.radians(rotation_deg % 360)
    squeeze = abs(math.cos(rad))
    if squeeze < 0.05:
        squeeze = 0.05

    cx = W // 2

    # ── scale: map hip_cm → pixels ───────────────────────────
    ref_hip_px = 90
    scale = ref_hip_px / max(hip_cm, 60)

    hip_px = int(hip_cm * scale * squeeze)
    waist_px = int(waist_cm * scale * squeeze)
    shoulder_px = int(shoulder_cm * scale * squeeze)
    height_px = min(int(height_cm * scale * 2.8), H - 60)

    top = (H - height_px) // 2
    bottom = top + height_px

    # proportional regions
    head_h   = int(height_px * 0.13)
    neck_h   = int(height_px * 0.05)
    torso_h  = int(height_px * 0.30)
    waist_h  = int(height_px * 0.04)
    hip_h    = int(height_px * 0.12)
    leg_h    = height_px - head_h - neck_h - torso_h - waist_h - hip_h

    y_head_top   = top
    y_neck_top   = y_head_top  + head_h
    y_torso_top  = y_neck_top  + neck_h
    y_waist_top  = y_torso_top + torso_h
    y_hip_top    = y_waist_top + waist_h
    y_leg_top    = y_hip_top   + hip_h
    y_leg_bot    = y_leg_top   + leg_h

    neck_w = max(int(shoulder_px * 0.22), 8)

    def fill(a):
        return (*tuple(int(c * a) for c in bytes.fromhex(skin_hex.lstrip('#'))), 255)

    body_fill    = fill(1.0)
    shadow_fill  = fill(0.78)
    outline_fill = fill(0.55)
    bg_fill      = (30, 30, 46, 255)

    def ellipse_pts(cx, cy, rw, rh):
        return [cx - rw, cy - rh, cx + rw, cy + rh]

    # ── shadow ────────────────────────────────────────────────
    draw.ellipse([cx - hip_px//2 - 8, y_leg_bot - 10,
                  cx + hip_px//2 + 8, y_leg_bot + 18],
                 fill=(10, 10, 18, 160))

    # ── head ──────────────────────────────────────────────────
    head_rw = int(neck_w * 1.85 * squeeze)
    head_rh = head_h // 2
    head_cy = y_head_top + head_rh
    draw.ellipse(ellipse_pts(cx, head_cy, head_rw, head_rh), fill=body_fill, outline=outline_fill, width=1)

    # ── neck ──────────────────────────────────────────────────
    draw.rectangle([cx - neck_w//2, y_neck_top, cx + neck_w//2, y_torso_top], fill=body_fill)

    # ── torso (trapezoid shoulder→waist) ─────────────────────
    poly = [
        cx - shoulder_px//2, y_torso_top,
        cx + shoulder_px//2, y_torso_top,
        cx + waist_px//2,    y_waist_top,
        cx - waist_px//2,    y_waist_top,
    ]
    draw.polygon(poly, fill=body_fill, outline=outline_fill)

    # ── waist band ────────────────────────────────────────────
    draw.rectangle([cx - waist_px//2, y_waist_top, cx + waist_px//2, y_waist_top + waist_h], fill=shadow_fill)

    # ── hips (trapezoid waist→hip) ────────────────────────────
    poly2 = [
        cx - waist_px//2, y_hip_top,
        cx + waist_px//2, y_hip_top,
        cx + hip_px//2,   y_hip_top + hip_h,
        cx - hip_px//2,   y_hip_top + hip_h,
    ]
    draw.polygon(poly2, fill=body_fill, outline=outline_fill)

    # ── legs ──────────────────────────────────────────────────
    leg_w_top = hip_px // 2 - 2
    leg_w_bot = max(int(leg_w_top * 0.55), 8)
    gap = int(hip_px * 0.06)

    # left leg
    left_leg = [
        cx - gap - leg_w_top, y_leg_top,
        cx - gap,             y_leg_top,
        cx - gap - 4,         y_leg_bot,
        cx - gap - leg_w_bot, y_leg_bot,
    ]
    # right leg
    right_leg = [
        cx + gap,             y_leg_top,
        cx + gap + leg_w_top, y_leg_top,
        cx + gap + leg_w_bot, y_leg_bot,
        cx + gap + 4,         y_leg_bot,
    ]
    draw.polygon(left_leg,  fill=body_fill, outline=outline_fill)
    draw.polygon(right_leg, fill=body_fill, outline=outline_fill)

    # ── arms ──────────────────────────────────────────────────
    arm_w_top = max(int(shoulder_px * 0.14), 6)
    arm_w_bot = max(int(arm_w_top * 0.7), 5)
    arm_len   = int(torso_h * 1.1)

    left_arm = [
        cx - shoulder_px//2 - arm_w_top, y_torso_top,
        cx - shoulder_px//2,             y_torso_top,
        cx - shoulder_px//2 + 8,         y_torso_top + arm_len,
        cx - shoulder_px//2 - arm_w_bot, y_torso_top + arm_len,
    ]
    right_arm = [
        cx + shoulder_px//2,             y_torso_top,
        cx + shoulder_px//2 + arm_w_top, y_torso_top,
        cx + shoulder_px//2 + arm_w_bot, y_torso_top + arm_len,
        cx + shoulder_px//2 - 8,         y_torso_top + arm_len,
    ]
    draw.polygon(left_arm,  fill=shadow_fill, outline=outline_fill)
    draw.polygon(right_arm, fill=shadow_fill, outline=outline_fill)

    # ── dress overlay ─────────────────────────────────────────
    if dress_img:
        try:
            d = dress_img.convert("RGBA").copy()
            dress_w = shoulder_px + int(shoulder_px * 0.35)
            dress_h = int((y_leg_top - y_torso_top) * 1.1)
            dress_w = max(dress_w, 40)
            dress_h = max(dress_h, 60)
            d = d.resize((dress_w, dress_h), Image.LANCZOS)
            # squish for rotation
            if squeeze < 0.98:
                sq_w = max(int(dress_w * squeeze), 10)
                d = d.resize((sq_w, dress_h), Image.LANCZOS)
                dress_w = sq_w
            dx = cx - dress_w // 2
            dy = y_torso_top - int(dress_h * 0.04)
            img.paste(d, (dx, dy), d)
        except Exception:
            pass

    # ── shoulder line detail ──────────────────────────────────
    draw.line([cx - shoulder_px//2, y_torso_top,
               cx + shoulder_px//2, y_torso_top], fill=outline_fill, width=2)

    # ── rotation indicator ────────────────────────────────────
    angle_label = f"{int(rotation_deg % 360)}°"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    draw.text((W - 40, H - 22), angle_label, fill=(180, 160, 120, 200), font=font)

    # ── base stand ────────────────────────────────────────────
    stand_w = int(hip_px * 0.25)
    draw.rectangle([cx - stand_w, y_leg_bot, cx + stand_w, y_leg_bot + 8],
                   fill=(80, 70, 100, 200))

    return img

# ══════════════════════════════════════════════════════════════
#  ANALYSIS HELPERS
# ══════════════════════════════════════════════════════════════

def detect_body_type(shoulder, waist, hip, category):
    s2h = shoulder / max(hip, 1)
    w2h = waist / max(hip, 1)
    s2w = shoulder / max(waist, 1)

    if category == "Women":
        if s2h > 1.05 and w2h < 0.75:
            return "Inverted Triangle"
        elif w2h < 0.75 and s2h < 0.95:
            return "Pear"
        elif w2h > 0.85 and s2h > 0.90:
            return "Apple"
        elif 0.95 <= s2h <= 1.05 and w2h < 0.75:
            if shoulder > 36 or hip > 40:
                return "Full Hourglass"
            return "Hourglass"
        elif 0.90 <= s2h <= 1.10 and w2h >= 0.80:
            return "Rectangle"
        elif shoulder < 34 and hip < 38:
            return "Petite"
        else:
            return "Hourglass"
    elif category == "Men":
        if s2h > 1.10:
            return "Trapezium"
        elif s2h < 0.90 and w2h > 0.88:
            return "Triangle"
        elif w2h > 0.90 and s2h > 0.92:
            return "Circle"
        elif w2h > 0.85:
            return "Oval"
        elif 0.92 <= s2h <= 1.10 and w2h > 0.82:
            return "Square"
        else:
            return "Column"
    else:
        return "Petite (Kids)"

def detect_skin_tone(img_array, rmin, rmax, cmin, cmax, body_h):
    """Sample face/neck area for skin tone."""
    face_region = img_array[rmin:rmin + int(body_h * 0.22), cmin:cmax]
    if face_region.size == 0:
        return "Medium", "#c8956c"
    r = np.mean(face_region[:, :, 0])
    g = np.mean(face_region[:, :, 1])
    b = np.mean(face_region[:, :, 2])
    brightness = (r + g + b) / 3
    warmth = r - b

    if brightness > 210:
        return "Fair",   "#f5d5c8"
    elif brightness > 185:
        return "Light",  "#ebbfa0"
    elif brightness > 155:
        return "Medium", "#c8956c"
    elif brightness > 120:
        return "Tan",    "#a0694a"
    else:
        return "Deep",   "#6b3a2a"

SKIN_DOT_CSS = {
    "Fair":   "#f5d5c8",
    "Light":  "#ebbfa0",
    "Medium": "#c8956c",
    "Tan":    "#a0694a",
    "Deep":   "#6b3a2a",
}

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
defaults = {
    "category": None,
    "measurements": None,
    "body_type": None,
    "skin_tone": None,
    "skin_hex": "#c8956c",
    "size": None,
    "dress_img": None,
    "rotation": 0,
    "analyzed": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>👗 3D Fashion Stylist Pro</h1>
  <p>Body Analysis · Skin Tone · Smart Recommendations · Virtual Try-On</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  STEP 1 — UPLOAD + CATEGORY
# ══════════════════════════════════════════════════════════════
st.markdown('<p class="sec-title">Step 1 — Upload Your Photo & Select Category</p>', unsafe_allow_html=True)

col_up, col_cat = st.columns([1.2, 1])
with col_up:
    uploaded = st.file_uploader("Upload a clear full-body photo", type=["jpg","jpeg","png"])
with col_cat:
    st.markdown("**Select Category**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👶 Kids", use_container_width=True):
            st.session_state.category = "Kids"; st.session_state.analyzed = False
    with c2:
        if st.button("👨 Men", use_container_width=True):
            st.session_state.category = "Men"; st.session_state.analyzed = False
    with c3:
        if st.button("👩 Women", use_container_width=True):
            st.session_state.category = "Women"; st.session_state.analyzed = False

    if st.session_state.category:
        st.markdown(f'<div class="tip-box">✅ Category: <strong>{st.session_state.category}</strong></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">☝️ Please select a category above</div>', unsafe_allow_html=True)

if not uploaded:
    st.markdown('<div class="info-box">📸 Upload a full-body photo to get started</div>', unsafe_allow_html=True)
    st.stop()

if not st.session_state.category:
    st.markdown('<div class="info-box">☝️ Select a category (Kids / Men / Women)</div>', unsafe_allow_html=True)
    st.stop()

category = st.session_state.category
original = Image.open(uploaded).convert("RGB")
img_array = np.array(original)
img_w, img_h = original.size

# ══════════════════════════════════════════════════════════════
#  ANALYSIS
# ══════════════════════════════════════════════════════════════
if not st.session_state.analyzed:
    gray      = np.mean(img_array, axis=2)
    threshold = np.percentile(gray, 25)
    mask      = gray > threshold
    rows      = np.any(mask, axis=1)
    cols      = np.any(mask, axis=0)

    r_idx = np.where(rows)[0]
    c_idx = np.where(cols)[0]
    if len(r_idx) < 2 or len(c_idx) < 2:
        st.error("Could not detect body in image. Please try a clearer full-body photo.")
        st.stop()

    rmin, rmax = r_idx[0], r_idx[-1]
    cmin, cmax = c_idx[0], c_idx[-1]
    body_h = rmax - rmin
    body_w = cmax - cmin

    avg_h = 162 if category == "Women" else (175 if category == "Men" else 120)
    px2cm = avg_h / max(body_h, 1)

    shoulder_cm = round(body_w * 0.42 * px2cm, 1)
    waist_cm    = round(body_w * 0.38 * px2cm, 1)
    hip_cm      = round(body_w * 0.44 * px2cm, 1)
    chest_cm    = round(body_w * 0.43 * px2cm, 1)
    height_cm   = round(body_h * px2cm, 1)
    inseam_cm   = round(height_cm * 0.44, 1)
    thigh_cm    = round(hip_cm * 0.55, 1)

    skin_tone, skin_hex = detect_skin_tone(img_array, rmin, rmax, cmin, cmax, body_h)
    body_type = detect_body_type(shoulder_cm, waist_cm, hip_cm, category)

    # Size
    if category == "Kids":
        size = "2-4Y" if height_cm < 100 else "4-6Y" if height_cm < 115 else "6-8Y" if height_cm < 125 else "8-10Y"
    elif category == "Men":
        if chest_cm < 88:   size = "S"
        elif chest_cm < 96: size = "M"
        elif chest_cm < 104:size = "L"
        elif chest_cm < 112:size = "XL"
        else:               size = "XXL"
    else:
        if bust_like := chest_cm:
            if bust_like < 80:  size = "XS"
            elif bust_like < 88:size = "S"
            elif bust_like < 96:size = "M"
            elif bust_like < 104:size = "L"
            elif bust_like < 112:size = "XL"
            else:               size = "XXL"

    st.session_state.measurements = {
        "height_cm": height_cm, "shoulder_cm": shoulder_cm, "chest_cm": chest_cm,
        "waist_cm": waist_cm, "hip_cm": hip_cm, "inseam_cm": inseam_cm, "thigh_cm": thigh_cm,
    }
    st.session_state.body_type = body_type
    st.session_state.skin_tone = skin_tone
    st.session_state.skin_hex  = skin_hex
    st.session_state.size      = size
    st.session_state.analyzed  = True

m         = st.session_state.measurements
body_type = st.session_state.body_type
skin_tone = st.session_state.skin_tone
skin_hex  = st.session_state.skin_hex
size      = st.session_state.size

# ══════════════════════════════════════════════════════════════
#  STEP 2 — ANALYSIS RESULTS
# ══════════════════════════════════════════════════════════════
st.markdown('<p class="sec-title">Step 2 — Body Analysis Results</p>', unsafe_allow_html=True)

res_col, photo_col = st.columns([1.4, 1])

with res_col:
    # body type
    bt_info = BODY_TYPE_DATA.get(body_type, {"icon": "👤", "desc": "", "tips": []})
    st.markdown(f"""
    <div class="glass-card">
      <div style="margin-bottom:.75rem">
        <span style="font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)">Body Type</span>
      </div>
      <div style="display:flex;align-items:center;gap:1rem;margin-bottom:.6rem">
        <span style="font-size:2.2rem">{bt_info['icon']}</span>
        <span class="body-type-badge">{body_type}</span>
      </div>
      <p style="font-size:.88rem;color:#aaa;margin:0">{bt_info['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    # skin tone
    dot_color = SKIN_DOT_CSS.get(skin_tone, "#c8956c")
    st.markdown(f"""
    <div class="glass-card">
      <div style="margin-bottom:.6rem">
        <span style="font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)">Skin Tone</span>
      </div>
      <div class="skin-row">
        <div class="skin-dot" style="background:{dot_color}"></div>
        <span style="font-weight:600;font-size:1.05rem">{skin_tone}</span>
        <span style="color:#888;font-size:.85rem;margin-left:.5rem">— {dot_color}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # measurements
    st.markdown("""<div class="glass-card">
    <div style="margin-bottom:.6rem">
      <span style="font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)">Measurements</span>
    </div>""", unsafe_allow_html=True)

    measures = [
        ("Height",   f"{m['height_cm']} cm"),
        ("Shoulder", f"{m['shoulder_cm']} cm"),
        ("Chest",    f"{m['chest_cm']} cm"),
        ("Waist",    f"{m['waist_cm']} cm"),
        ("Hip",      f"{m['hip_cm']} cm"),
        ("Inseam",   f"{m['inseam_cm']} cm"),
        ("Thigh",    f"{m['thigh_cm']} cm"),
        ("Size",     size),
    ]
    pills_html = '<div class="measure-grid">'
    for label, val in measures:
        pills_html += f'<div class="measure-pill"><div class="label">{label}</div><div class="val">{val}</div></div>'
    pills_html += '</div>'
    st.markdown(pills_html + '</div>', unsafe_allow_html=True)

with photo_col:
    st.image(original, caption="Uploaded Photo", use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  STEP 3 — COLOUR RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
st.markdown('<p class="sec-title">Step 3 — Colour Recommendations for Your Skin Tone</p>', unsafe_allow_html=True)

palette = SKIN_PALETTE.get(skin_tone, SKIN_PALETTE["Medium"])

col_best, col_neut = st.columns(2)
with col_best:
    st.markdown(f'<div class="glass-card"><strong style="color:var(--success)">✅ Best Colours</strong>', unsafe_allow_html=True)
    swatches = '<div class="swatch-row">'
    for c in palette["best"]:
        hex_c = COLOR_HEX.get(c, "#ccc")
        swatches += f'<div class="swatch" style="background:{hex_c}" title="{c}"></div>'
    swatches += '</div>'
    names = "  •  ".join(palette["best"])
    st.markdown(swatches + f'<p style="font-size:.82rem;color:#aaa;margin-top:.5rem">{names}</p></div>', unsafe_allow_html=True)

with col_neut:
    st.markdown(f'<div class="glass-card"><strong style="color:var(--accent2)">🎨 Neutral / Works Well</strong>', unsafe_allow_html=True)
    swatches2 = '<div class="swatch-row">'
    for c in palette["neutral"]:
        hex_c = COLOR_HEX.get(c, "#ccc")
        swatches2 += f'<div class="swatch" style="background:{hex_c}" title="{c}"></div>'
    swatches2 += '</div>'
    names2 = "  •  ".join(palette["neutral"])
    st.markdown(swatches2 + f'<p style="font-size:.82rem;color:#aaa;margin-top:.5rem">{names2}</p></div>', unsafe_allow_html=True)

# body type style tips
bt_info = BODY_TYPE_DATA.get(body_type, {"tips": []})
if bt_info["tips"]:
    tips_html = "  •  ".join(bt_info["tips"])
    st.markdown(f'<div class="tip-box">👗 <strong>Style Tips for {body_type}:</strong> {tips_html}</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  STEP 4 — PRODUCT RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
st.markdown('<p class="sec-title">Step 4 — Shop Recommendations (Amazon · Flipkart · JioMart · Meesho)</p>',
            unsafe_allow_html=True)

st.markdown(f'<div class="info-box">Showing products for <strong>{category}</strong> · Size <strong>{size}</strong> · Skin tone <strong>{skin_tone}</strong> · Body type <strong>{body_type}</strong></div>',
            unsafe_allow_html=True)

best_colors = set(palette["best"] + palette["neutral"])

recommendations = [
    p for p in PRODUCTS
    if p["category"] == category
    and size in p["sizes"]
    and body_type in p["body_types"]
    and any(c in best_colors for c in p["colors"])
]

# fallback — relax body_type filter
if not recommendations:
    recommendations = [
        p for p in PRODUCTS
        if p["category"] == category
        and size in p["sizes"]
        and any(c in best_colors for c in p["colors"])
    ]

# fallback — any products for category
if not recommendations:
    recommendations = [p for p in PRODUCTS if p["category"] == category]

if recommendations:
    cols = st.columns(min(len(recommendations), 3))
    for i, prod in enumerate(recommendations):
        with cols[i % 3]:
            badge_cls, badge_label = PLATFORM_COLORS.get(prod["platform"], ("badge-amazon", prod["platform"]))
            # pick first matching colour
            matched_colors = [c for c in prod["colors"] if c in best_colors] or prod["colors"]
            color_swatches = "".join(
                f'<span style="display:inline-block;width:14px;height:14px;border-radius:3px;'
                f'background:{COLOR_HEX.get(c,"#ccc")};margin-right:3px;vertical-align:middle"></span>'
                for c in matched_colors
            )
            st.markdown(f"""
            <div class="product-card">
              <span class="product-badge {badge_cls}">{badge_label}</span>
              <div style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:600;
                          margin:.4rem 0 .3rem;color:var(--accent2)">{prod['title']}</div>
              <div style="font-size:.8rem;color:var(--muted);margin-bottom:.5rem">
                Colours: {color_swatches} {' · '.join(matched_colors)}
              </div>
              <div style="font-size:.78rem;color:#888;margin-bottom:.8rem">📏 Available: {' · '.join(prod['sizes'])}</div>
            </div>
            """, unsafe_allow_html=True)
            st.link_button(f"🛒 Shop on {prod['platform']}", prod["link"], use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
else:
    st.info("No products matched. Browse all platforms below:")
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1: st.link_button("🛒 Amazon",   "https://www.amazon.in/s?k=fashion+clothing", use_container_width=True)
    with pc2: st.link_button("🛒 Flipkart", "https://www.flipkart.com/search?q=fashion+clothing", use_container_width=True)
    with pc3: st.link_button("🛒 JioMart",  "https://www.jiomart.com/search/fashion", use_container_width=True)
    with pc4: st.link_button("🛒 Meesho",   "https://www.meesho.com/s?q=fashion", use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  STEP 5 — 3D MANNEQUIN + VIRTUAL TRY-ON
# ══════════════════════════════════════════════════════════════
st.markdown('<p class="sec-title">Step 5 — 3D Mannequin & Virtual Try-On</p>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
  👇 The mannequin below is built to <strong>your exact measurements</strong>.
  Upload a dress image (save from shopping site first) to see it on the mannequin.
  Use the 360° rotation slider to view from any angle.
</div>
""", unsafe_allow_html=True)

mann_col, ctrl_col = st.columns([1, 1.1])

with ctrl_col:
    st.markdown("**Upload Dress for Try-On**")
    dress_upload = st.file_uploader("Save dress image locally then upload here",
                                     type=["jpg","jpeg","png"], key="dress_uploader")
    if dress_upload:
        st.session_state.dress_img = Image.open(dress_upload).convert("RGBA")
        st.success("✅ Dress loaded! See try-on on the left →")

    st.markdown("**🔄 360° Rotation**")
    rotation = st.slider("Rotate Mannequin", 0, 359, st.session_state.rotation,
                          step=5, format="%d°", key="rot_slider")
    st.session_state.rotation = rotation

    # quick-turn buttons
    bt1, bt2, bt3, bt4 = st.columns(4)
    with bt1:
        if st.button("↶ 45°"):  st.session_state.rotation = (st.session_state.rotation - 45) % 360; st.rerun()
    with bt2:
        if st.button("→ Side"):  st.session_state.rotation = 90; st.rerun()
    with bt3:
        if st.button("↻ Back"):  st.session_state.rotation = 180; st.rerun()
    with bt4:
        if st.button("↺ Front"): st.session_state.rotation = 0;  st.rerun()

    st.markdown("**Mannequin Skin Tone**")
    st.markdown(f'<div class="skin-row"><div class="skin-dot" style="background:{skin_hex}"></div>'
                f'<span style="font-size:.9rem">Auto-matched to your skin tone: <strong>{skin_tone}</strong></span></div>',
                unsafe_allow_html=True)

    if st.session_state.dress_img:
        st.markdown("**Uploaded Dress Preview**")
        st.image(st.session_state.dress_img, use_container_width=True)

with mann_col:
    mann_img = draw_mannequin(
        shoulder_cm = m["shoulder_cm"],
        waist_cm    = m["waist_cm"],
        hip_cm      = m["hip_cm"],
        height_cm   = m["height_cm"],
        rotation_deg= st.session_state.rotation,
        skin_hex    = skin_hex,
        dress_img   = st.session_state.dress_img,
    )

    # convert to display
    buf = io.BytesIO()
    mann_img.save(buf, format="PNG")
    buf.seek(0)

    st.markdown('<div class="mannequin-stage">', unsafe_allow_html=True)
    st.image(buf, caption=f"Your 3D Mannequin — {int(st.session_state.rotation % 360)}° view",
             use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # download button
    dl_buf = io.BytesIO()
    mann_img.save(dl_buf, format="PNG")
    dl_buf.seek(0)
    st.download_button(
        label="⬇️ Download Mannequin Image",
        data=dl_buf,
        file_name=f"mannequin_{int(st.session_state.rotation)}deg.png",
        mime="image/png",
        use_container_width=True,
    )

# ══════════════════════════════════════════════════════════════
#  FOOTER SUMMARY
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style="background:var(--card);border:1px solid var(--border);border-radius:16px;
            padding:1.75rem;display:flex;flex-wrap:wrap;gap:1.5rem;align-items:center;justify-content:space-between">
  <div>
    <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;color:var(--accent2);margin-bottom:.3rem">
      Your Style Profile
    </div>
    <div style="font-size:.85rem;color:var(--muted);line-height:1.8">
      Body Type: <strong style="color:var(--text)">{body_type}</strong> &nbsp;·&nbsp;
      Skin Tone: <strong style="color:var(--text)">{skin_tone}</strong> &nbsp;·&nbsp;
      Size: <strong style="color:var(--text)">{size}</strong> &nbsp;·&nbsp;
      Height: <strong style="color:var(--text)">{m['height_cm']} cm</strong>
    </div>
  </div>
  <div style="font-size:.78rem;color:var(--muted)">👗 3D Fashion Stylist Pro</div>
</div>
""", unsafe_allow_html=True)
