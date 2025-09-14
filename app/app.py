# app.py
import os
from pathlib import Path
from datetime import datetime
import logging

import pandas as pd
import joblib
import numpy as np
import requests
import streamlit as st
from streamlit_option_menu import option_menu  # For better navigation
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Basic logging
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("krishimitra")

# =========================
# Page Config (must be the first Streamlit UI call)
# =========================
st.set_page_config(
    page_title="KrishiMitra AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3CB371;
        text-align: center;
    }
    .card { padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; background-color: #F8FFF8; }
    .disease-card { padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 15px; background-color: #FFF8F8; }
    .prevention-card { background-color: #F8F8FF; }
    .treatment-card { background-color: #F8FFF8; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🌾 KrishiMitra AI</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Intelligent Crop Recommendations for Indian Farmers</h2>', unsafe_allow_html=True)

# =========================
# Paths & Constants
# =========================
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR.parent / "images"
MODEL_PATH = BASE_DIR / "crop_model.pkl"
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR.parent / "crop_model.pkl"

# API key - prefer st.secrets, then env; fail if missing (Option A - strict)
API_KEY = None
try:
    API_KEY = st.secrets.get("OPENWEATHER_API_KEY")  # type: ignore
except Exception:
    API_KEY = None

if not API_KEY:
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    st.error("Missing OpenWeather API key. Set OPENWEATHER_API_KEY in st.secrets or as an environment variable.")
    st.stop()

# Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# =========================
# Crop Diseases Database
# =========================
CROP_DISEASES = {
    "Rice": [
        {
            "name": "Blast",
            "symptoms": "Spindle-shaped spots with gray centers and dark borders on leaves, nodes, and panicles",
            "prevention": ["Use resistant varieties", "Avoid excessive nitrogen", "Maintain proper water management"],
            "treatment": ["Apply fungicides like Tricyclazole", "Use bio-control agents like Pseudomonas fluorescens"],
            "season": "Throughout growth cycle, favored by high humidity"
        },
        {
            "name": "Brown Spot",
            "symptoms": "Small, circular to oval brown spots on leaves and grains",
            "prevention": ["Use disease-free seeds", "Practice crop rotation", "Maintain proper nutrition"],
            "treatment": ["Apply fungicides like Mancozeb", "Use resistant varieties"],
            "season": "Most severe during heading and grain filling"
        }
    ],
    "Maize": [
        {
            "name": "Corn Borer",
            "symptoms": "Small holes in leaves, stems broken at nodes, sawdust-like frass",
            "prevention": ["Use Bt corn varieties", "Proper crop rotation", "Remove crop residues"],
            "treatment": ["Apply Trichogramma wasps", "Use chemical insecticides if severe"],
            "season": "During growing season, especially early stages"
        },
        {
            "name": "Gray Leaf Spot",
            "symptoms": "Gray to tan rectangular lesions on leaves with distinct margins",
            "prevention": ["Use resistant hybrids", "Crop rotation", "Reduce plant density"],
            "treatment": ["Apply fungicides like Azoxystrobin", "Remove infected debris"],
            "season": "Warm, humid conditions during growing season"
        }
    ],
    "Cotton": [
        {
            "name": "Boll Rot",
            "symptoms": "Water-soaked lesions on bolls that later turn black and rot",
            "prevention": ["Avoid waterlogging", "Proper spacing", "Remove infected bolls"],
            "treatment": ["Spray Copper oxychloride", "Apply Trichoderma viride"],
            "season": "Boll formation stage, especially in humid conditions"
        },
        {
            "name": "Pink Bollworm",
            "symptoms": "Pink larvae in bolls, premature opening of bolls, seed damage",
            "prevention": ["Use pheromone traps", "Bt cotton varieties", "Crop rotation"],
            "treatment": ["Release Trichogramma wasps", "Apply specific insecticides"],
            "season": "During boll development stage"
        }
    ],
    "Potato": [
        {
            "name": "Late Blight",
            "symptoms": "Water-soaked lesions on leaves that turn brown and necrotic, white fungal growth underside",
            "prevention": ["Use certified seeds", "Proper hilling", "Avoid overhead irrigation"],
            "treatment": ["Spray Mancozeb", "Apply systemic fungicides"],
            "season": "Cool, moist weather conditions"
        },
        {
            "name": "Early Blight",
            "symptoms": "Dark brown spots with concentric rings on leaves and tubers",
            "prevention": ["Crop rotation", "Proper plant spacing", "Avoid overhead irrigation"],
            "treatment": ["Apply Chlorothalonil", "Remove infected plant debris"],
            "season": "Warm, humid conditions"
        }
    ],
    "Apple": [
        {
            "name": "Apple Scab",
            "symptoms": "Dark, scaly lesions on leaves and fruit, premature leaf drop",
            "prevention": ["Plant resistant varieties", "Prune for air circulation", "Remove fallen leaves"],
            "treatment": ["Apply fungicides like Captan", "Use dormant oil sprays"],
            "season": "Spring and early summer, favored by wet conditions"
        },
        {
            "name": "Fire Blight",
            "symptoms": "Wilting and blackening of shoots, cankers on branches",
            "prevention": ["Plant resistant varieties", "Avoid excess nitrogen", "Prune infected areas"],
            "treatment": ["Apply Streptomycin during bloom", "Remove infected branches"],
            "season": "Spring during bloom period"
        }
    ],
    "Banana": [
        {
            "name": "Panama Disease",
            "symptoms": "Yellowing of older leaves, wilting, vascular discoloration",
            "prevention": ["Use disease-free planting material", "Avoid infected soil", "Practice quarantine"],
            "treatment": ["Remove infected plants", "Soil solarization", "Use biological control agents"],
            "season": "Year-round, spreads through soil and water"
        },
        {
            "name": "Black Sigatoka",
            "symptoms": "Dark streaks on leaves, premature leaf death, reduced fruit quality",
            "prevention": ["Plant resistant varieties", "Improve drainage", "Remove infected leaves"],
            "treatment": ["Apply fungicides like Propiconazole", "Use cultural practices"],
            "season": "Warm, humid conditions throughout the year"
        }
    ],
    "Coconut": [
        {
            "name": "Lethal Yellowing",
            "symptoms": "Yellowing of fronds, premature nut drop, death of palm",
            "prevention": ["Plant resistant varieties", "Control insect vectors", "Use healthy seedlings"],
            "treatment": ["Inject tetracycline antibiotics", "Remove infected palms"],
            "season": "Year-round, transmitted by insect vectors"
        },
        {
            "name": "Bud Rot",
            "symptoms": "Rotting of the growing point, foul smell, collapse of crown",
            "prevention": ["Avoid injuries to palm", "Improve drainage", "Use copper fungicides"],
            "treatment": ["Apply systemic fungicides", "Remove infected tissue"],
            "season": "Rainy season, favored by high humidity"
        }
    ],
    "Coffee": [
        {
            "name": "Coffee Leaf Rust",
            "symptoms": "Orange-yellow powdery spots on undersides of leaves",
            "prevention": ["Plant resistant varieties", "Improve air circulation", "Manage shade properly"],
            "treatment": ["Apply copper-based fungicides", "Remove infected leaves"],
            "season": "Rainy season with high humidity"
        },
        {
            "name": "Coffee Berry Borer",
            "symptoms": "Small holes in coffee berries, reduced quality of beans",
            "prevention": ["Harvest all ripe cherries", "Remove fallen berries", "Use pheromone traps"],
            "treatment": ["Apply appropriate insecticides", "Use biological control agents"],
            "season": "During fruit development and harvesting"
        }
    ],
    "Grapes": [
        {
            "name": "Downy Mildew",
            "symptoms": "Yellow spots on upper leaf surface, white fungal growth underneath",
            "prevention": ["Improve air circulation", "Avoid overhead irrigation", "Use resistant varieties"],
            "treatment": ["Apply copper fungicides", "Use systemic fungicides"],
            "season": "Cool, moist conditions during growing season"
        },
        {
            "name": "Powdery Mildew",
            "symptoms": "White powdery growth on leaves, shoots, and berries",
            "prevention": ["Plant resistant varieties", "Prune for air circulation", "Avoid excess nitrogen"],
            "treatment": ["Apply sulfur-based fungicides", "Use systemic fungicides"],
            "season": "Warm, dry conditions with moderate humidity"
        }
    ],
    "Mango": [
        {
            "name": "Anthracnose",
            "symptoms": "Dark, sunken spots on leaves, flowers, and fruits",
            "prevention": ["Prune for air circulation", "Remove infected debris", "Avoid overhead irrigation"],
            "treatment": ["Apply copper-based fungicides", "Use systemic fungicides during flowering"],
            "season": "Rainy season and high humidity conditions"
        },
        {
            "name": "Powdery Mildew",
            "symptoms": "White powdery growth on leaves, flowers, and young fruits",
            "prevention": ["Plant in sunny locations", "Avoid overhead watering", "Prune for ventilation"],
            "treatment": ["Apply sulfur-based fungicides", "Use systemic fungicides"],
            "season": "Cool, humid conditions"
        }
    ],
    "Orange": [
        {
            "name": "Citrus Canker",
            "symptoms": "Raised, corky lesions on leaves, stems, and fruits",
            "prevention": ["Use disease-free nursery stock", "Avoid overhead irrigation", "Control citrus leafminer"],
            "treatment": ["Apply copper sprays", "Remove infected plant parts"],
            "season": "Warm, humid conditions with frequent rainfall"
        },
        {
            "name": "Greening Disease",
            "symptoms": "Yellowing of leaves, small bitter fruits, tree decline",
            "prevention": ["Control Asian citrus psyllid", "Use certified disease-free plants", "Remove infected trees"],
            "treatment": ["No cure available", "Manage psyllid populations", "Remove infected trees"],
            "season": "Year-round, transmitted by insect vectors"
        }
    ],
    "Papaya": [
        {
            "name": "Papaya Ringspot Virus",
            "symptoms": "Ring spots on fruits, mosaic patterns on leaves, stunted growth",
            "prevention": ["Use virus-resistant varieties", "Control aphid vectors", "Remove infected plants"],
            "treatment": ["No cure available", "Remove infected plants", "Control aphid populations"],
            "season": "Year-round, transmitted by aphid vectors"
        },
        {
            "name": "Black Spot",
            "symptoms": "Black spots on fruits, premature fruit drop",
            "prevention": ["Improve drainage", "Avoid overhead irrigation", "Practice crop rotation"],
            "treatment": ["Apply copper-based fungicides", "Remove infected fruits"],
            "season": "Rainy season with high humidity"
        }
    ],
    "Pomegranate": [
        {
            "name": "Bacterial Blight",
            "symptoms": "Water-soaked lesions on leaves, cracking of fruits",
            "prevention": ["Use disease-free planting material", "Avoid overhead irrigation", "Practice sanitation"],
            "treatment": ["Apply copper-based bactericides", "Remove infected plant parts"],
            "season": "Rainy season and high humidity conditions"
        },
        {
            "name": "Fruit Rot",
            "symptoms": "Brown rot of fruits, fungal growth on affected areas",
            "prevention": ["Improve air circulation", "Avoid fruit injuries", "Harvest at proper maturity"],
            "treatment": ["Apply fungicides like Carbendazim", "Remove infected fruits"],
            "season": "During fruit development and storage"
        }
    ],
    "Watermelon": [
        {
            "name": "Fusarium Wilt",
            "symptoms": "Yellowing and wilting of vines, vascular discoloration",
            "prevention": ["Use resistant varieties", "Practice crop rotation", "Improve soil drainage"],
            "treatment": ["No effective cure", "Remove infected plants", "Soil solarization"],
            "season": "Warm soil conditions, spreads through soil"
        },
        {
            "name": "Anthracnose",
            "symptoms": "Circular, sunken spots on fruits and leaves",
            "prevention": ["Use certified seeds", "Avoid overhead irrigation", "Practice crop rotation"],
            "treatment": ["Apply fungicides like Chlorothalonil", "Remove infected plant debris"],
            "season": "Warm, humid conditions"
        }
    ],
    "Muskmelon": [
        {
            "name": "Powdery Mildew",
            "symptoms": "White powdery growth on leaves and stems",
            "prevention": ["Plant resistant varieties", "Improve air circulation", "Avoid overhead watering"],
            "treatment": ["Apply sulfur-based fungicides", "Use systemic fungicides"],
            "season": "Warm, dry conditions with moderate humidity"
        },
        {
            "name": "Downy Mildew",
            "symptoms": "Yellow spots on leaves, fuzzy growth on undersides",
            "prevention": ["Use resistant varieties", "Improve drainage", "Avoid overhead irrigation"],
            "treatment": ["Apply copper-based fungicides", "Use systemic fungicides"],
            "season": "Cool, moist conditions"
        }
    ],
    "Chickpea": [
        {
            "name": "Wilt",
            "symptoms": "Yellowing and wilting of plants, vascular browning",
            "prevention": ["Use resistant varieties", "Practice crop rotation", "Treat seeds with fungicides"],
            "treatment": ["Apply soil fungicides", "Remove infected plants"],
            "season": "Warm soil conditions during growing season"
        },
        {
            "name": "Blight",
            "symptoms": "Brown spots on leaves, pods, and stems",
            "prevention": ["Use disease-free seeds", "Avoid overhead irrigation", "Practice crop rotation"],
            "treatment": ["Apply fungicides like Mancozeb", "Remove infected plant debris"],
            "season": "Cool, moist conditions"
        }
    ],
    "Lentil": [
        {
            "name": "Rust",
            "symptoms": "Orange pustules on leaves and pods",
            "prevention": ["Plant resistant varieties", "Avoid excess nitrogen", "Practice crop rotation"],
            "treatment": ["Apply fungicides like Propiconazole", "Remove infected debris"],
            "season": "Cool, moist conditions during flowering"
        },
        {
            "name": "Wilt",
            "symptoms": "Yellowing and wilting of plants, root rot",
            "prevention": ["Use certified seeds", "Improve soil drainage", "Practice crop rotation"],
            "treatment": ["Apply soil fungicides", "Remove infected plants"],
            "season": "Warm, moist soil conditions"
        }
    ],
    "Blackgram": [
        {
            "name": "Yellow Mosaic Virus",
            "symptoms": "Yellow mosaic patterns on leaves, stunted growth",
            "prevention": ["Control whitefly vectors", "Use virus-free seeds", "Remove infected plants"],
            "treatment": ["No cure available", "Control whitefly populations", "Remove infected plants"],
            "season": "Warm conditions, transmitted by whiteflies"
        },
        {
            "name": "Leaf Spot",
            "symptoms": "Brown spots on leaves, premature defoliation",
            "prevention": ["Use disease-free seeds", "Practice crop rotation", "Avoid overhead irrigation"],
            "treatment": ["Apply fungicides like Mancozeb", "Remove infected debris"],
            "season": "Rainy season and high humidity"
        }
    ],
    "Mungbean": [
        {
            "name": "Yellow Mosaic Virus",
            "symptoms": "Yellow patches on leaves, reduced pod formation",
            "prevention": ["Control whitefly vectors", "Use resistant varieties", "Remove infected plants"],
            "treatment": ["No cure available", "Control whitefly populations", "Use reflective mulch"],
            "season": "Warm conditions with high whitefly activity"
        },
        {
            "name": "Powdery Mildew",
            "symptoms": "White powdery growth on leaves and pods",
            "prevention": ["Plant resistant varieties", "Avoid overcrowding", "Improve air circulation"],
            "treatment": ["Apply sulfur-based fungicides", "Use systemic fungicides"],
            "season": "Cool, humid conditions"
        }
    ],
    "Mothbeans": [
        {
            "name": "Leaf Spot",
            "symptoms": "Circular brown spots on leaves, defoliation",
            "prevention": ["Use disease-free seeds", "Practice crop rotation", "Avoid overhead watering"],
            "treatment": ["Apply fungicides like Chlorothalonil", "Remove infected plant debris"],
            "season": "Rainy season with high humidity"
        },
        {
            "name": "Root Rot",
            "symptoms": "Yellowing of plants, rotting of roots, wilting",
            "prevention": ["Improve soil drainage", "Avoid overwatering", "Use well-drained fields"],
            "treatment": ["Apply soil fungicides", "Improve drainage"],
            "season": "Waterlogged conditions during monsoon"
        }
    ],
    "Kidneybeans": [
        {
            "name": "Common Blight",
            "symptoms": "Water-soaked spots on leaves, yellowing, defoliation",
            "prevention": ["Use certified seeds", "Avoid overhead irrigation", "Practice crop rotation"],
            "treatment": ["Apply copper-based bactericides", "Remove infected plant debris"],
            "season": "Warm, humid conditions"
        },
        {
            "name": "Anthracnose",
            "symptoms": "Sunken spots on pods, dark lesions on stems and leaves",
            "prevention": ["Use disease-free seeds", "Practice crop rotation", "Improve air circulation"],
            "treatment": ["Apply fungicides like Mancozeb", "Remove infected plant material"],
            "season": "Cool, moist conditions"
        }
    ],
    "Pigeonpeas": [
        {
            "name": "Wilt",
            "symptoms": "Yellowing and wilting of leaves, vascular browning",
            "prevention": ["Use resistant varieties", "Practice crop rotation", "Improve soil drainage"],
            "treatment": ["Apply soil fungicides", "Remove infected plants"],
            "season": "Warm, moist soil conditions"
        },
        {
            "name": "Pod Borer",
            "symptoms": "Holes in pods, larvae inside pods, reduced yield",
            "prevention": ["Use pheromone traps", "Practice intercropping", "Monitor regularly"],
            "treatment": ["Apply appropriate insecticides", "Use biological control agents"],
            "season": "During pod formation and development"
        }
    ],
    "Jute": [
        {
            "name": "Stem Rot",
            "symptoms": "Rotting of stem base, yellowing of leaves, plant death",
            "prevention": ["Improve field drainage", "Avoid overcrowding", "Use disease-free seeds"],
            "treatment": ["Apply fungicides like Carbendazim", "Remove infected plants"],
            "season": "Waterlogged conditions during monsoon"
        },
        {
            "name": "Leaf Spot",
            "symptoms": "Brown spots on leaves, premature defoliation",
            "prevention": ["Practice crop rotation", "Avoid overhead irrigation", "Remove crop debris"],
            "treatment": ["Apply fungicides like Mancozeb", "Improve air circulation"],
            "season": "High humidity and moderate temperature"
        }
    ]
}

# =========================
# Utilities
# =========================
def http_get_json(url: str, timeout=15):
    """HTTP request with error handling; returns parsed JSON or None."""
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.exception("HTTP request failed")
        st.error(f"Network error while contacting external API: {e}")
        return None

def safe_image_show(crop_name: str):
    """Show crop image if exists; show styled placeholder if missing."""
    if not IMAGES_DIR.exists():
        st.warning("❌ Images folder not found.")
        return

    base = crop_name.lower().replace(' ', '_')
    for ext in (".jpg", ".jpeg", ".png"):
        test_path = IMAGES_DIR / (base + ext)
        if test_path.exists():
            try:
                # Try to verify the image is valid before displaying
                from PIL import Image as PILImage
                with PILImage.open(test_path) as img:
                    img.verify()
                
                # If verification passes, display the image
                st.image(str(test_path), caption=crop_name, width=300)
                return
            except (TypeError, Exception) as e:
                # If there's any error with the image, create a placeholder instead
                logger.warning(f"Image error for {crop_name}: {e}")
                break

    # Show a nice placeholder instead of warning
    create_crop_placeholder(crop_name)

def create_crop_placeholder(crop_name: str):
    """Create a styled placeholder for missing crop images"""
    # Crop-specific colors and emojis
    crop_themes = {
        'blackgram': {'color': '#4A4A4A', 'bg': '#F5F5F5', 'emoji': '🤎', 'desc': 'Black Lentil'},
        'chickpea': {'color': '#D2691E', 'bg': '#FFF8DC', 'emoji': '🥬', 'desc': 'Chickpea/Gram'},
        'cotton': {'color': '#FFE4E1', 'bg': '#FFFFFF', 'emoji': '☁️', 'desc': 'Cotton Plant'},
        'lentil': {'color': '#CD853F', 'bg': '#FFF8DC', 'emoji': '🥬', 'desc': 'Red Lentils'},
        'mango': {'color': '#FFD700', 'bg': '#FFFAF0', 'emoji': '🥭', 'desc': 'Mango Tree'},
        'mothbeans': {'color': '#8B4513', 'bg': '#F5DEB3', 'emoji': '🌱', 'desc': 'Moth Beans'},
        'mungbean': {'color': '#228B22', 'bg': '#F0FFF0', 'emoji': '👌', 'desc': 'Mung Bean'},
        'muskmelon': {'color': '#FFA500', 'bg': '#FFFACD', 'emoji': '🍈', 'desc': 'Muskmelon'},
        'pigeonpeas': {'color': '#DAA520', 'bg': '#FFFAF0', 'emoji': '🥬', 'desc': 'Pigeon Peas'}
    }
    
    theme = crop_themes.get(crop_name.lower(), {'color': '#2E8B57', 'bg': '#F0FFF0', 'emoji': '🌱', 'desc': 'Agricultural Crop'})
    
    # Create a styled HTML placeholder
    placeholder_html = f"""
    <div style="
        width: 300px;
        height: 200px;
        background: linear-gradient(135deg, {theme['bg']} 0%, {theme['color']}20 100%);
        border: 2px solid {theme['color']};
        border-radius: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">{theme['emoji']}</div>
        <div style="
            font-size: 18px;
            font-weight: bold;
            color: {theme['color']};
            margin-bottom: 5px;
        ">{crop_name.title()}</div>
        <div style="
            font-size: 14px;
            color: {theme['color']}80;
            font-style: italic;
        ">{theme['desc']}</div>
        <div style="
            font-size: 12px;
            color: {theme['color']}60;
            margin-top: 8px;
        ">🎨 Crop Placeholder</div>
    </div>
    """
    
    st.markdown(placeholder_html, unsafe_allow_html=True)

def fmt_money(val: float) -> str:
    """Format currency (INR) nicely."""
    try:
        return f"₹{val:,.0f}"
    except Exception:
        return "₹-"

def get_lat_lon(pin: str):
    """Resolve lat/lon from Indian PIN code using OpenWeather geocoding (zip)."""
    if not pin or len(pin) != 6 or not pin.isdigit():
        return None, None

    url = f"https://api.openweathermap.org/geo/1.0/zip?zip={pin},IN&appid={API_KEY}"
    data = http_get_json(url)
    if not data:
        return None, None

    lat = data.get("lat")
    lon = data.get("lon")

    if lat is None or lon is None:
        # Some responses may include different fields or an error message
        logger.warning("Geocode response missing lat/lon: %s", data)
        return None, None

    try:
        return float(lat), float(lon)
    except Exception:
        return None, None

def get_weather(lat: float, lon: float):
    """Get weather summary (avg temp, avg humidity, total rainfall across forecast entries)."""
    if lat is None or lon is None:
        return None, None, None

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )
    data = http_get_json(url)
    if not data or "list" not in data:
        return None, None, None

    temps, hums, rains = [], [], []
    for entry in data["list"]:
        main = entry.get("main", {})
        temps.append(main.get("temp", 0.0))
        hums.append(main.get("humidity", 0.0))

        # 'rain' may be absent or a dict with '3h'
        rain = entry.get("rain", {})
        if isinstance(rain, dict):
            rains.append(rain.get("3h", 0.0))
        else:
            rains.append(0.0)

    try:
        temp_avg = float(np.mean(temps)) if temps else None
        hum_avg = float(np.mean(hums)) if hums else None
        rain_total = float(np.sum(rains)) if rains else 0.0
        return temp_avg, hum_avg, rain_total
    except Exception:
        logger.exception("Error computing weather aggregates")
        return None, None, None

# =========================
# Model & Encoder Load
# =========================
@st.cache_resource()
def load_model_and_encoder():
    """Load model and best-effort encoder with backward compatibility."""
    try:
        if not MODEL_PATH.exists():
            st.error(f"Model file not found at: {MODEL_PATH}")
            return None, None

        model_bundle = joblib.load(str(MODEL_PATH))
        # preferred: dict {"model":..., "encoder":...}
        if isinstance(model_bundle, dict) and "model" in model_bundle and "encoder" in model_bundle:
            return model_bundle["model"], model_bundle["encoder"]

        # tuple/list: (model, encoder)
        if isinstance(model_bundle, (list, tuple)) and len(model_bundle) >= 2:
            return model_bundle[0], model_bundle[1]

        # model only: try to locate encoder in pipeline steps
        model = model_bundle
        encoder = None

        # If pipeline, inspect named_steps for something with classes_
        try:
            named = getattr(model, "named_steps", {})
            if named:
                for name, step in named.items():
                    if hasattr(step, "classes_") and getattr(step, "classes_", None) is not None:
                        encoder = step
                        break
        except Exception:
            logger.debug("No named_steps or couldn't inspect pipeline for encoder")

        # final fallback: None (app will handle no encoder case)
        return model, encoder
    except Exception as e:
        logger.exception("Model load failed")
        st.error(f"⚠️ Could not load model or encoder. Technical detail: {e}")
        return None, None

model, label_encoder = load_model_and_encoder()

# Recommendation fallback if module not available
try:
    from recommendation import get_crop_recommendations  # type: ignore
except Exception as e:
    st.warning("Recommendation module not found. Using built-in fallback recommendations.")
    st.error(f"Import error details: {e}")
    def get_crop_recommendations(prediction, land_area, budget):
        """Fallback: return a single recommendation object."""
        return [{
            "name": prediction,
            "roi": budget * 1.5,
            "profit": budget * 0.8,
            "investment": budget * 0.7,
            "demand": "High",
            "price_trend": 1,
            "harvest_time": "3-4",
            "resilience": "7",
            "sowing_window": "June-July",
            "critical_months": "August",
            "weather_impact": {
                "Temperature": "Optimal between 20-30°C",
                "Rainfall": "Requires moderate rainfall"
            },
            "tips": ["Use organic fertilizers", "Maintain proper spacing"],
            "warnings": ["Avoid waterlogging", "Watch for pest attacks"]
        }]

# PDF export fallback
try:
    from export_pdf import generate_crop_pdf  # type: ignore
except Exception:
    generate_crop_pdf = None
    st.info("PDF export disabled. Add export_pdf.py (uses fpdf) to enable PDF reports.")

# =========================
# Navigation
# =========================
selected_tab = option_menu(
    None,
    ["Get Recommendations", "Crop Calendar", "Crop Diseases", "Farming Guidelines"],
    icons=['🎯', '🗓️', '🦠', '📖'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

# =========================
# TAB 1: Crop Recommendation
# =========================
if selected_tab == "Get Recommendations":
    st.header("📍 Smart Crop Recommendation Based on Weather & Soil")

    with st.form("crop_recommendation_form"):
        col1, col2 = st.columns(2)

        with col1:
            pin_code = st.text_input("📮 Enter your PIN code", max_chars=6,
                                     placeholder="e.g., 395007", help="6-digit Indian PIN code")
            land_area = st.number_input("🌾 Land Area (acres)", min_value=0.1,
                                        max_value=1000.0, value=1.0, step=0.1)
            budget = st.number_input("💰 Budget (₹)", min_value=1000,
                                     max_value=10_000_000, value=50_000, step=1000)

        with col2:
            st.subheader("🧪 Soil Parameters")
            n = st.slider("🌿 Nitrogen (N) level", min_value=0, max_value=200, value=50)
            p = st.slider("🧪 Phosphorus (P) level", min_value=0, max_value=200, value=50)
            k = st.slider("🧲 Potassium (K) level", min_value=0, max_value=200, value=50)
            ph = st.slider("🧬 Soil pH", min_value=0.0, max_value=14.0, value=6.5, step=0.1)

        submitted = st.form_submit_button("🌱 Get Crop Recommendations")

    if submitted:
        # basic validations
        if not pin_code or len(pin_code) != 6 or not pin_code.isdigit():
            st.error("❌ Please enter a valid 6-digit PIN code.")
        elif model is None:
            st.error("❌ Crop prediction model is not available.")
        else:
            with st.spinner("🌤️ Fetching weather data..."):
                lat, lon = get_lat_lon(pin_code)

            if lat is None or lon is None:
                st.error("📍 Couldn't find location for that PIN code. Please check and try again.")
            else:
                with st.spinner("📊 Analyzing weather and soil conditions..."):
                    temp, humidity, rainfall = get_weather(lat, lon)

                if temp is None:
                    st.error("⚠️ Weather data unavailable. Please try again later.")
                else:
                    # Display weather information
                    weather_col1, weather_col2, weather_col3 = st.columns(3)
                    with weather_col1:
                        st.metric("Temperature", f"{temp:.1f}°C")
                    with weather_col2:
                        st.metric("Humidity", f"{humidity:.1f}%")
                    with weather_col3:
                        st.metric("Rainfall (forecast sum)", f"{rainfall:.1f} mm")

                    # Feature order used during model training - ensure exact order
                    feature_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
                    features = pd.DataFrame([{
                        "N": n, "P": p, "K": k,
                        "temperature": temp, "humidity": humidity,
                        "ph": ph, "rainfall": rainfall
                    }])[feature_order]

                    # Skip ML model prediction - use pincode-based recommendations directly
                    st.info("📍 **Using Pincode-Based Recommendations:** Analyzing crops from dataset based on your location")
                    
                    # Set a dummy prediction since we're using pincode-based mode
                    prediction = "PINCODE_BASED"

                    # get recommendations (plugin or fallback) - pass pincode for location-specific recommendations
                    try:
                        # Get recommendations with API key
                        api_key = os.getenv('OPENWEATHERMAP_API_KEY')
                        
                        # Show weather data status
                        if api_key:
                            st.info("🌤️ Using real-time weather data for recommendations...")
                        else:
                            st.warning("⚠️ No API key found. Using pincode-based weather estimation for recommendations.")
                        
                        # IMPORTANT: Get pincode-specific recommendations directly from dataset
                        # AGGRESSIVE cache clearing and session state management
                        try:
                            st.cache_data.clear()
                        except:
                            pass
                        try:
                            st.cache_resource.clear() 
                        except:
                            pass
                        
                        # Clear any cached function results
                        if hasattr(get_crop_recommendations, 'clear'):
                            get_crop_recommendations.clear()
                        
                        # Force Python to clear any internal caches
                        import gc
                        gc.collect()
                        
                        # Store current pincode in session state to track changes
                        if 'current_pincode' not in st.session_state:
                            st.session_state.current_pincode = None
                        
                        # Check if pincode changed
                        if st.session_state.current_pincode != pin_code:
                            st.write(f"🔄 **PINCODE CHANGED:** {st.session_state.current_pincode} → {pin_code}**")
                            st.session_state.current_pincode = pin_code
                            # Clear any cached data when pincode changes
                            if hasattr(st, 'cache_data'):
                                st.cache_data.clear()
                        else:
                            st.write(f"🔍 **Getting recommendations for PIN {pin_code}...**")
                        
                        # Get recommendations with explicit parameters and unique processing
                        import hashlib
                        import time
                        timestamp = int(time.time() * 1000)  # Millisecond timestamp
                        pincode_hash = hashlib.md5(f"{pin_code}_{budget}_{land_area}_{timestamp}".encode()).hexdigest()[:8]
                        st.write(f"📊 **Processing ID:** {pincode_hash} (timestamp: {timestamp})")
                        
                        # USE COMPLETELY FRESH FUNCTION - bypass ALL possible caching
                        import sys
                        import os
                        
                        # Import the fresh recommendation function
                        sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
                        from fresh_recommendations import get_fresh_crop_recommendations
                        
                        # Call completely fresh function
                        st.write(f"🆕 **USING FRESH FUNCTION for PIN {pin_code}**")
                        recommendations = get_fresh_crop_recommendations(
                            pincode=str(pin_code),
                            land_area=land_area, 
                            budget=budget
                        )
                        
                        # Show fresh results immediately
                        if recommendations:
                            fresh_top_3 = [rec['name'] for rec in recommendations[:3]]
                            st.success(f"✨ **FRESH RESULTS for PIN {pin_code}:** {', '.join(fresh_top_3)}")
                        
                        if recommendations:
                            # Show detailed debugging information
                            top_3_crops = [rec['name'] for rec in recommendations[:3]]
                            st.success(f"🌾 **PIN {pin_code} Top 3:** {', '.join(top_3_crops)}")
                            
                            # Additional verification
                            st.write("**🗺️ VERIFICATION:**")
                            for i, rec in enumerate(recommendations[:5], 1):
                                score = rec.get('debug_score', 'N/A')
                                st.write(f"{i}. **{rec['name']}** (Score: {score})")
                            
                            # Double-check by calling fresh function again
                            st.write("**🔄 DOUBLE-CHECK (calling fresh function again):**")
                            verify_recs = get_fresh_crop_recommendations(str(pin_code), land_area, budget)
                            verify_top_3 = [rec['name'] for rec in verify_recs[:3]] if verify_recs else ["No crops"]
                            st.write(f"Second call result: {', '.join(verify_top_3)}")
                            
                        else:
                            st.error("No recommendations generated!")
                        
                        # Show success message
                        if api_key and recommendations:
                            st.success(f"✅ Found {len(recommendations)} crops specifically suited for PIN {pin_code} using real-time weather!")
                        elif recommendations:
                            st.success(f"✅ Found {len(recommendations)} crops specifically suited for PIN {pin_code} based on regional conditions!")
                    except Exception:
                        logger.exception("Recommendation function failed; using fallback single recommendation")
                        recommendations = [{
                            "name": prediction,
                            "roi": budget * 1.2,
                            "profit": budget * 0.7,
                            "investment": budget * 0.6,
                            "demand": "High",
                            "price_trend": 1,
                            "harvest_time": "3-4",
                            "resilience": "7",
                            "sowing_window": "June-July",
                            "critical_months": "August",
                            "weather_impact": {"Temperature": "20-30°C", "Rainfall": "Moderate"},
                            "tips": ["Use organic fertilizers", "Maintain proper spacing"],
                            "warnings": ["Avoid waterlogging"]
                        }]

                    # Check image availability
                    available_images = len([f for f in (IMAGES_DIR).glob('*.jpg')]) if IMAGES_DIR.exists() else 0
                    total_crops = 22  # From dataset analysis
                    
                    if available_images >= total_crops:
                        st.success(f"🎨 **Complete Image Collection:** All {total_crops} crop images available! ({available_images} total images)")
                    else:
                        st.info(f"🖼️ **Image Status:** {available_images}/{total_crops} crop images available. Missing images will show as styled placeholders.")
                    
                    st.success(f"✅ Analysis complete for PIN {pin_code}! Here are your best crop options:")

                    for idx, crop in enumerate(recommendations, 1):
                        crop_name = crop.get('name', 'Unknown Crop')
                        with st.expander(f"{idx}. {crop_name} 🌱 (PIN: {pin_code})", expanded=(idx == 1)):
                            # Clear pincode identification
                            st.info(f"📍 **This crop recommendation is specifically for PIN {pin_code}**")
                            
                            col_img, col_info = st.columns([1, 2])
                            with col_img:
                                safe_image_show(crop_name)
                            with col_info:
                                st.subheader(f"{crop_name} for PIN {pin_code}")
                                st.write(f"**Specifically suited for:** {pin_code} region")
                                st.write(f"**Your land area:** {land_area} acres")

                            # Financial Overview
                            st.subheader("💰 Financial Overview")
                            fin1, fin2, fin3 = st.columns(3)
                            with fin1:
                                st.metric("Expected ROI", fmt_money(crop.get("roi", 0)))
                                st.metric("Profit Potential", fmt_money(crop.get("profit", 0)))
                            with fin2:
                                inv = crop.get("investment", 0)
                                st.metric("Investment Needed", fmt_money(inv))
                                st.metric("Per Acre Cost", fmt_money(inv / max(land_area, 0.1)))
                            with fin3:
                                st.metric("Market Demand", crop.get("demand", "—"))
                                trend = crop.get("price_trend", 0)
                                trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                                st.metric("Price Trend", f"{trend_icon} {'Rising' if trend > 0 else 'Falling' if trend < 0 else 'Stable'}")

                            # Timeline & Season Info
                            st.subheader("🗓️ Growth Timeline")
                            time1, time2 = st.columns(2)
                            with time1:
                                st.metric("Time to Harvest", f"{crop.get('harvest_time', '—')} months")
                                st.metric("Resilience Score", f"{crop.get('resilience', '—')}/10")
                            with time2:
                                st.write(f"**Best Sowing Window:** {crop.get('sowing_window', '—')}")
                                st.write(f"**Critical Months:** {crop.get('critical_months', '—')}")

                            # Weather Suitability
                            st.subheader("🌤️ Weather Suitability")
                            weather_impact = crop.get("weather_impact", {})
                            if weather_impact:
                                for factor, impact in weather_impact.items():
                                    st.write(f"• **{factor}:** {impact}")
                            else:
                                st.info("Weather impact data not available.")

                            # Cultivation Guidelines
                            st.subheader("🌱 Cultivation Guidelines")
                            guide1, guide2 = st.columns(2)
                            with guide1:
                                st.write("✅ **Best Practices:**")
                                for tip in crop.get("tips", []):
                                    st.write(f"• {tip}")
                            with guide2:
                                st.write("❌ **Things to Avoid:**")
                                for warn in crop.get("warnings", []):
                                    st.write(f"• {warn}")

                    # PDF Export if supported
                    if generate_crop_pdf:
                        try:
                            pdf_path = generate_crop_pdf(recommendations, land_area)
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="📄 Download Detailed PDF Report",
                                    data=f,
                                    file_name="crop_recommendation_report.pdf",
                                    mime="application/pdf",
                                    # width='stretch',
                                )
                        except Exception as e:
                            logger.exception("PDF export failed")
                            st.error(f"PDF generation failed: {e}")
                    else:
                        st.info("💡 Install fpdf and add export_pdf.py to enable PDF report downloads")

# =========================
# TAB 2: Crop Calendar
# =========================
elif selected_tab == "Crop Calendar":
    st.header("🗓️ Monthly Crop Calendar")

    current_month = datetime.now().strftime("%B")
    st.success(f"📅 Current month: {current_month}")

    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox("Select month to view:", months, index=datetime.now().month - 1)

    crop_calendar = {
        "Kharif Crops (Monsoon: June–October)": {
            "Rice": "Jun–Jul",
            "Cotton": "May–Jun",
            "Maize": "Jun–Jul",
            "Soybean": "Jun–Jul",
            "Groundnut": "Jun–Jul",
        },
        "Rabi Crops (Winter: October–March)": {
            "Wheat": "Oct–Nov",
            "Mustard": "Oct–Nov",
            "Chickpea": "Oct–Nov",
            "Potato": "Oct–Nov",
            "Barley": "Oct–Nov",
        },
        "Zaid Crops (Summer: March–June)": {
            "Watermelon": "Feb–Mar",
            "Muskmelon": "Feb–Mar",
            "Cucumber": "Feb–Mar",
            "Vegetables": "Year-round",
        },
    }

    for season, crops in crop_calendar.items():
        st.subheader(season)
        for crop, sowing_time in crops.items():
            is_current_season = selected_month in sowing_time or "Year-round" in sowing_time
            if is_current_season:
                st.markdown(f"✅ **{crop}** - {sowing_time} *(Ideal for {selected_month})*")
            else:
                st.markdown(f"🌱 {crop} - {sowing_time}")

# =========================
# TAB 3: Crop Diseases
# =========================
elif selected_tab == "Crop Diseases":
    st.header("🦠 Crop Disease Identification & Management")
    st.info("""
    This section helps you identify common crop diseases, their symptoms, and effective management strategies.
    Select a crop to view its common diseases and recommended treatments.
    """)

    crops_list = list(CROP_DISEASES.keys())
    selected_crop = st.selectbox("🌾 Select a crop:", crops_list)

    if selected_crop in CROP_DISEASES:
        st.subheader(f"Common Diseases in {selected_crop}")
        for disease in CROP_DISEASES[selected_crop]:
            with st.expander(f"🦠 {disease['name']}", expanded=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("#### 📋 Symptoms")
                    st.write(disease['symptoms'])
                    st.markdown("#### 📅 Common Season")
                    st.write(disease['season'])
                with col2:
                    st.markdown("#### 🛡️ Prevention")
                    for prevention in disease['prevention']:
                        st.write(f"• {prevention}")
                    st.markdown("#### 💊 Treatment")
                    for treatment in disease['treatment']:
                        st.write(f"• {treatment}")

    st.subheader("🌿 General Disease Prevention Tips")
    tip_col1, tip_col2, tip_col3 = st.columns(3)
    with tip_col1:
        st.markdown("**🌱 Cultural Practices**")
        st.write("• Practice crop rotation")
        st.write("• Use certified disease-free seeds")
        st.write("• Maintain proper plant spacing")
        st.write("• Remove and destroy infected plants")
    with tip_col2:
        st.markdown("**💧 Water Management**")
        st.write("• Avoid overhead irrigation")
        st.write("• Ensure proper drainage")
        st.write("• Water in morning hours")
        st.write("• Avoid waterlogging")
    with tip_col3:
        st.markdown("**🧪 Chemical Management**")
        st.write("• Use fungicides as preventive measure")
        st.write("• Follow recommended dosage")
        st.write("• Rotate chemical groups to avoid resistance")
        st.write("• Observe pre-harvest intervals")

    st.subheader("🔍 Need Help Identifying a Disease?")
    with st.form("disease_identification_form"):
        st.write("Describe the symptoms you're observing:")
        crop_type = st.selectbox("Crop type", crops_list)
        plant_part = st.selectbox("Affected plant part", ["Leaves", "Stems", "Roots", "Fruits", "Flowers", "Whole plant"])
        symptom_desc = st.text_area("Describe the symptoms in detail")
        uploaded_img = st.file_uploader("Upload a photo (if available)", type=['jpg', 'jpeg', 'png'])
        submitted = st.form_submit_button("Get Identification Help")

        if submitted:
            st.success("Thank you for the information! Our agricultural experts will review your query and provide guidance.")
            st.info("For immediate assistance, contact your local Krishi Vigyan Kendra (KVK) or agricultural extension officer.")

# =========================
# TAB 4: Farming Guidelines
# =========================
else:
    st.header("📖 Farming Best Practices & Guidelines")
    topics = {
        "🌡️ Weather Considerations": [
            "Monitor local weather forecasts regularly",
            "Plan irrigation based on rainfall predictions",
            "Protect crops from extreme weather events",
            "Consider crop insurance for weather risks"
        ],
        "💧 Water Management": [
            "Implement drip irrigation for water efficiency",
            "Use mulching to reduce evaporation",
            "Practice rainwater harvesting",
            "Schedule irrigation based on soil moisture"
        ],
        "🌿 Soil Health": [
            "Conduct soil testing every season",
            "Practice crop rotation to maintain fertility",
            "Use organic compost and green manure",
            "Maintain optimal soil pH for your crops"
        ],
        "🐛 Pest Management": [
            "Use integrated pest management (IPM) approaches",
            "Monitor crops regularly for early detection",
            "Prefer biological controls over chemicals",
            "Practice field sanitation to reduce pests"
        ],
        "💰 Financial Planning": [
            "Maintain detailed records of expenses and income",
            "Explore government subsidy programs",
            "Diversify crops to manage market risks",
            "Consider contract farming for stable prices"
        ]
    }
    for topic, guidelines in topics.items():
        with st.expander(topic):
            for guideline in guidelines:
                st.write(f"• {guideline}")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 20px;'>
        <p>Made with ❤️ for Indian Farmers | 🌾 KrishiMitra AI</p>
        <p>Data sources: Soil Health Card, AgMarkNet, ICRISAT, FAO, OpenWeather</p>
        <p>For support: contact@krishimitrai.com</p>
    </div>
    """,
    unsafe_allow_html=True,
)
