import os
# Prevent transformers from importing TensorFlow/Flax (can hang); this app only needs PyTorch
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
from pathlib import Path
from datetime import datetime
import logging
import gc
import hashlib
import time
import sys
import random
from fpdf import FPDF
import pandas as pd
import joblib
import numpy as np
import requests
import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
from PIL import Image
from googletrans import Translator
from transformers import AutoImageProcessor, ViTForImageClassification
import torch
from io import BytesIO
import traceback
import json

# Try to import additional libraries
try:
    from export_pdf import generate_crop_pdf
except ImportError:
    def generate_crop_pdf(recommendations, land_area):
        """Fallback PDF generation function."""
        st.warning("PDF export functionality not available. Install fpdf and add export_pdf.py.")
        return None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:
    pass

# Hugging Face disease model is loaded lazily (first use) so the app starts fast
@st.cache_resource(show_spinner="Loading disease detection model...")
def load_disease_model():
    try:
        return (AutoImageProcessor.from_pretrained("wambugu71/crop_leaf_diseases_vit"),
                ViTForImageClassification.from_pretrained("wambugu71/crop_leaf_diseases_vit"))
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to load disease detection model: {e}")
        return None, None

# Initialize translator
translator = Translator()

# Try to import voice-related libraries
try:
    import speech_recognition as sr
    from gtts import gTTS
    import pygame
    import io
    HAS_VOICE = True
    
    # Voice functions
    def speak_text(text, language=None):
        """Convert text to speech in the selected UI language and play it"""
        try:
            if language is None:
                lang_name = st.session_state.get("language", "English")
                language = globals().get("languages", {}).get(lang_name, {}).get("code", "en")
            text = str(text).replace("*", "").replace("#", "").replace("_", " ")
            tts = gTTS(text=text, lang=language, slow=False)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"Text-to-speech error: {e}")

    def listen_to_speech():
        """Listen to microphone input and return text"""
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=1)
                st.info("Listening... Speak now")
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                try:
                    return r.recognize_google(audio)
                except sr.UnknownValueError:
                    st.error("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    st.error(f"Error with speech recognition: {e}")
                    return None
        except Exception as e:
            st.error(f"Speech recognition error: {e}")
            return None
            
except ImportError:
    HAS_VOICE = False
    
    # Define dummy functions if voice libraries are not available
    def speak_text(text, language="en"):
        st.error("Voice features are not available. Please install gTTS, pygame, and speech_recognition.")
    
    def listen_to_speech():
        st.error("Voice features are not available. Please install gTTS, pygame, and speech_recognition.")
        return None

load_dotenv()

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("krishimitra")

# Page Config (must be the first Streamlit UI call)
st.set_page_config(
    page_title="KrishiMitra AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        background-color: #F8FFFB;
    }

    .disease-card {
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        background-color: #FFFFFB;
    }

    .prevention-card {
        background-color: #F8F8FF;
    }

    .treatment-card {
        background-color: #F8FFFB;
    }

    .chat-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        max-height: 400px;
        overflow-y: auto;
    }

    .user-message {
        background-color: #dcf8c6;
        color: #000000;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: right;
        max-width: 80%;
        margin-left: auto;
    }

    .bot-message {
        background-color: #ffffff;
        color: #000000;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: left;
        max-width: 80%;
        margin-right: auto;
        border: 1px solid #e0e0e0;
    }

    .alert-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px;
        margin: 10px 0;
        border-radius: 4px;
    }
    
    .voice-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    
    .farmer-profile {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .community-advice {
        background-color: #f1f8e9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #000000;
    }
    
    .government-scheme {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #000000;
        border-left: 4px solid #2196F3;
    }
    
    .government-scheme h4 {
        color: #0d47a1;
        margin-top: 0;
    }
    
    .government-scheme p {
        color: #000000;
    }
    
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 12px;
        margin: 10px 0;
        border-radius: 4px;
        color: #c62828;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    :root {
        --km-green: #2F7D32;
        --km-green-2: #66A94D;
        --km-leaf: #E4F0D4;
        --km-cream: #FBF8EF;
        --km-wheat: #E8B93C;
        --km-soil: #6B4F2A;
        --km-card: #FFFFFF;
        --km-border: #D5E4BF;
        --km-text: #26361F;
    }
    .stApp {
        background:
            radial-gradient(circle at 92% 4%, rgba(232,185,60,.18), transparent 32%),
            linear-gradient(180deg, #F6FAEE 0%, #FBF8EF 45%, #F3F8E8 100%);
        color: var(--km-text);
    }
    .block-container { padding-top: 1.4rem; max-width: 1200px; }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* Hero banner */
    .km-hero {
        position: relative; overflow: hidden; text-align: center;
        background:
            linear-gradient(160deg, #2F7D32 0%, #4C9A3B 55%, #8DBF4A 100%);
        border-radius: 22px; padding: 30px 20px 26px 20px; margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(47,125,50,.25);
    }
    .km-hero::before { content: "🌾  🌱  🌾  🌿  🌾"; position: absolute; left: 0; right: 0; bottom: -6px;
        font-size: 2.2rem; letter-spacing: 1.1rem; opacity: .22; white-space: nowrap; }
    .km-hero::after { content: "☀️"; position: absolute; right: 26px; top: 14px; font-size: 2.2rem; }
    .main-header { font-size: 2.8rem; font-weight: 800; color: #fff !important; margin: 0; letter-spacing: .5px;
        -webkit-text-fill-color: #fff; }
    .sub-header { font-size: 1.1rem; font-weight: 400; color: #F3FAE6 !important; margin: .3rem 0 0 0; }

    h1, h2, h3, h4 { color: var(--km-green) !important; }

    /* Cards */
    .card, .disease-card, .prevention-card, .treatment-card, .farmer-profile, .community-advice {
        background-color: var(--km-card) !important;
        border: 1px solid var(--km-border);
        border-left: 5px solid var(--km-green-2);
        color: var(--km-text) !important;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(80,110,50,.08);
    }
    .government-scheme { background-color: #F1F7FF !important; color: var(--km-text) !important; }
    .government-scheme h4, .government-scheme p { color: var(--km-text) !important; }
    .bot-message { background: #fff; color: var(--km-text); }
    .user-message { background: var(--km-leaf); color: var(--km-text); }
    .alert-box { background: #FFF6DA; border-left: 4px solid var(--km-wheat); color: var(--km-text); }

    /* Metric tiles */
    div[data-testid="stMetric"] {
        background: var(--km-card); border: 1px solid var(--km-border);
        border-top: 4px solid var(--km-wheat);
        border-radius: 14px; padding: 12px 14px; box-shadow: 0 2px 8px rgba(80,110,50,.08);
    }
    div[data-testid="stMetricLabel"] p { color: var(--km-soil); font-weight: 600; }
    div[data-testid="stMetricValue"] { color: var(--km-green); }

    /* Expanders, forms, sidebar */
    div[data-testid="stExpander"] { background: rgba(255,255,255,.75); border: 1px solid var(--km-border); border-radius: 14px; }
    div[data-testid="stForm"] { background: rgba(255,255,255,.8); border: 1px solid var(--km-border); border-radius: 18px; padding: 1.3rem; }
    section[data-testid="stSidebar"] { background: #EAF3DC; border-right: 1px solid var(--km-border); }

    /* Inputs */
    div[data-baseweb="input"] input, div[data-baseweb="select"] > div, textarea { border-radius: 10px !important; }

    /* Buttons */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        border-radius: 12px; font-weight: 700; border: 1px solid var(--km-green);
        background: #fff; color: var(--km-green); transition: all .15s ease;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: var(--km-green); color: #fff; box-shadow: 0 4px 14px rgba(47,125,50,.3); transform: translateY(-1px);
    }
    div[data-testid="stFormSubmitButton"] > button { background: var(--km-green); color: #fff; }

    /* Top-pick banner */
    .km-top {
        background: linear-gradient(135deg, #FFF4CC 0%, #E9F5D3 100%);
        border: 1px solid #E5D48A; border-left: 6px solid var(--km-wheat);
        border-radius: 16px; padding: 18px 22px; margin: 8px 0 16px 0;
        box-shadow: 0 3px 12px rgba(200,160,40,.15);
    }
    .km-top h3 { margin: 0 0 6px 0; color: var(--km-soil) !important; }
    .km-top p { margin: 0; color: var(--km-text); }
    .km-chip { display: inline-block; padding: 2px 11px; border-radius: 999px; font-size: .8rem; font-weight: 700;
        background: var(--km-green); color: #fff; margin-right: 8px; }

    @media (max-width: 640px) {
        .main-header { font-size: 1.9rem; }
        .km-hero { padding: 22px 12px; }
        .km-hero::after { display: none; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# Translation dictionary for the entire UI
TRANSLATIONS = {
    "English": {
        "main_header": "KrishiMitra AI",
        "sub_header": "Intelligent Crop Recommendations for Indian Farmers",
        "language_settings": "Language Settings",
        "select_language": "Select Language",
        "feedback": "Feedback",
        "provide_feedback": "Provide Feedback",
        "share_experience": "Share your experience",
        "rate_experience": "Rate your experience (1-5)",
        "additional_comments": "Additional comments",
        "submit_feedback": "Submit Feedback",
        "thank_you_feedback": "Thank you for your feedback!",
        "get_recommendations": "Get Recommendations",
        "crop_calendar": "Crop Calendar",
        "crop_diseases": "Crop Diseases",
        "farming_guidelines": "Farming Guidelines",
        "ai_assistant": "AI Assistant",
        "crop_recommendation_ai": "Crop Recommendation by AI",
        "fertilizer_guide": "Fertilizer Guide",
        "government_schemes": "Government Schemes",
        "community": "Community",
        "farmer_profile": "Farmer Profile",
        "smart_crop_recommendation": "🔍 Smart Crop Recommendation Based on Weather & Soil",
        "enter_pin_code": "Enter your PIN code",
        "pin_help": "6-digit Indian PIN code",
        "land_area": "Land Area (acres)",
        "budget": "Budget (Rs)",
        "soil_parameters": "🔍 Soil Parameters",
        "nitrogen": "Nitrogen (N) level",
        "phosphorus": "Phosphorus (P) level",
        "potassium": "Potassium (K) level",
        "soil_ph": "Soil pH",
        "get_recommendations_btn": "Get Crop Recommendations",
        "invalid_pin": "✗ Please enter a valid 6-digit PIN code.",
        "model_error": "✗ Crop prediction model is not available.",
        "location_error": "Couldn't find location for that PIN code. Please check and try again.",
        "weather_error": "Weather data unavailable. Please try again later.",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "rainfall": "Rainfall (forecast sum)",
        "weather_alerts": "Weather Alerts:",
        "analysis_complete": "✔ Analysis complete for PIN {pin_code}: Here are your best crop options:",
        "specifically_for": "This crop recommendation is specifically for PIN {pin_code}",
        "specifically_suited": "Specifically suited for: {pin_code} region",
        "your_land_area": "Your land area: {land_area} acres",
        "financial_overview": "Financial Overview",
        "expected_roi": "Expected Revenue",
        "profit_potential": "Profit Potential",
        "investment_needed": "Investment Needed",
        "per_acre_cost": "Per Acre Cost",
        "market_demand": "Market Demand",
        "price_trend": "Price Trend",
        "market_information": "Market Information",
        "market_price_range": "Market Price Range",
        "growth_timeline": "Growth Timeline",
        "time_to_harvest": "Time to Harvest",
        "resilience_score": "Resilience Score",
        "best_sowing_window": "Best Sowing Window",
        "critical_months": "Critical Months",
        "weather_suitability": "Weather Suitability",
        "cultivation_guidelines": "Cultivation Guidelines",
        "best_practices": "Best Practices",
        "things_to_avoid": "Things to Avoid",
        "download_pdf": "📄 Download Detailed PDF Report",
        "monthly_crop_calendar": "📅 Monthly Crop Calendar",
        "current_month": "Current month: {current_month}",
        "select_month": "Select month to view:",
        "crop_disease_identification": "🦠 Crop Disease Identification & Management",
        "disease_help": "This section helps you identify common crop diseases, their symptoms, and effective management strategies. Select a crop to view its common diseases and recommended treatments.",
        "select_crop": "Select a crop:",
        "common_diseases": "Common Diseases in {crop}",
        "symptoms": "🔍 Symptoms",
        "common_season": "🔍 Common Season",
        "prevention": "🔍 Prevention",
        "treatment": "🔍 Treatment",
        "general_prevention_tips": "🔍 General Disease Prevention Tips",
        "cultural_practices": "🌱 Cultural Practices",
        "water_management": "💧 Water Management",
        "chemical_management": "🧪 Chemical Management",
        "ai_disease_detection": "🤖 AI Disease Detection",
        "ai_disease_help": "Upload an image of affected plant part for AI-assisted diagnosis",
        "choose_image": "Choose an image...",
        "analyze_image": "Analyze Image",
        "analyzing": "Analyzing image for disease patterns...",
        "analysis_complete_disease": "Analysis Complete",
        "detected_disease": "Detected Disease:",
        "farming_best_practices": "📖 Farming Best Practices & Guidelines",
        "ai_assistant_header": "🤖 KrishiMitra AI Assistant",
        "ai_assistant_help": "Ask me anything about farming, crops, weather, soil, or any agricultural topic. I'm here to help you with your farming questions and provide expert advice.",
        "chat_with_ai": "💬 Chat with KrishiMitra AI",
        "voice_input": "🎤 Voice Input",
        "type_question": "Type your farming question here:",
        "send_message": "Send Message",
        "clear_chat": "Clear Chat",
        "read_last": "🔊 Read Last",
        "ai_thinking": "KrishiMitra AI is thinking...",
        "suggested_questions": "💡 Suggested Questions",
        "ai_powered_recommendation": "🤖 AI-Powered Crop Recommendation",
        "ai_crop_help": "Get personalized crop recommendations based on your specific conditions using AI. Describe your soil, climate, and preferences, and our AI will suggest the best crops for you.",
        "ai_crop_chat": "💬 AI Crop Recommendation Chat",
        "tell_conditions": "💬 Tell us about your farming conditions",
        "soil_type": "Soil Type",
        "climate": "Climate",
        "water_availability": "Water Availability",
        "region_state": "Region/State",
        "preferences": "Crop Preferences",
        "additional_info": "Additional Information",
        "get_ai_recommendation": "Get AI Recommendation",
        "quick_questions": "💬 Quick Questions",
        "fertilizer_guide_header": "🧪 Fertilizer Recommendation Guide",
        "select_crop_fertilizer": "Select Crop",
        "current_n": "Current Nitrogen (N) level (kg/ha)",
        "current_p": "Current Phosphorus (P) level (kg/ha)",
        "current_k": "Current Potassium (K) level (kg/ha)",
        "land_area_fertilizer": "Land Area (acres)",
        "fertilizer_budget": "Fertilizer Budget (Rs)",
        "get_fertilizer_recommendations": "Get Fertilizer Recommendations",
        "fertilizer_recommendations": "Fertilizer Recommendations:",
        "application_guidelines": "Application Guidelines",
        "footer_text": "Made with ❤️ for Indian Farmers | KrishiMitra AI",
        "data_sources": "Data sources: Soil Health Card, AgMarkNet, ICRISAT, FAO, OpenWeather",
        "support_contact": "For support: contact@krishimitrai.com",
        "create_profile": "Create Farmer Profile",
        "farmer_type": "Type of Farmer",
        "experience": "Years of Farming Experience",
        "irrigation_type": "Irrigation Type",
        "create_profile_btn": "Create Profile",
        "profile_saved": "Profile saved successfully!",
        "connect_officer": "Connect with Agricultural Officer",
        "community_advice": "Community Advice",
        "share_advice": "Share Your Advice",
        "read_aloud": "🔊 Read Aloud",
        "government_schemes": "Government Schemes",
        "available_schemes": "Available Schemes for You",
        "offline_mode": "Offline Mode",
        "download_data": "Download Essential Data",
        "offline_data_available": "Offline data available for basic recommendations"
    },
    "Hindi": {
        "main_header": "कृषिमित्र AI",
        "sub_header": "भारतीय किसानों के लिए बुद्धिमान फसल सिफारिशें",
        "language_settings": "भाषा सेटिंग्स",
        "select_language": "भाषा चुनें",
        "feedback": "प्रतिक्रिया",
        "provide_feedback": "प्रतिक्रिया दें",
        "share_experience": "अपना अनुभव साझा करें",
        "rate_experience": "अपने अनुभव को रेट करें (1-5)",
        "additional_comments": "अतिरिक्त टिप्पणियाँ",
        "submit_feedback": "प्रतिक्रिया सबमिट करें",
        "thank_you_feedback": "आपकी प्रतिक्रिया के लिए धन्यवाद!",
        "get_recommendations": "सिफारिशें प्राप्त करें",
        "crop_calendar": "फसल कैलेंडर",
        "crop_diseases": "फसल रोग",
        "farming_guidelines": "कृषि दिशानिर्देश",
        "ai_assistant": "AI सहायक",
        "crop_recommendation_ai": "AI द्वारा फसल सिफारिश",
        "fertilizer_guide": "उर्वरक गाइड",
        "government_schemes": "सरकारी योजनाएं",
        "community": "समुदाय",
        "farmer_profile": "किसान प्रोफाइल",
        "smart_crop_recommendation": "🔍 मौसम और मिट्टी के आधार पर स्मार्ट फसल सिफारिश",
        "enter_pin_code": "अपना पिन कोड दर्ज करें",
        "pin_help": "6-अंकीय भारतीय पिन कोड",
        "land_area": "जमीन का क्षेत्रफल (एकड़)",
        "budget": "बजट (Rs)",
        "soil_parameters": "🔍 मिट्टी के पैरामीटर",
        "nitrogen": "नाइट्रोजन (N) स्तर",
        "phosphorus": "फॉस्फोरस (P) स्तर",
        "potassium": "पोटैशियम (K) स्तर",
        "soil_ph": "मिट्टी का pH",
        "get_recommendations_btn": "फसल सिफारिशें प्राप्त करें",
        "invalid_pin": "✗ कृपया एक वैध 6-अंकीय पिन कोड दर्ज करें।",
        "model_error": "✗ फसल भविष्यवाणी मॉडल उपलब्ध नहीं है।",
        "location_error": "उस पिन कोड के लिए स्थान नहीं मिल सका। कृपया जांचें और पुनः प्रयास करें।",
        "weather_error": "मौसम डेटा उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।",
        "temperature": "तापमान",
        "humidity": "नमी",
        "rainfall": "बारिश (पूर्वानुमान योग)",
        "weather_alerts": "मौसम चेतावनियाँ:",
        "analysis_complete": "✔ पिन {pin_code} के लिए विश्लेषण पूर्ण: यहाँ आपके सर्वोत्तम फसल विकल्प हैं:",
        "specifically_for": "यह फसल सिफारिश विशेष रूप से पिन {pin_code} के लिए है",
        "specifically_suited": "विशेष रूप से उपयुक्त: {pin_code} क्षेत्र",
        "your_land_area": "आपका जमीन क्षेत्र: {land_area} एकड़",
        "financial_overview": "वित्तीय अवलोकन",
        "expected_roi": "अपेक्षित आय (राजस्व)",
        "profit_potential": "लाभ क्षमता",
        "investment_needed": "आवश्यक निवेश",
        "per_acre_cost": "प्रति एकड़ लागत",
        "market_demand": "बाजार मांग",
        "price_trend": "मूल्य प्रवृत्ति",
        "market_information": "बाजार जानकारी",
        "market_price_range": "बाजार मूल्य सीमा",
        "growth_timeline": "विकास समयरेखा",
        "time_to_harvest": "कटाई का समय",
        "resilience_score": "लचीलापन स्कोर",
        "best_sowing_window": "सर्वोत्तम बुवाई विंडो",
        "critical_months": "महत्वपूर्ण महीने",
        "weather_suitability": "मौसम उपयुक्तता",
        "cultivation_guidelines": "खेती दिशानिर्देश",
        "best_practices": "सर्वोत्तम अभ्यास",
        "things_to_avoid": "बचने के लिए चीजें",
        "download_pdf": "📄 विस्तृत PDF रिपोर्ट डाउनलोड करें",
        "monthly_crop_calendar": "📅 मासिक फसल कैलेंडर",
        "current_month": "वर्तमान महीना: {current_month}",
        "select_month": "देखने के लिए महीना चुनें:",
        "crop_disease_identification": "🦠 फसल रोग पहचान और प्रबंधन",
        "disease_help": "यह अनुभाग आपको सामान्य फसल रोगों, उनके लक्षणों और प्रभावी प्रबंधन रणनीतियों को पहचानने में मदद करता है। सामान्य रोगों और अनुशंसित उपचारों को देखने के लिए एक फसल चुनें।",
        "select_crop": "एक फसल चुनें:",
        "common_diseases": "{crop} में सामान्य रोग",
        "symptoms": "🔍 लक्षण",
        "common_season": "🔍 सामान्य मौसम",
        "prevention": "🔍 रोकथाम",
        "treatment": "🔍 उपचार",
        "general_prevention_tips": "🔍 सामान्य रोग रोकथाम युक्तियाँ",
        "cultural_practices": "🌱 सांस्कृतिक प्रथाएं",
        "water_management": "💧 जल प्रबंधन",
        "chemical_management": "🧪 रासायनिक प्रबंधन",
        "ai_disease_detection": "🤖 AI रोग पहचान",
        "ai_disease_help": "AI-सहायित निदान के लिए प्रभावित पौधे के हिस्से की छवि अपलोड करें",
        "choose_image": "एक छवि चुनें...",
        "analyze_image": "छवि विश्लेषण",
        "analyzing": "रोग पैटर्न के लिए छवि का विश्लेषण...",
        "analysis_complete_disease": "विश्लेषण पूर्ण",
        "detected_disease": "पता चला रोग:",
        "farming_best_practices": "📖 कृषि सर्वोत्तम अभ्यास और दिशानिर्देश",
        "ai_assistant_header": "🤖 कृषिमित्र AI सहायक",
        "ai_assistant_help": "कृषि, फसलों, मौसम, मिट्टी या किसी भी कृषि विषय के बारे में कुछ भी पूछें। मैं आपकी कृषि संबंधी प्रश्नों में मदद करने और विशेषज्ञ सलाह प्रदान करने के लिए यहां हूं।",
        "chat_with_ai": "💬 कृषिमित्र AI से चैट करें",
        "voice_input": "🎤 वॉइस इनपुट",
        "type_question": "अपना कृषि प्रश्न यहाँ टाइप करें:",
        "send_message": "संदेश भेजें",
        "clear_chat": "चैट साफ़ करें",
        "read_last": "🔊 अंतिम पढ़ें",
        "ai_thinking": "कृषिमित्र AI सोच रहा है...",
        "suggested_questions": "💡 सुझाए गए प्रश्न",
        "ai_powered_recommendation": "🤖 AI-संचालित फसल सिफारिश",
        "ai_crop_help": "AI का उपयोग करके अपनी विशिष्ट परिस्थितियों के आधार पर व्यक्तिगत फसल सिफारिशें प्राप्त करें। अपनी मिट्टी, जलवायु और प्राथमिकताओं का वर्णन करें, और हमारा AI आपके लिए सर्वोत्तम फसलों का सुझाव देगा。",
        "ai_crop_chat": "💬 AI फसल सिफारिश चैट",
        "tell_conditions": "💬 हमें अपनी कृषि परिस्थितियों के बारे में बताएं",
        "soil_type": "मिट्टी का प्रकार",
        "climate": "जलवायु",
        "water_availability": "पानी की उपलब्धता",
        "region_state": "क्षेत्र/राज्य",
        "preferences": "फसल प्राथमिकताएं",
        "additional_info": "अतिरिक्त जानकारी",
        "get_ai_recommendation": "AI सिफारिश प्राप्त करें",
        "quick_questions": "💬 त्वरित प्रश्न",
        "fertilizer_guide_header": "🧪 उर्वरक सिफारिश गाइड",
        "select_crop_fertilizer": "फसल चुनें",
        "current_n": "वर्तमान नाइट्रोजन (N) स्तर (किग्रा/हेक्टेयर)",
        "current_p": "वर्तमान फॉस्फोरस (P) स्तर (किग्रा/हेक्टेयर)",
        "current_k": "वर्तमान पोटैशियम (K) स्तर (किग्रा/हेक्टेयर)",
        "land_area_fertilizer": "जमीन का क्षेत्रफल (एकड़)",
        "fertilizer_budget": "उर्वरक बजट (Rs)",
        "get_fertilizer_recommendations": "उर्वरक सिफारिशें प्राप्त करें",
        "fertilizer_recommendations": "उर्वरक सिफारिशें:",
        "application_guidelines": "आवेदन दिशानिर्देश",
        "footer_text": "भारतीय किसानों के लिए ❤️ के साथ बनाया गया | कृषिमित्र AI",
        "data_sources": "डेटा स्रोत: मृदा स्वास्थ्य कार्ड, AgMarkNet, ICRISAT, FAO, OpenWeather",
        "support_contact": "समर्थन के लिए: contact@krishimitrai.com",
        "create_profile": "किसान प्रोफाइल बनाएं",
        "farmer_type": "किसान का प्रकार",
        "experience": "कृषि अनुभव (वर्ष)",
        "irrigation_type": "सिंचाई का प्रकार",
        "create_profile_btn": "प्रोफाइल बनाएं",
        "profile_saved": "प्रोफाइल सफलतापूर्वक सहेजी गई!",
        "connect_officer": "कृषि अधिकारी से जुड़ें",
        "community_advice": "समुदाय सलाह",
        "share_advice": "अपनी सलाह साझा करें",
        "read_aloud": "🔊 जोर से पढ़ें",
        "government_schemes": "सरकारी योजनाएं",
        "available_schemes": "आपके लिए उपलब्ध योजनाएं",
        "offline_mode": "ऑफलाइन मोड",
        "download_data": "आवश्यक डेटा डाउनलोड करें",
        "offline_data_available": "मूल सिफारिशों के लिए ऑफलाइन डेटा उपलब्ध"
    }
}

# Initialize session state for language if not exists 
if "language" not in st.session_state: 
    st.session_state.language = "English"

# Initialize session state for new features
if "farmer_profile" not in st.session_state:
    st.session_state.farmer_profile = None

if "community_advice" not in st.session_state:
    st.session_state.community_advice = []

if "offline_data" not in st.session_state:
    st.session_state.offline_data = None

# Helper function to get translation 
def t(key): 
    lang = st.session_state.language 
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key) 

st.markdown(
    f"<div class='km-hero'><h1 class='main-header'>🌱 {t('main_header')}</h1>"
    f"<p class='sub-header'>{t('sub_header')}</p></div>",
    unsafe_allow_html=True,
)

# Paths & Constants
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" if (BASE_DIR / "data").is_dir() else BASE_DIR
IMAGES_DIR = BASE_DIR.parent / "images"
MODEL_PATH = BASE_DIR / "crop_model.pkl"

if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR.parent / "crop_model.pkl"

# API keys
API_KEY = None

try:
    API_KEY = st.secrets.get("OPENWEATHER_API_KEY", None)
except Exception:
    API_KEY = None

if not API_KEY:
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    st.error("Missing OpenWeather API key. Set OPENWEATHER_API_KEY in st.secrets or as an environment variable.")
    st.stop()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Language settings
languages = {
    "English": {"code": "en", "name": "English"},
    "Hindi": {"code": "hi", "name": "Hindi"},
    "Gujarati": {"code": "gu", "name": "Gujarati"},
    "Marathi": {"code": "mr", "name": "Marathi"}
}

# Translation function
def translate_text(text, target_lang):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except:
        return text  # Fallback to English if translation fails

# Load datasets
@st.cache_data
def load_crop_yield_data():
    """Load crop yield data from CSV"""
    try:
        crop_yield_path = DATA_DIR / "crop_yield.csv"
        if crop_yield_path.exists():
            df = pd.read_csv(crop_yield_path)
            return df
        else:
            # st.warning("Crop yield data not found. Using default values.")
            return None
    except Exception as e:
        st.error(f"Error loading crop yield data: {e}")
        return None

@st.cache_data
def load_pincode_data():
    """Load pincode data from CSV"""
    try:
        pincode_path = DATA_DIR / "pincodes.csv"
        if pincode_path.exists():
            df = pd.read_csv(pincode_path)
            return df
        else:
            # st.warning("Pincode data not found. Using default values.")
            return None
    except Exception as e:
        st.error(f"Error loading pincode data: {e}")
        return None

@st.cache_data
def load_regional_crop_data():
    """Load regional crop data from JSON"""
    try:
        regional_data_path = DATA_DIR / "regional_crop_data.json"
        if regional_data_path.exists():
            with open(regional_data_path, 'r') as f:
                return json.load(f)
        else:
            # st.warning("Regional crop data not found. Using default values.")
            return None
    except Exception as e:
        st.error(f"Error loading regional crop data: {e}")
        return None

@st.cache_data
def load_static_prices():
    """Load static prices from CSV"""
    try:
        static_prices_path = DATA_DIR / "static_prices.csv"
        if static_prices_path.exists():
            df = pd.read_csv(static_prices_path)
            return df
        else:
            # st.warning("Static prices data not found. Using default values.")
            return None
    except Exception as e:
        st.error(f"Error loading static prices data: {e}")
        return None

@st.cache_data
def load_cod_yield_data():
    """Load COD yield data from CSV"""
    try:
        cod_yield_path = DATA_DIR / "COD_Yield.csv"
        if cod_yield_path.exists():
            df = pd.read_csv(cod_yield_path)
            return df
        else:
            # st.warning("COD yield data not found. Using default values.")
            return None
    except Exception as e:
        st.error(f"Error loading COD yield data: {e}")
        return None

# Load all datasets
crop_yield_df = load_crop_yield_data()
pincode_df = load_pincode_data()
regional_crop_data = load_regional_crop_data()
static_prices_df = load_static_prices()
cod_yield_df = load_cod_yield_data()

# Expanded Crop Diseases Database
CROP_DISEASES = {
    "Rice": [
        {
            "name": "Blast",
            "symptoms": "Spindle-shaped spots with gray centers and brown margins on leaves",
            "season": "Wet season",
            "prevention": ["Use resistant varieties", "Avoid excessive nitrogen"],
            "treatment": ["Apply fungicides like tricyclazole", "Use biological controls"]
        },
        {
            "name": "Brown Spot",
            "symptoms": "Small, circular to oval brown spots on leaves",
            "season": "High humidity conditions",
            "prevention": ["Use disease-free seeds", "Maintain proper plant spacing"],
            "treatment": ["Apply fungicides like carbendazim", "Remove infected plants"]
        }
    ],
    "Wheat": [
        {
            "name": "Rust",
            "symptoms": "Small, round, yellow-orange pustules on leaves and stems",
            "season": "Cool, moist weather",
            "prevention": ["Use resistant varieties", "Practice crop rotation"],
            "treatment": ["Apply fungicides", "Remove infected plant debris"]
        },
        {
            "name": "Karnal Bunt",
            "symptoms": "Partial bunting of grains with fishy odor",
            "season": "Flowering to grain filling stage",
            "prevention": ["Use certified seeds", "Avoid late sowing"],
            "treatment": ["Seed treatment with fungicides", "Solarization of soil"]
        }
    ],
    "Cotton": [
        {
            "name": "Boll Rot",
            "symptoms": "Water-soaked lesions on bolls turning black",
            "season": "High rainfall periods",
            "prevention": ["Avoid waterlogging", "Maintain proper plant spacing"],
            "treatment": ["Spray with copper-based fungicides", "Remove infected bolls"]
        }
    ],
    "Sugarcane": [
        {
            "name": "Red Rot",
            "symptoms": "Reddish internal discoloration of stalks",
            "season": "Warm, humid conditions",
            "prevention": ["Use disease-free setts", "Practice crop rotation"],
            "treatment": ["Rogue out infected plants", "Hot water treatment of setts"]
        }
    ]
}

# Crop-specific NPK targets for fertilizer recommendations
CROP_NPK_TARGETS = {
    "Rice": {"N": 150, "P": 60, "K": 40},
    "Wheat": {"N": 120, "P": 50, "K": 60},
    "Cotton": {"N": 200, "P": 60, "K": 80},
    "Sugarcane": {"N": 250, "P": 80, "K": 100},
}

# Government schemes database
# National schemes available across India. Benefit rates for state-run components vary,
# so no state-specific percentages are hard-coded here - farmers should confirm locally.
GOVERNMENT_SCHEMES = [
    {"name": "PM-KISAN", "description": "Income support of ₹6,000 per year, paid in three installments of ₹2,000.",
     "eligibility": "Landholding farmer families, subject to the scheme's exclusion criteria", "link": "https://pmkisan.gov.in"},
    {"name": "PM Fasal Bima Yojana (PMFBY)", "description": "Crop insurance against yield loss from natural calamities, pests and diseases, with low fixed farmer premiums (2% Kharif, 1.5% Rabi, 5% commercial/horticulture crops).",
     "eligibility": "Farmers growing notified crops in notified areas", "link": "https://pmfby.gov.in"},
    {"name": "Kisan Credit Card (KCC)", "description": "Short-term bank credit for seeds, fertilizer and other cultivation costs, with interest subvention for timely repayment.",
     "eligibility": "Farmers, tenant farmers and sharecroppers", "link": "https://www.myscheme.gov.in"},
    {"name": "Soil Health Card", "description": "Free soil testing with crop-wise nutrient and fertilizer recommendations.",
     "eligibility": "All farmers", "link": "https://soilhealth.dac.gov.in"},
    {"name": "PM-KUSUM", "description": "Support for solar irrigation pumps and solar power on farms. Subsidy levels vary by state.",
     "eligibility": "Farmers wanting solar pumps; check your state agency", "link": "https://pmkusum.mnre.gov.in"},
    {"name": "PMKSY - Per Drop More Crop", "description": "Subsidy for drip and sprinkler irrigation. Rates vary by state and farmer category.",
     "eligibility": "Farmers adopting micro-irrigation; check your state agriculture department", "link": "https://pmksy.gov.in"},
    {"name": "e-NAM", "description": "Online national market to sell produce and see prices from many mandis.",
     "eligibility": "Farmers selling through registered mandis", "link": "https://enam.gov.in"},
]

# Real national helplines and portals (replaces the earlier placeholder officer list)
FARMER_HELPLINES = [
    {"name": "Kisan Call Centre", "contact": "1800-180-1551 (toll-free)", "about": "Free advice on crops, pests, weather and schemes in local languages"},
    {"name": "PM-KISAN Helpline", "contact": "155261 / 011-24300606", "about": "Payment and registration queries"},
    {"name": "Crop Insurance Helpline (PMFBY)", "contact": "14447", "about": "Claims and enrolment for crop insurance"},
    {"name": "Krishi Vigyan Kendra (KVK) locator", "contact": "https://kvk.icar.gov.in", "about": "Find the farm science centre for your district for training and soil testing"},
]

# Utilities
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
        st.warning("Images folder not found.")
        return

    base = crop_name.lower().replace(' ', '')
    for ext in (".jpg", ".jpeg", ".png"):
        test_path = IMAGES_DIR / (base + ext)
        if test_path.exists():
            try:
                img = Image.open(test_path)
                st.image(img, caption=crop_name, width=300)
                return
            except Exception as e:
                logger.warning(f"Image error for {crop_name}: {e}")
                break

    create_crop_placeholder(crop_name)

def create_crop_placeholder(crop_name: str):
    """Create a styled placeholder for missing crop images"""
    crop_themes = {
        'blackgram': {'color': '#AAAAAA', 'bg': '#F5F5F5', 'emoji': '🌱', 'desc': 'Black Lentil'},
        'chickpea': {'color': '#D2691E', 'bg': '#FFFF8D', 'emoji': '🌱', 'desc': 'Chickpea/Gram'},
        'cotton': {'color': '#FFE4E1', 'bg': '#FFFFFF', 'emoji': '🌱', 'desc': 'Cotton Plant'},
        'lentil': {'color': '#CD853F', 'bg': '#FFFF8D', 'emoji': '🌱', 'desc': 'Red Lentils'},
        'mango': {'color': '#FFD700', 'bg': '#FFFFAF', 'emoji': '🌳', 'desc': 'Mango Tree'},
        'mothbeans': {'color': '#BB4513', 'bg': '#F5DEB3', 'emoji': '🌱', 'desc': 'Moth Beans'},
        'mungbean': {'color': '#228B22', 'bg': '#F0FFF0', 'emoji': '🌱', 'desc': 'Mung Bean'},
        'muskmelon': {'color': '#FA500', 'bg': '#FFFACD', 'emoji': '🍈', 'desc': 'Muskmelon'},
        'pigeonpeas': {'color': '#DA4520', 'bg': '#FFFFAF', 'emoji': '🌱', 'desc': 'Pigeon Peas'},
        'rice': {'color': '#F5F5DC', 'bg': '#FFFFF0', 'emoji': '🌾', 'desc': 'Rice Plantation'},
        'wheat': {'color': '#F5DEB3', 'bg': '#FFFFAF', 'emoji': '🌾', 'desc': 'Wheat Field'}
    }

    theme = crop_themes.get(crop_name.lower(), {'color': '#2E8B57', 'bg': '#F0FFF0', 'emoji': '🌱', 'desc': 'Agricultural Crop'})

    placeholder_html = f"""
    <div style="width: 300px; height: 200px; background: linear-gradient(135deg, {theme['bg']} 0%, {theme['color']}20 100%); border: 2px solid {theme['color']}; border-radius: 15px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 10px 0;">
        <div style="font-size: 48px; margin-bottom: 10px;">{theme['emoji']}</div>
        <div style="font-size: 18px; font-weight: bold; color: {theme['color']}; margin-bottom: 5px;">{crop_name.title()}</div>
        <div style="font-size: 14px; color: {theme['color']}80; font-style: italic;">{theme['desc']}</div>
        <div style="font-size: 12px; color: {theme['color']}60; margin-top: 8px;">Crop Placeholder</div>
    </div>
    """

    st.markdown(placeholder_html, unsafe_allow_html=True)

def fmt_money(val: float) -> str:
    """Format currency (INR) nicely."""
    try:
        return f"Rs{val:.0f}"
    except Exception:
        return "Rs0"

def load_pin_database():
    """Load a local database of PIN codes with coordinates."""
    pin_db = {}
    try:
        if pincode_df is not None:
            for _, row in pincode_df.iterrows():
                pin = str(row['Pincode']).strip()
                if len(pin) == 6 and pin.isdigit():
                    pin_db[pin] = {
                        'lat': row['Latitude'],
                        'lon': row['Longitude'],
                        'district': row['District'],
                        'state': row['StateName']
                    }
        else:
            # Fallback to manual database if CSV not available
            pin_db = {
                "395007": {"lat": 21.2292, "lon": 72.8333, "district": "Surat", "state": "Gujarat"},
                "110001": {"lat": 28.6139, "lon": 77.2090, "district": "New Delhi", "state": "Delhi"},
                "600001": {"lat": 13.0827, "lon": 80.2707, "district": "Chennai", "state": "Tamil Nadu"},
                "700001": {"lat": 22.5726, "lon": 88.3639, "district": "Kolkata", "state": "West Bengal"},
                "500001": {"lat": 17.3850, "lon": 78.4867, "district": "Hyderabad", "state": "Telangana"}
            }
    except Exception as e:
        logger.error(f"Failed to load PIN database: {e}")
    
    return pin_db

def get_lat_lon(pin: str):
    """Resolve lat/lon from Indian PIN code with better validation."""
    if not pin or len(pin) != 6 or not pin.isdigit():
        return None, None, None

    # First try OpenWeather API
    url = f"https://api.openweathermap.org/geo/1.0/zip?zip={pin},IN&appid={API_KEY}"
    data = http_get_json(url)
    
    if data and "lat" in data and "lon" in data:
        lat = data.get("lat")
        lon = data.get("lon")
        place_name = data.get("name", "")
        
        try:
            return float(lat), float(lon), place_name
        except Exception:
            pass
    
    # Fallback to a local PIN code database
    pin_db = load_pin_database()
    if pin in pin_db:
        return pin_db[pin]['lat'], pin_db[pin]['lon'], pin_db[pin]['district']
    
    return None, None, None

def generate_weather_alerts(temp, humidity, rainfall):
    """Generate more accurate and region-specific weather alerts."""
    alerts = []
    
    # Temperature alerts
    if temp > 38:
        alerts.append("Extreme heat warning: Consider shade nets, increase irrigation frequency, and irrigate during evening hours.")
    elif temp > 35:
        alerts.append("High temperature alert: Increase irrigation and consider using shade nets for sensitive crops.")
    elif temp < 5:
        alerts.append("Frost warning: Protect sensitive crops with covers or mulch. Consider irrigation to raise ambient temperature.")
    elif temp < 10:
        alerts.append("Low temperature alert: Protect seedlings and sensitive crops from cold stress.")
    
    # Rainfall alerts
    if rainfall > 100:
        alerts.append("Heavy rainfall expected: Ensure proper drainage, postpone fertilizer application, and prepare for potential waterlogging.")
    elif rainfall > 50:
        alerts.append("Moderate to heavy rainfall expected: Check drainage systems and postpone pesticide application.")
    elif rainfall < 5 and humidity < 40:
        alerts.append("Dry conditions: Irrigation recommended. Consider water conservation techniques like mulching.")
    
    # Humidity alerts
    if humidity > 85:
        alerts.append("High humidity: Increased risk of fungal diseases. Monitor crops closely and consider preventive fungicide application.")
    elif humidity < 30:
        alerts.append("Low humidity: Increased evaporation rate. More frequent irrigation may be needed.")
    
    return alerts

def get_weather_with_alerts(lat: float, lon: float, max_retries=3):
    """Get weather summary with alerts with retry mechanism."""
    if lat is None or lon is None:
        return None, None, None, []

    for attempt in range(max_retries):
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            data = http_get_json(url)
            if not data or "list" not in data:
                if attempt == max_retries - 1:
                    return None, None, None, []
                time.sleep(2)  # Wait before retrying
                continue

            temps, hums, rains = [], [], []
            for entry in data["list"][:12]:  # Use only first 12 forecasts (36 hours)
                main = entry.get("main", {})
                temps.append(main.get("temp", 0.0))
                hums.append(main.get("humidity", 0.0))

                rain = entry.get("rain", {})
                if isinstance(rain, dict):
                    rains.append(rain.get("3h", 0.0))
                else:
                    rains.append(0.0)

            # Calculate weighted average giving more importance to recent forecasts
            weights = [i+1 for i in range(len(temps))]  # Linear weights
            total_weight = sum(weights)
            
            temp_avg = sum(t * w for t, w in zip(temps, weights)) / total_weight
            hum_avg = sum(h * w for h, w in zip(hums, weights)) / total_weight
            rain_total = sum(rains)  # Total forecasted rain

            # Generate more accurate weather alerts
            alerts = generate_weather_alerts(temp_avg, hum_avg, rain_total)
            
            return temp_avg, hum_avg, rain_total, alerts
            
        except Exception as e:
            logger.error(f"Weather API attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                return None, None, None, []
            time.sleep(2)  # Wait before retrying
    
    return None, None, None, []

def get_typical_monthly_rainfall(pin: str, default: float = 100.0) -> float:
    """Typical monthly rainfall (mm) for the PIN's state: mean annual rainfall / 12.

    The crop model was trained on monthly-scale rainfall (20-300 mm), so it must not be fed the
    36-hour forecast total, which is close to 0 for most of the year.
    """
    try:
        info = load_pin_database().get(str(pin))
        if info is None or crop_yield_df is None:
            return default
        states = crop_yield_df["State"].astype(str).str.strip().str.lower()
        rain = crop_yield_df.loc[states == str(info["state"]).strip().lower(), "Annual_Rainfall"]
        if rain.empty:
            return default
        return float(min(max(rain.mean() / 12.0, 20.0), 300.0))
    except Exception as e:
        logger.warning(f"Typical rainfall lookup failed: {e}")
        return default

def with_loading(message, func, *args, **kwargs):
    """Execute a function with a loading spinner."""
    with st.spinner(message):
        return func(*args, **kwargs)

# AI Chatbot Functions
def render_chat(history, empty_hint="Ask a question below to get started."):
    """Render a chat history with native chat bubbles (markdown-safe)."""
    if not history:
        st.caption(empty_hint)
        return
    for message in history:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👨‍🌾"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🌱"):
                st.markdown(message["content"])

def _language_instruction():
    """Extra prompt line so the AI replies in the language chosen in the sidebar."""
    lang = st.session_state.get("language", "English")
    return "" if lang == "English" else f"\nReply in {lang} (use its native script), keeping crop names easy to understand.\n"

def query_gemini(prompt):
    """Send a query to the Gemini API and return the response."""
    if not gemini_api_key:
        return "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable."

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt + _language_instruction())
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error while processing your request: {str(e)}"

def format_chat_response(response_text):
    """Format the chatbot response to make it more farmer-friendly."""
    if "chat_history" not in st.session_state or len(st.session_state.chat_history) == 0:
        greeting = "Namaskar! I am KrishiMitra AI, your farming assistant. How can I help you with your farming questions today?\n\n"
        return greeting + response_text
    return response_text

def get_gemini_crop_recommendation(user_query, context=""):
    """Get crop recommendation from Gemini with agricultural context."""
    if not gemini_api_key:
        return "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable."

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        system_prompt = f"""
        You are KrishiMitra AI, an expert farming assistant for Indian farmers specializing in crop recommendations.
        Provide helpful, practical, and accurate advice about crop selection, farming techniques, and agricultural best practices.

        Context: {context}

        Guidelines:
        - Focus on Indian agricultural practices and conditions
        - Recommend crops suitable for different regions of India
        - Consider soil type, climate, and water availability
        - Suggest crops with good market potential and profitability
        - Recommend sustainable and organic farming practices when appropriate
        - Mention specific varieties suitable for Indian conditions
        - Include planting schedules and cultivation tips
        - Be concise but comprehensive
        - Use metric units and Indian currency (Rs)

        If the question is not related to agriculture, politely redirect to farming topics.
        """

        full_prompt = f"{system_prompt}{_language_instruction()}\n\nFarmer's question: {user_query}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Error connecting to AI service: {str(e)}. Please try again later."

# Market price function - using AgMarkNet API
def get_market_prices(crop_name, state=None, district=None):
    """Fetch real market prices from AgMarkNet API (data.gov.in)."""

    API_KEY = os.getenv("AGMARKNET_API_KEY")  # saved in your .env
    RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Daily market prices dataset

    if not API_KEY:
        logger.info("AGMARKNET_API_KEY not set; using local price data")
        return None

    # Build query params
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 5,  # get top 5 records
    }
    if crop_name:
        params["filters[commodity]"] = crop_name
    if state:
        params["filters[state]"] = state
    if district:
        params["filters[district]"] = district

    url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
    data = http_get_json(url + "?" + "&".join([f"{k}={v}" for k, v in params.items()]))

    if not data or "records" not in data:
        return {"min": 0, "max": 0, "trend": "unknown"}

    prices = []
    for rec in data["records"]:
        try:
            modal_price = float(rec.get("modal_price", 0))
            prices.append(modal_price)
        except:
            continue

    if not prices:
        return {"min": 0, "max": 0, "trend": "unknown"}

    return {
        "min": min(prices),
        "max": max(prices),
        "trend": "stable"  # TODO: can compute trend if comparing last 7 days
    }

def _get_govt_prices(crop_name, state=None, district=None):
    """Get prices from alternative government API."""
    # Implementation for another API
    return {"min": 0, "max": 0, "trend": "unknown"}

# Model crop label -> commodity name(s) in static_prices.csv (exact names)
_PRICE_ALIASES = {
    "rice": ["Rice", "Paddy(Dhan)(Common)"], "chickpea": ["Bengal Gram(Gram)(Whole)"],
    "blackgram": ["Black Gram (Urd Beans)(Whole)"], "mungbean": ["Green Gram (Moong)(Whole)"],
    "lentil": ["Lentil (Masur)(Whole)"], "pigeonpeas": ["Arhar (Tur/Red Gram)(Whole)"],
    "mothbeans": ["Moath Dal"], "muskmelon": ["Karbuja(Musk Melon)"],
    "coconut": ["Coconut"], "grapes": ["Grapes"], "mango": ["Mango"], "banana": ["Banana"],
}
_HARDCODED_PRICES = {
    "rice": (1800, 2200, "stable"), "wheat": (1900, 2100, "rising"), "cotton": (5500, 6000, "stable"),
}

def _get_static_prices(crop_name, state=None, district=None):
    """Get prices (Rs/quintal) from the local mandi price CSV, with a small hardcoded fallback."""
    key = str(crop_name).lower()
    if static_prices_df is not None:
        try:
            names = [n.lower() for n in _PRICE_ALIASES.get(key, [key])]
            rows = static_prices_df[static_prices_df['Commodity'].str.lower().isin(names)]
            if state and not rows.empty:
                in_state = rows[rows['State'].str.lower() == str(state).lower()]
                if not in_state.empty:
                    rows = in_state
            if not rows.empty:
                lo = pd.to_numeric(rows['Min_x0020_Price'], errors='coerce').median()
                hi = pd.to_numeric(rows['Max_x0020_Price'], errors='coerce').median()
                if pd.notna(lo) and pd.notna(hi) and hi > 0:
                    return {"min": int(lo), "max": int(hi), "trend": "stable"}
        except Exception as e:
            logger.error(f"Error reading static prices: {e}")

    if key in _HARDCODED_PRICES:
        lo, hi, tr = _HARDCODED_PRICES[key]
        return {"min": lo, "max": hi, "trend": tr}
    return {"min": 0, "max": 0, "trend": "unknown"}

def get_real_time_market_prices(crop_name, state=None, district=None):
    """Fetch real market prices with multiple fallback sources."""
    prices = None
    
    # Try AgMarkNet first
    try:
        prices = get_market_prices(crop_name, state, district)
        if prices and prices['max'] > 0:
            return prices
    except Exception as e:
        logger.warning(f"AgMarkNet failed: {e}")
    
    # Fallback to government API
    try:
        prices = _get_govt_prices(crop_name, state, district)
        if prices and prices['max'] > 0:
            return prices
    except Exception as e:
        logger.warning(f"Government API failed: {e}")
    
    # Final fallback to static data
    return _get_static_prices(crop_name, state, district)

# New functions for enhanced features
def load_regional_crop_data():
    """Load regional crop suitability data."""
    if regional_crop_data is not None:
        return regional_crop_data
    
    # Fallback to hardcoded data if JSON not available
    return {
        'north': {
            'Wheat': {'productivity_factor': 1.2, 'profit_factor': 1.1, 
                     'regional_tips': ['Sow in well-drained clay loam soil', 'Use timely irrigation'],
                     'regional_warnings': ['Avoid late sowing']},
            'Rice': {'productivity_factor': 0.9, 'profit_factor': 0.95,
                    'regional_tips': ['Use SRI method for better yield'],
                    'regional_warnings': ['Ensure proper water management']}
        },
        'south': {
            'Rice': {'productivity_factor': 1.3, 'profit_factor': 1.2,
                    'regional_tips': ['Ideal for coastal regions', 'Use salt-tolerant varieties'],
                    'regional_warnings': ['Monitor for blast disease']},
            'Cotton': {'productivity_factor': 1.1, 'profit_factor': 1.05,
                      'regional_tips': ['Use drip irrigation for water efficiency'],
                      'regional_warnings': ['Watch for bollworm infestation']}
        }
    }

def get_region_from_pin(pin_code):
    """Get region from PIN code (simplified implementation)."""
    # In a real implementation, this would use a geocoding API or database
    # For now, we'll use a simple mapping based on the first digit
    first_digit = pin_code[0] if pin_code else '0'
    
    region_map = {
        '1': 'north',  # Delhi, Haryana, Punjab, etc.
        '2': 'north',  # Uttar Pradesh, Uttarakhand
        '3': 'west',   # Rajasthan, Gujarat
        '4': 'west',   # Maharashtra, Goa
        '5': 'south',  # Andhra Pradesh, Karnataka
        '6': 'south',  # Kerala, Tamil Nadu
        '7': 'east',   # West Bengal, Odisha
        '8': 'east',   # Bihar, Jharkhand
        '0': 'north'   # Fallback
    }
    
    return region_map.get(first_digit, 'north')

def adjust_for_soil_conditions(crop, soil_params):
    """Adjust recommendations based on soil conditions."""
    n, p, k, ph = soil_params
    name = str(crop['name']).lower()

    if n < 30 and name in ('wheat', 'rice', 'maize', 'cotton'):
        crop['tips'].append('Soil nitrogen is low: apply extra nitrogen fertilizer in split doses')
        crop['investment'] *= 1.1
        crop['profit'] -= crop['investment'] * 0.1 / 1.1

    if p < 15 and name in ('chickpea', 'lentil', 'blackgram', 'mungbean', 'pigeonpeas', 'kidneybeans', 'mothbeans'):
        crop['tips'].append('Soil phosphorus is low: apply phosphorus-rich fertilizer at sowing')
        crop['investment'] *= 1.05
        crop['profit'] -= crop['investment'] * 0.05 / 1.05

    if ph < 5.5:
        crop['warnings'].append('Soil is acidic (pH < 5.5). Consider liming before planting.')
        crop['investment'] *= 1.15
        crop['profit'] -= crop['investment'] * 0.15 / 1.15
    elif ph > 8.0:
        crop['warnings'].append('Soil is alkaline (pH > 8). Consider gypsum or acidifying fertilizers.')
        crop['investment'] *= 1.12
        crop['profit'] -= crop['investment'] * 0.12 / 1.12

_DEFAULT_CROP_INFO = {
    "investment_per_acre": 12000, "roi_per_acre": 24000, "harvest_time": "3-5",
    "resilience": 6, "sowing_window": "Depends on region and season",
    "critical_months": "-", "price_trend": 0, "demand": "Medium",
    "weather_impact": {"Temperature": "Check suitability for your local climate",
                       "Rainfall": "Ensure adequate water availability"},
    "tips": ["Use certified seeds", "Maintain proper spacing"],
    "warnings": ["Watch for pests and disease", "Avoid waterlogging"],
}

def _build_crop_entry(name, land_area, budget, confidence=None):
    """Build one recommendation entry from CROP_DATA (or defaults)."""
    try:
        from crop_data import CROP_DATA
    except Exception:
        CROP_DATA = {}
    info = CROP_DATA.get(str(name).lower(), _DEFAULT_CROP_INFO)
    investment = info["investment_per_acre"] * land_area
    revenue = info["roi_per_acre"] * land_area
    entry = {
        "name": name,
        "roi": revenue,
        "profit": revenue - investment,
        "investment": investment,
        "demand": info.get("demand", "Medium"),
        "price_trend": info.get("price_trend", 0),
        "harvest_time": info.get("harvest_time", "3-5"),
        "resilience": f"{info.get('resilience', 6)}/10",
        "sowing_window": info.get("sowing_window", "-"),
        "critical_months": info.get("critical_months", "-"),
        "weather_impact": dict(info.get("weather_impact", {})),
        "tips": list(info.get("tips", [])),
        "warnings": list(info.get("warnings", [])),
        "confidence": confidence,
    }
    if investment > budget:
        entry["warnings"].insert(0, f"Estimated investment (₹{investment:,.0f}) exceeds your budget (₹{budget:,.0f}).")
    return entry

def _get_base_recommendations(prediction, land_area, budget, ranked=None):
    """Get base crop recommendations (top-ranked crops if model probabilities are given)."""
    if ranked:
        return [_build_crop_entry(n, land_area, budget, c) for n, c in ranked]
    return [_build_crop_entry(prediction, land_area, budget)]

def get_fallback_recommendations(prediction, land_area, budget, ranked=None):
    """Get fallback recommendations if the main function fails."""
    return _get_base_recommendations(prediction, land_area, budget, ranked)

def get_crop_recommendations(prediction, land_area, budget, pin_code, soil_params, ranked=None):
    """Get more accurate crop recommendations with regional considerations."""
    try:
        # Load regional crop suitability data
        regional_data = load_regional_crop_data()
        
        # Get region from PIN code
        region = get_region_from_pin(pin_code)
        
        # Get base recommendations
        base_recommendations = _get_base_recommendations(prediction, land_area, budget, ranked)
        
        # Adjust based on regional suitability
        for crop in base_recommendations:
            crop_name = crop['name']
            if region and crop_name in regional_data.get(region, {}):
                regional_info = regional_data[region][crop_name]
                
                # Adjust ROI based on regional productivity
                crop['roi'] = crop['roi'] * regional_info.get('productivity_factor', 1.0)
                crop['profit'] = crop['profit'] * regional_info.get('profit_factor', 1.0)
                
                # Add region-specific tips
                if 'regional_tips' in regional_info:
                    crop['tips'].extend(regional_info['regional_tips'])
                
                # Add region-specific warnings
                if 'regional_warnings' in regional_info:
                    crop['warnings'].extend(regional_info['regional_warnings'])
            
            # Adjust based on soil parameters
            adjust_for_soil_conditions(crop, soil_params)
        
        return base_recommendations
    except Exception as e:
        logger.exception("Enhanced recommendation function failed; using fallback")
        return get_fallback_recommendations(prediction, land_area, budget, ranked)

def get_government_schemes(state, farmer_category):
    """Fetch relevant government schemes for the farmer"""
    return GOVERNMENT_SCHEMES

def setup_offline_mode():
    """Cache essential data for offline use"""
    essential_data = {
        "crop_info": CROP_DISEASES,
        "fertilizer_guide": CROP_NPK_TARGETS,
        "basic_recommendations": load_basic_recommendations()
    }
    
    # Store in session state for offline access
    st.session_state.offline_data = essential_data
    st.success("Offline data downloaded successfully!")

def load_basic_recommendations():
    """Load basic recommendations for offline use"""
    return {
        "Rice": {
            "roi": 50000,
            "profit": 30000,
            "investment": 20000,
            "harvest_time": "3-4 months",
            "tips": ["Use SRI method for higher yield", "Maintain proper water level"]
        },
        "Wheat": {
            "roi": 45000,
            "profit": 25000,
            "investment": 20000,
            "harvest_time": "4-5 months",
            "tips": ["Use certified seeds", "Timely sowing is crucial"]
        }
    }

def create_farmer_profile():
    """Create or update farmer profile"""
    with st.form("farmer_profile_form"):
        st.subheader(t("create_profile"))
        
        farmer_type = st.selectbox(t("farmer_type"), 
                                  ["Small Farmer", "Marginal Farmer", "Other"])
        experience = st.slider(t("experience"), 0, 50, 5)
        irrigation_type = st.selectbox(t("irrigation_type"), 
                                      ["Rainfed", "Tube Well", "Canal", "Drip", "Other"])
        
        if st.form_submit_button(t("create_profile_btn")):
            st.session_state.farmer_profile = {
                "type": farmer_type,
                "experience": experience,
                "irrigation_type": irrigation_type
            }
            st.success(t("profile_saved"))

def connect_to_agricultural_officer():
    """Show real national helplines and how to reach the local agriculture office."""
    st.subheader(t("connect_officer"))

    pin_code = st.session_state.get('pin_code', '')
    info = load_pin_database().get(str(pin_code)) if pin_code else None
    if info:
        st.info(f"Your area: {str(info['district']).title()}, {str(info['state']).title()}. "
                "Ask the District Agriculture Officer or your nearest Krishi Vigyan Kendra (KVK) for local advice.")
    else:
        st.info("Tip: enter your PIN code in the Get Recommendations tab to see your district here.")

    for h in FARMER_HELPLINES:
        st.markdown(f"""
        <div class="government-scheme">
            <h4>{h['name']}</h4>
            <p>{h['about']}</p>
            <p><strong>Contact:</strong> {h['contact']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.caption("Numbers are national services; please verify on the official portals before sharing personal details.")

def community_advice_section():
    """Allow farmers to share advice and experiences"""
    st.subheader(t("community_advice"))
    
    # Display existing advice
    for advice in st.session_state.community_advice:
        st.markdown(f"""
        <div class="community-advice">
            <p><strong>{advice['crop']}:</strong> {advice['advice']}</p>
            <p><em>— Shared by a fellow farmer</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Form to add new advice
    with st.form("add_advice_form"):
        st.subheader(t("share_advice"))
        crop = st.selectbox("Select Crop", list(CROP_DISEASES.keys()))
        advice_text = st.text_area("Your Advice or Experience")
        if st.form_submit_button("Share Advice"):
            st.session_state.community_advice.append({
                "crop": crop,
                "advice": advice_text,
                "farmer": "Anonymous Farmer"
            })
            st.success("Thank you for sharing your experience!")

# Disease detection function (local)
def analyze_crop_disease(image, crop_type=None):
    """Analyze crop disease with enhanced accuracy and crop-specific models."""
    try:
        feature_extractor, vit_model = load_disease_model()
        if feature_extractor is None or vit_model is None:
            return "Model not loaded", 0.0
            
        # Use general model
        inputs = feature_extractor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = vit_model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()

        probs = torch.nn.functional.softmax(logits, dim=-1)
        confidence = probs[0, predicted_class_idx].item()

        return vit_model.config.id2label[predicted_class_idx], confidence
        
    except Exception as e:
        logger.error(f"Disease detection error: {e}")
        return "Unknown", 0.0

# Model & Encoder Load
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

        return model, encoder
    except Exception as e:
        logger.exception("Model load failed")
        st.error(f"Could not load model or encoder. Technical detail: {e}")
        return None, None

model, label_encoder = load_model_and_encoder()

# Sidebar with language selection and feedback
with st.sidebar:
    st.header(t("language_settings"))
    language = st.selectbox(
        t("select_language"),
        list(languages.keys()),
        index=list(languages.keys()).index(st.session_state.language)
    )
    st.session_state.language = language

    # Farmer profile section
    st.header(t("farmer_profile"))
    if st.session_state.farmer_profile:
        st.write(f"Type: {st.session_state.farmer_profile['type']}")
        st.write(f"Experience: {st.session_state.farmer_profile['experience']} years")
        st.write(f"Irrigation: {st.session_state.farmer_profile['irrigation_type']}")
        if st.button("Edit Profile"):
            st.session_state.farmer_profile = None
    else:
        create_farmer_profile()

    # Offline mode section
    st.header(t("offline_mode"))
    if st.button(t("download_data")):
        setup_offline_mode()
    
    if st.session_state.offline_data:
        st.success(t("offline_data_available"))

    st.header(t("feedback"))
    if st.button(t("provide_feedback")):
        feedback_expander = st.expander(t("share_experience"), expanded=True)
        with feedback_expander:
            rating = st.slider(t("rate_experience"), 1, 5, 4)
            comments = st.text_area(t("additional_comments"))
            if st.button(t("submit_feedback")):
                # Save feedback to a file
                import csv
                with open(BASE_DIR / "feedback.csv", "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"), rating, comments])
                st.success(t("thank_you_feedback"))

# Navigation - Added new tabs
selected_tab = option_menu(
    None,
    [t("get_recommendations"), t("crop_calendar"), t("crop_diseases"), t("farming_guidelines"),
     t("ai_assistant"), t("crop_recommendation_ai"), t("fertilizer_guide"), t("government_schemes"), t("community")],
    icons=["geo-alt", "calendar3", "bug", "journal-text", "robot", "cpu", "droplet", "bank", "people"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "6px", "background-color": "#FFFFFF", "border-radius": "16px",
                      "border": "1px solid #D5E4BF", "box-shadow": "0 2px 8px rgba(80,110,50,.10)"},
        "icon": {"font-size": "15px"},
        "nav-link": {"font-size": "13px", "text-align": "center", "margin": "2px", "border-radius": "10px",
                     "color": "#26361F", "--hover-color": "#E4F0D4"},
        "nav-link-selected": {"background-color": "#2F7D32", "color": "white", "font-weight": "700"},
    }
)

# Main application with error handling
try:
    # TAB 1: Crop Recommendation
    if selected_tab == t("get_recommendations"):
        st.header(t("smart_crop_recommendation"))
        with st.form("crop_recommendation_form"):
            col1, col2 = st.columns(2)
            with col1:
                pin_code = st.text_input(t("enter_pin_code"), max_chars=6, placeholder="e.g., 395007", help=t("pin_help"))
                land_area = st.number_input(t("land_area"), min_value=0.1, max_value=1000.0, value=1.0, step=0.1)
                budget = st.number_input(t("budget"), min_value=1000, max_value=10_000_000, value=50_000, step=1000)

            with col2:
                st.subheader(t("soil_parameters"))
                n = st.slider(t("nitrogen"), min_value=0, max_value=200, value=50)
                p = st.slider(t("phosphorus"), min_value=0, max_value=200, value=50)
                k = st.slider(t("potassium"), min_value=0, max_value=200, value=50)
                ph = st.slider(t("soil_ph"), min_value=0.0, max_value=14.0, value=6.5, step=0.1)

            submitted = st.form_submit_button(t("get_recommendations_btn"))

        if submitted:
            # Store PIN code in session state for other sections
            st.session_state.pin_code = pin_code
            
            # basic validations
            if not pin_code or len(pin_code) != 6 or not pin_code.isdigit():
                st.error(t("invalid_pin"))

            elif model is None:
                st.error(t("model_error"))

            else:
                with st.spinner("🔍 Fetching location data..."):
                    lat, lon, place_name = get_lat_lon(pin_code)

                if lat is None or lon is None:
                    st.error(t("location_error"))

                else:
                    with st.spinner("🌤️ Analyzing weather conditions..."):
                        temp, humidity, rainfall, alerts = get_weather_with_alerts(lat, lon)

                    if temp is None:
                        st.error(t("weather_error"))

                    else:
                        # Display weather information
                        weather_col1, weather_col2, weather_col3 = st.columns(3)

                        with weather_col1:
                            st.metric(t("temperature"), f"{temp:.1f}°C")

                        with weather_col2:
                            st.metric(t("humidity"), f"{humidity:.1f}%")

                        with weather_col3:
                            st.metric(t("rainfall"), f"{rainfall:.1f} mm")

                        # Display weather alerts if any
                        if alerts:
                            st.markdown("<div class='alert-box'>", unsafe_allow_html=True)
                            st.warning(t("weather_alerts"))
                            for alert in alerts:
                                st.write(f"- {alert}")
                            st.markdown("</div>", unsafe_allow_html=True)

                        # Model expects monthly-scale rainfall, not the short-term forecast
                        model_rainfall = get_typical_monthly_rainfall(pin_code)
                        st.caption(f"Crop model uses typical monthly rainfall for your state (~{model_rainfall:.0f} mm), "
                                   f"not the {rainfall:.1f} mm forecast for the next 36 hours.")

                        # Feature order used during model training - ensure exact order
                        feature_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
                        features = pd.DataFrame({
                            "N": [n], "P": [p], "K": [k],
                            "temperature": [temp], "humidity": [humidity],
                            "ph": [ph], "rainfall": [model_rainfall]
                        })[feature_order]

                        # Make prediction
                        try:
                            prediction_encoded = model.predict(features)
                            if label_encoder:
                                prediction = label_encoder.inverse_transform(prediction_encoded)[0]
                            else:
                                prediction = prediction_encoded[0]
                        except Exception as e:
                            logger.error(f"Prediction error: {e}")
                            st.error("Error making prediction. Using fallback.")
                            prediction = "Rice"  # Fallback crop

                        # Get recommendations
                        ranked = None
                        try:
                            if hasattr(model, "predict_proba") and label_encoder is not None:
                                probs = model.predict_proba(features)[0]
                                top_idx = np.argsort(probs)[::-1][:3]
                                names = label_encoder.inverse_transform(model.classes_[top_idx])
                                ranked = [(str(nm), float(probs[i])) for nm, i in zip(names, top_idx)]
                        except Exception as e:
                            logger.warning(f"Top-3 ranking unavailable: {e}")
                        recommendations = get_crop_recommendations(prediction, land_area, budget, pin_code, (n, p, k, ph), ranked)

                        # Display success message and image status
                        st.success(t("analysis_complete").format(pin_code=pin_code))

                        # Check image availability
                        available_images = len([f for f in IMAGES_DIR.glob("*.jpg")]) if IMAGES_DIR.exists() else 0
                        total_crops = 22  # From dataset analysis

                        if available_images >= total_crops:
                            st.success(f"✔ Complete Image Collection: All {total_crops} crop images available! ({available_images} total images)")
                        else:
                            st.info(f"ℹ️ Image Status: {available_images}/{total_crops} crop images available. Missing images will show as styled placeholders.")

                        # Summary: top pick banner + side-by-side comparison
                        if recommendations:
                            top = recommendations[0]
                            top_conf = top.get("confidence")
                            conf_chip = f"<span class='km-chip'>{top_conf*100:.0f}% match</span>" if top_conf is not None else ""
                            st.markdown(
                                f"<div class='km-top'><h3>🏆 Best fit: {str(top['name']).title()}</h3>"
                                f"<p>{conf_chip}Est. profit ₹{top.get('profit', 0):,.0f} on {land_area:g} acre(s) "
                                f"· Investment ₹{top.get('investment', 0):,.0f} · Sow: {top.get('sowing_window', '-')}</p></div>",
                                unsafe_allow_html=True,
                            )
                            if len(recommendations) > 1:
                                cmp_df = pd.DataFrame([{
                                    "Crop": str(c["name"]).title(),
                                    "Match": f"{c['confidence']*100:.0f}%" if c.get("confidence") is not None else "-",
                                    "Investment (₹)": f"{c.get('investment', 0):,.0f}",
                                    "Est. profit (₹)": f"{c.get('profit', 0):,.0f}",
                                    "Harvest (months)": c.get("harvest_time", "-"),
                                    "Demand": c.get("demand", "-"),
                                } for c in recommendations])
                                st.dataframe(cmp_df, hide_index=True, use_container_width=True)
                            st.caption("Financial figures are indicative per-acre estimates for planning. Actual costs and prices vary by region, variety and season; confirm with your local agriculture office.")

                        # Display each crop recommendation
                        for idx, crop in enumerate(recommendations, 1):
                            crop_name = crop.get('name', 'Unknown Crop')
                            conf = crop.get("confidence")
                            conf_txt = f" - {conf*100:.0f}% match" if conf is not None else ""
                            with st.expander(f"{idx}. {str(crop_name).title()}{conf_txt} (PIN: {pin_code})", expanded=(idx == 1)):
                                # Clear pincode identification
                                st.info(t("specifically_for").format(pin_code=pin_code))

                                col_img, col_info = st.columns([1, 2])
                                with col_img:
                                    safe_image_show(crop_name)
                                with col_info:
                                    st.subheader(f"{str(crop_name).title()} for PIN {pin_code}")
                                    if crop.get("confidence") is not None:
                                        st.progress(min(max(float(crop["confidence"]), 0.0), 1.0), text=f"Model match: {crop['confidence']*100:.0f}%")
                                    st.write(t("specifically_suited").format(pin_code=pin_code))
                                    st.write(t("your_land_area").format(land_area=land_area))

                                # Add voice read button
                                if st.button(f"🔊 {t('read_aloud')}", key=f"read_{crop_name}"):
                                    speak_text(f"Recommendation for {crop_name}. This crop is well suited for your region. Expected revenue is {crop.get('roi', 0):,.0f} rupees. Profit potential is {crop.get('profit', 0)} rupees.")

                                # Financial Overview
                                st.subheader(t("financial_overview"))

                                fin1, fin2, fin3 = st.columns(3)
                                with fin1:
                                    st.metric(t("expected_roi"), fmt_money(crop.get("roi", 0)))
                                    st.metric(t("profit_potential"), fmt_money(crop.get("profit", 0)))
                                with fin2:
                                    inv = crop.get("investment", 0)
                                    st.metric(t("investment_needed"), fmt_money(inv))
                                    st.metric(t("per_acre_cost"), fmt_money(inv / max(land_area, 0.1)))
                                with fin3:
                                    st.metric(t("market_demand"), crop.get("demand", "-"))
                                    trend = crop.get("price_trend", 0)
                                    trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                                    st.metric(t("price_trend"), f"{trend_icon} {'Rising' if trend > 0 else 'Falling' if trend < 0 else 'Stable'}")

                                # Market Information
                                st.subheader(t("market_information"))
                                market_data = get_real_time_market_prices(crop_name)
                                if market_data['max'] > 0:
                                    st.metric(t("market_price_range"), f"₹{market_data['min']:,.0f} - ₹{market_data['max']:,.0f}/quintal")
                                else:
                                    st.metric(t("market_price_range"), "Not available")
                                st.write(f"Price Trend: {market_data['trend'].capitalize()}")

                                # Timeline & Season Info
                                st.subheader(t("growth_timeline"))
                                time1, time2 = st.columns(2)
                                with time1:
                                    st.metric(t("time_to_harvest"), f"{crop.get('harvest_time', '-')} months")
                                    st.metric(t("resilience_score"), f"{crop.get('resilience', '-')}")
                                with time2:
                                    st.write(f"**{t('best_sowing_window')}:** {crop.get('sowing_window', '-')}")
                                    st.write(f"**{t('critical_months')}:** {crop.get('critical_months', '-')}")

                                # Weather Suitability
                                st.subheader(t("weather_suitability"))
                                weather_impact = crop.get("weather_impact", {})

                                if weather_impact:
                                    for factor, impact in weather_impact.items():
                                        st.write(f"**{factor}:** {impact}")
                                else:
                                    st.info("Weather impact data not available.")

                                # Cultivation Guidelines
                                st.subheader(t("cultivation_guidelines"))
                                guide1, guide2 = st.columns(2)
                                with guide1:
                                    st.write(f"**{t('best_practices')}:**")
                                    for tip in crop.get("tips", []):
                                        st.write(f"• {tip}")
                                with guide2:
                                    st.write(f"**{t('things_to_avoid')}:**")
                                    for warn in crop.get("warnings", []):
                                        st.write(f"• {warn}")

                        # Generate PDF after displaying all crops
                        try:
                            pdf_path = generate_crop_pdf(recommendations, land_area)
                            if pdf_path and os.path.exists(pdf_path):
                                with open(pdf_path, "rb") as f:
                                    pdf_bytes = f.read()
                                st.download_button(
                                    label=t("download_pdf"),
                                    data=pdf_bytes,
                                    file_name=f"crop_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                    mime="application/pdf",
                                    key="final_crop_report_download"
                                )
                                # Clean up the temporary file after some time
                                try:
                                    os.unlink(pdf_path)
                                except:
                                    pass
                        except Exception as e:
                            st.warning("PDF file could not be created. Please check if all required dependencies are installed.")

    # TAB 2: Crop Calendar
    elif selected_tab == t("crop_calendar"):
        st.header(t("monthly_crop_calendar"))

        current_month = datetime.now().strftime("%B")
        st.success(t("current_month").format(current_month=current_month))

        months = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]

        selected_month = st.selectbox(t("select_month"), months, index=datetime.now().month - 1)

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
            }
        }

        for season, crops in crop_calendar.items():
            st.subheader(season)
            for crop, sowing_time in crops.items():
                is_current_season = selected_month in sowing_time or "Year-round" in sowing_time
                if is_current_season:
                    st.markdown(f"✔ **{crop}** - {sowing_time} *ideal for {selected_month}*")
                else:
                    st.markdown(f"✖ {crop} - {sowing_time}")

        # Add voice read button for the entire calendar
        if st.button(f"🔊 {t('read_aloud')}", key="read_calendar"):
            calendar_text = f"Crop calendar for {selected_month}. "
            for season, crops in crop_calendar.items():
                calendar_text += f"{season}: "
                for crop, sowing_time in crops.items():
                    is_current_season = selected_month in sowing_time or "Year-round" in sowing_time
                    if is_current_season:
                        calendar_text += f"{crop} is ideal for this month. "
            speak_text(calendar_text)

    # TAB 3: Crop Diseases
    elif selected_tab == t("crop_diseases"):
        st.header(t("crop_disease_identification"))
        st.info(t("disease_help"))
        
        crops_list = list(CROP_DISEASES.keys())
        selected_crop = st.selectbox(t("select_crop"), crops_list)

        if selected_crop in CROP_DISEASES:
            st.subheader(t("common_diseases").format(crop=selected_crop))
            for disease in CROP_DISEASES[selected_crop]:
                with st.expander(f"🦠 {disease['name']}", expanded=True):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.markdown(f"### {t('symptoms')}")
                        st.write(disease["symptoms"])
                        st.markdown(f"### {t('common_season')}")
                        st.write(disease["season"])
                    with col2:
                        st.markdown(f"### {t('prevention')}")
                        for prevention in disease["prevention"]:
                            st.write(f"• {prevention}")
                        st.markdown(f"### {t('treatment')}")
                        for treatment in disease["treatment"]:
                            st.write(f"• {treatment}")

            st.subheader(t("general_prevention_tips"))
            tip_col1, tip_col2, tip_col3 = st.columns(3)
            with tip_col1:
                st.markdown(f"**{t('cultural_practices')}**")
                st.write("• Practice crop rotation")
                st.write("• Use certified disease-free seeds")
                st.write("• Maintain proper plant spacing")
                st.write("• Remove and destroy infected plants")
            with tip_col2:
                st.markdown(f"**{t('water_management')}**")
                st.write("• Avoid overhead irrigation")
                st.write("• Ensure proper drainage")
                st.write("• Water in morning hours")
                st.write("• Avoid waterlogging")
            with tip_col3:
                st.markdown(f"**{t('chemical_management')}**")
                st.write("• Use fungicides as preventive measure")
                st.write("• Follow recommended dosage")
                st.write("• Rotate chemical groups to avoid resistance")
                st.write("• Observe pre-harvest intervals")

            st.subheader(t("ai_disease_detection"))
            st.info(t("ai_disease_help"))

            uploaded_file = st.file_uploader(t("choose_image"), type=['jpg', 'jpeg', 'png'])

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_container_width=True)

                if st.button(t("analyze_image")):
                    with st.spinner(t("analyzing")):
                        disease, confidence = analyze_crop_disease(image, selected_crop)

                    st.success(t("analysis_complete_disease"))
                    st.subheader(t("detected_disease"))

                    with st.expander(f"{disease} (Confidence: {confidence:.2%})"):
                        # Try to find disease in database
                        treatment_info = "Recommended treatment based on general guidelines."

                        for crop_name, diseases in CROP_DISEASES.items():
                            for d in diseases:
                                if d['name'].lower() in disease.lower() or disease.lower() in d['name'].lower():
                                    treatment_info = f"""
                                    **{t('prevention')}:**
                                    {', '.join(d['prevention'])}

                                    **{t('treatment')}:**
                                    {', '.join(d['treatment'])}
                                    """
                                    break

                        st.write(treatment_info)
                        
                        # Add voice read button for disease information
                        if st.button(f"🔊 {t('read_aloud')}", key=f"read_{disease}"):
                            speak_text(f"Detected disease: {disease}. {treatment_info}")

    # TAB 4: Farming Guidelines
    elif selected_tab == t("farming_guidelines"):
        st.header(t("farming_best_practices"))

        topics = {
            "🌤️ Weather Considerations": [
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
            "🌱 Soil Health": [
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
                
                # Add voice read button for each topic
                if st.button(f"🔊 {t('read_aloud')}", key=f"read_{topic}"):
                    guidelines_text = f"{topic}. {' '.join(guidelines)}"
                    speak_text(guidelines_text)

    # TAB 5: AI Assistant (Gemini Integration)
    elif selected_tab == t("ai_assistant"):
        st.header(t("ai_assistant_header"))
        st.info(t("ai_assistant_help"))

        # Initialize chat history in session state if not present
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat messages
        st.markdown(f"#### {t('chat_with_ai')}")

        # Create a container for the chat messages
        with st.container():
            render_chat(st.session_state.chat_history)

        # Voice input button
        if HAS_VOICE and st.button(t("voice_input"), key="voice_input_ai"):
            user_input = listen_to_speech()
            if user_input:
                st.session_state.user_input = user_input
                st.rerun()

        # Input for new message
        if "user_input_key" not in st.session_state:
            st.session_state.user_input_key = 0

        user_input = st.text_input(
            t("type_question"),
            key=f"user_input_{st.session_state.user_input_key}",
            placeholder="E.g., How to improve soil fertility?"
        )

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            send_button = st.button(t("send_message"), use_container_width=True)
        with col2:
            clear_button = st.button(t("clear_chat"), use_container_width=True)
        with col3:
            if st.button(t("read_last"), use_container_width=True) and st.session_state.chat_history:
                replies = [m["content"] for m in st.session_state.chat_history if m["role"] == "assistant"]
                if replies:
                    speak_text(replies[-1])

        if clear_button:
            st.session_state.chat_history = []
            st.session_state.user_input_key += 1  # Reset the input field
            st.rerun()

        if send_button and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Show a spinner while processing
            with st.spinner(t("ai_thinking")):
                # Create a prompt with context about being a farming assistant
                farming_context = """
                You are KrishiMitra AI, an expert farming assistant for Indian farmers.
                Provide helpful, practical, and accurate advice about farming, crops, weather, soil, and agriculture.

                Keep your responses clear, concise, and focused on practical solutions for farmers.
                If appropriate, suggest specific crops, techniques, or resources that would be helpful.
                """

                full_prompt = f"{farming_context}\n\nFarmer's question: {user_input}"

                # Get response from Gemini API
                response = query_gemini(full_prompt)

                # Format the response to be more farmer-friendly
                formatted_response = format_chat_response(response)

                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": formatted_response})

            # Reset the input field by incrementing the key
            st.session_state.user_input_key += 1

            # Rerun to update the chat display
            st.rerun()

        # Suggested questions
        st.markdown("---")
        st.subheader(t("suggested_questions"))

        suggested_questions = [
            "What crops are best for my region with red soil?",
            "How can I prevent pest attacks without chemicals?",
            "What is the best time to sow wheat in Uttar Pradesh?",
            "How to increase yield in tomato cultivation?",
            "What are the government schemes available for farmers?"
        ]

        cols = st.columns(2)
        for i, question in enumerate(suggested_questions):
            with cols[i % 2]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    # Set the question as the input value
                    st.session_state.user_input_key += 1  # Force reset the input field
                    st.session_state.chat_history.append({"role": "user", "content": question})

                    # Get response
                    with st.spinner(t("ai_thinking")):
                        farming_context = """
                        You are KrishiMitra AI, an expert farming assistant for Indian farmers.
                        Provide helpful, practical, and accurate advice about farming, crops, weather, soil, and agriculture.
                        """

                        full_prompt = f"{farming_context}\n\nFarmer's question: {question}"
                        response = query_gemini(full_prompt)
                        formatted_response = format_chat_response(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": formatted_response})

                    st.rerun()

    # TAB 6: Crop Recommendation by AI (NEW TAB)
    elif selected_tab == t("crop_recommendation_ai"):
        st.header(t("ai_powered_recommendation"))
        st.info(t("ai_crop_help"))

        # Initialize session state for AI chat history
        if "ai_crop_chat" not in st.session_state:
            st.session_state.ai_crop_chat = []

        # Display chat history
        st.markdown(f"### {t('ai_crop_chat')}")

        with st.container():
            render_chat(st.session_state.ai_crop_chat)

        # Input form for crop recommendation
        with st.form("ai_crop_form"):
            st.subheader(t("tell_conditions"))

            col1, col2 = st.columns(2)

            with col1:
                soil_type = st.selectbox(t("soil_type"), ["Loamy", "Sandy", "Clay", "Silty", "Peaty", "Chalky", "Unknown"])
                climate = st.selectbox(t("climate"), ["Tropical", "Subtropical", "Temperate", "Arid", "Semi-arid", "Unknown"])
                water_availability = st.selectbox(t("water_availability"), ["High", "Medium", "Low", "Irrigation Available", "Rainfed"])
            with col2:
                region = st.text_input(t("region_state"), placeholder="e.g., Punjab, Karnataka, etc.")
                budget = st.number_input(t("budget"), min_value=1000, value=50000, step=1000)
                preferences = st.multiselect(t("preferences"), ["Vegetables", "Grains", "Fruits", "Cash Crops", "Pulses", "Oilseeds"])
            additional_info = st.text_area(t("additional_info"), placeholder="Any specific requirements, challenges, or preferences?")

            submitted = st.form_submit_button(t("get_ai_recommendation"))

        # Quick question buttons
        st.subheader(t("quick_questions"))
        quick_col1, quick_col2 = st.columns(2)

        with quick_col1:
            if st.button("Best crops for clay soil", use_container_width=True):
                st.session_state.ai_crop_chat.append({"role": "user", "content": "What are the best crops for clay soil?"})
                response = get_gemini_crop_recommendation("What are the best crops for clay soil?")
                st.session_state.ai_crop_chat.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("Low water requirement crops", use_container_width=True):
                st.session_state.ai_crop_chat.append({"role": "user", "content": "What crops require less water?"})
                response = get_gemini_crop_recommendation("What crops require less water?")
                st.session_state.ai_crop_chat.append({"role": "assistant", "content": response})
                st.rerun()

        with quick_col2:
            if st.button("High-profit crops", use_container_width=True):
                st.session_state.ai_crop_chat.append({"role": "user", "content": "What are the most profitable crops?"})
                response = get_gemini_crop_recommendation("What are the most profitable crops?")
                st.session_state.ai_crop_chat.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("Organic farming options", use_container_width=True):
                st.session_state.ai_crop_chat.append({"role": "user", "content": "What are good crops for organic farming?"})
                response = get_gemini_crop_recommendation("What are good crops for organic farming?")
                st.session_state.ai_crop_chat.append({"role": "assistant", "content": response})
                st.rerun()

        # Process form submission
        if submitted:
            # Build the query from form data
            query_parts = []
            if soil_type != "Unknown":
                query_parts.append(f"soil type: {soil_type}")
            if climate != "Unknown":
                query_parts.append(f"climate: {climate}")
            if water_availability:
                query_parts.append(f"water availability: {water_availability}")
            if region:
                query_parts.append(f"region: {region}")
            if budget:
                query_parts.append(f"budget: Rs{budget}")
            if preferences:
                query_parts.append(f"preferences: {', '.join(preferences)}")
            if additional_info:
                query_parts.append(f"additional info: {additional_info}")
            
            query = f"Recommend crops for these conditions: {', '.join(query_parts)}"

            # Add user query to chat history
            st.session_state.ai_crop_chat.append({"role": "user", "content": query})

            # Get AI response
            with st.spinner("Analyzing your conditions and generating recommendations..."):
                # Get context from previous messages for continuity
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.ai_crop_chat[-3:]])

                response = get_gemini_crop_recommendation(query, context)

            # Add assistant response to chat history
            st.session_state.ai_crop_chat.append({"role": "assistant", "content": response})

            st.rerun()

        # Clear chat button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.ai_crop_chat = []
            st.rerun()

    # TAB 7: Fertilizer Guide
    elif selected_tab == t("fertilizer_guide"):
        st.header(t("fertilizer_guide_header"))

        with st.form("fertilizer_form"):
            col1, col2 = st.columns(2)

            with col1:
                crop_type = st.selectbox(t("select_crop_fertilizer"), list(CROP_DISEASES.keys()))
                n_level = st.slider(t("current_n"), 0, 200, 50)
                p_level = st.slider(t("current_p"), 0, 200, 50)
                k_level = st.slider(t("current_k"), 0, 200, 50)

            with col2:
                soil_type = st.selectbox(t("soil_type"), ["Loamy", "Sandy", "Clay", "Silty"])
                land_area = st.number_input(t("land_area_fertilizer"), min_value=0.1, value=1.0, step=0.1)
                budget = st.number_input(t("fertilizer_budget"), min_value=1000, value=5000, step=500)

            submitted = st.form_submit_button(t("get_fertilizer_recommendations"))

        if submitted:
            # Get crop-specific NPK targets
            crop_targets = CROP_NPK_TARGETS.get(crop_type, {"N": 120, "P": 60, "K": 80})
            
            # Calculate deficits based on crop-specific targets
            n_deficit = max(0, crop_targets["N"] - n_level)
            p_deficit = max(0, crop_targets["P"] - p_level)
            k_deficit = max(0, crop_targets["K"] - k_level)

            # Convert to per acre
            n_deficit_per_acre = n_deficit * 0.4047
            p_deficit_per_acre = p_deficit * 0.4047
            k_deficit_per_acre = k_deficit * 0.4047

            # Calculate required fertilizers
            urea_needed = n_deficit_per_acre * 2.17  # Urea contains 46% N
            dap_needed = p_deficit_per_acre * 2.0  # DAP contains 46% P2O5
            mop_needed = k_deficit_per_acre * 1.67  # MOP contains 60% K2O

            # Calculate costs
            fertilizer_prices = {"Urea": 6, "DAP": 25, "MOP": 15}  # Rs per kg
            urea_cost = urea_needed * fertilizer_prices["Urea"]
            dap_cost = dap_needed * fertilizer_prices["DAP"]
            mop_cost = mop_needed * fertilizer_prices["MOP"]
            total_cost = (urea_cost + dap_cost + mop_cost) * land_area  # whole plot

            st.success(t("fertilizer_recommendations"))
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Urea (46% N)", f"{urea_needed:.1f} kg/acre")
                st.metric("Cost", f"Rs{urea_cost:.0f}")
            with col2:
                st.metric("DAP (18-46-0)", f"{dap_needed:.1f} kg/acre")
                st.metric("Cost", f"Rs{dap_cost:.0f}")
            with col3:
                st.metric("MOP (60% K₂O)", f"{mop_needed:.1f} kg/acre")
                st.metric("Cost", f"Rs{mop_cost:.0f}")

            # Budget comparison
            st.subheader("Budget Analysis")
            budget_col1, budget_col2 = st.columns(2)
            with budget_col1:
                st.metric(f"Total Cost ({land_area:g} acre)", f"Rs{total_cost:.0f}")
            with budget_col2:
                st.metric("Your Budget", f"Rs{budget}")
            
            if total_cost > budget:
                st.warning("⚠️ The recommended fertilizers exceed your budget. Consider prioritizing based on soil test results.")
            else:
                st.success("✅ The recommended fertilizers fit within your budget.")

            st.subheader(t("application_guidelines"))
            st.write("""
            - Apply fertilizers in split doses (basal and top dressing)
            - Incorporate urea into soil to prevent nitrogen loss
            - Apply phosphorus fertilizers near root zone
            - Avoid fertilizer application during heavy rainfall
            - Consider soil test results for precise recommendations
            """)
            
            # Add voice read button
            if st.button(f"🔊 {t('read_aloud')}", key="read_fertilizer"):
                speak_text(f"Fertilizer recommendations for {crop_type}. You need {urea_needed:.1f} kg of Urea, {dap_needed:.1f} kg of DAP, and {mop_needed:.1f} kg of MOP per acre.")

    # TAB 8: Government Schemes (NEW)
    elif selected_tab == t("government_schemes"):
        st.header(t("government_schemes"))
        
        # Get farmer profile information
        farmer_type = st.session_state.farmer_profile["type"] if st.session_state.farmer_profile else "Small Farmer"
        pin_info = load_pin_database().get(str(st.session_state.get("pin_code", "")))
        state = str(pin_info["state"]).title() if pin_info else ""
        
        schemes = get_government_schemes(state, farmer_type.lower().replace(" ", "_"))
        
        if schemes:
            st.subheader(t("available_schemes"))
            st.caption("National schemes" + (f" · your state: {state}. Benefit rates for some schemes differ by state - confirm with your local agriculture office." if state else " · benefit rates for some schemes differ by state."))
            for scheme in schemes:
                st.markdown(f"""
                <div class="government-scheme">
                    <h4>{scheme['name']}</h4>
                    <p>{scheme['description']}</p>
                    <p><strong>Eligibility:</strong> {scheme['eligibility']}</p>
                    <p><a href="{scheme['link']}" target="_blank">Official portal ↗</a></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add voice read button for each scheme
                if st.button(f"🔊 {t('read_aloud')}", key=f"read_{scheme['name']}"):
                    speak_text(f"Government scheme: {scheme['name']}. {scheme['description']}. Eligibility: {scheme['eligibility']}")
        else:
            st.info("No government schemes found for your profile. Please check back later or contact your local agricultural office.")

        # Additional information about how to apply
        st.subheader("How to Apply for Schemes")
        st.write("""
        1. Visit your local agricultural office
        2. Bring necessary documents (Aadhaar card, land records, etc.)
        3. Fill out the application form
        4. Submit to the concerned officer
        5. Track your application status online
        """)

    # TAB 9: Community (NEW)
    elif selected_tab == t("community"):
        st.header(t("community"))
        
        # Two main sections: Connect with Agricultural Officer and Community Advice
        tab1, tab2 = st.tabs(["Connect with Agricultural Officer", "Community Advice"])
        
        with tab1:
            connect_to_agricultural_officer()
        
        with tab2:
            community_advice_section()

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    logger.exception("Application error")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.markdown(f"**{t('footer_text')}**", unsafe_allow_html=True)
with footer_col2:
    st.markdown(f"*{t('data_sources')}*", unsafe_allow_html=True)
with footer_col3:
    st.markdown(f"*{t('support_contact')}*", unsafe_allow_html=True)