

# Crop recommendation logic with OpenWeather API integration
import os
import pandas as pd
import numpy as np
import requests
import streamlit as st
from datetime import datetime

def get_lat_lon(pincode):
    """Get latitude and longitude from pincode using a simple mapping"""
    # Simple pincode to coordinates mapping for major Indian cities
    pincode_coords = {
        "110001": (28.6139, 77.2090),  # Delhi
        "400001": (19.0760, 72.8777),  # Mumbai
        "600001": (13.0827, 80.2707),  # Chennai
        "700001": (22.5726, 88.3639),  # Kolkata
        "560001": (12.9716, 77.5946),  # Bangalore
        "380001": (23.0225, 72.5714),  # Ahmedabad
        "500001": (17.3850, 78.4867),  # Hyderabad
        "411001": (18.5204, 73.8567),  # Pune
        "302001": (26.9124, 75.7873),  # Jaipur
        "110017": (28.5355, 77.3910),  # Gurgaon
        "400051": (19.2183, 72.9781),  # Thane
        "600034": (13.0827, 80.2707),  # Chennai
        "700091": (22.5726, 88.3639),  # Kolkata
        "560025": (12.9716, 77.5946),  # Bangalore
        "380015": (23.0225, 72.5714),  # Ahmedabad
        "500032": (17.3850, 78.4867),  # Hyderabad
        "411005": (18.5204, 73.8567),  # Pune
        "302016": (26.9124, 75.7873),  # Jaipur
    }
    
    # If exact pincode not found, use regional mapping
    if pincode in pincode_coords:
        return pincode_coords[pincode]
    
    # Regional fallback based on pincode ranges
    pincode_num = int(pincode) if pincode.isdigit() else 110001
    
    if pincode_num < 200000:  # North India
        return (30.7333, 76.7794)  # Chandigarh
    elif pincode_num < 400000:  # West India
        return (19.0760, 72.8777)  # Mumbai
    elif pincode_num < 600000:  # South India
        return (12.9716, 77.5946)  # Bangalore
    else:  # East India
        return (22.5726, 88.3639)  # Kolkata

def get_weather_data(lat, lon, api_key):
    """Get weather data from OpenWeather API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'rainfall': data.get('rain', {}).get('1h', 0) * 24,  # Convert to daily
                'description': data['weather'][0]['description']
            }
        else:
            print(f"Weather API error: {response.status_code}")
        return None
    except Exception as e:
        print(f"Failed to fetch weather data: {str(e)}")
        return None

def get_pincode_based_conditions(pincode):
    """Generate fallback conditions based on pincode when API fails"""
    if not pincode or not pincode.isdigit():
        pincode = "110001"  # Default to Delhi
    
    pincode_num = int(pincode)
    
    # Create pincode-based variations for different regions
    if pincode_num < 200000:  # North India
        base_temp = 25 + (pincode_num % 15)  # 25-40°C
        base_humidity = 50 + (pincode_num % 30)  # 50-80%
        base_rainfall = 100 + (pincode_num % 200)  # 100-300mm
        base_ph = 6.0 + (pincode_num % 20) / 10  # 6.0-8.0
    elif pincode_num < 400000:  # West India
        base_temp = 28 + (pincode_num % 12)  # 28-40°C
        base_humidity = 40 + (pincode_num % 40)  # 40-80%
        base_rainfall = 50 + (pincode_num % 150)  # 50-200mm
        base_ph = 6.5 + (pincode_num % 15) / 10  # 6.5-8.0
    elif pincode_num < 600000:  # South India
        base_temp = 26 + (pincode_num % 10)  # 26-36°C
        base_humidity = 60 + (pincode_num % 35)  # 60-95%
        base_rainfall = 150 + (pincode_num % 250)  # 150-400mm
        base_ph = 5.5 + (pincode_num % 25) / 10  # 5.5-8.0
    else:  # East India
        base_temp = 24 + (pincode_num % 14)  # 24-38°C
        base_humidity = 55 + (pincode_num % 40)  # 55-95%
        base_rainfall = 200 + (pincode_num % 300)  # 200-500mm
        base_ph = 6.2 + (pincode_num % 18) / 10  # 6.2-8.0
    
    return {
        'temperature': base_temp,
        'humidity': base_humidity,
        'rainfall': base_rainfall,
        'ph': base_ph
    }

def calculate_resilience_score(crop, pincode_conditions):
    """Calculate resilience based on crop and pincode conditions"""
    resilience_base = {
        'rice': 8, 'wheat': 7, 'cotton': 6, 'sugarcane': 7, 'maize': 7,
        'banana': 6, 'mango': 5, 'grapes': 5, 'coconut': 8, 'coffee': 6,
        'jute': 7, 'pomegranate': 6, 'papaya': 5, 'watermelon': 6,
        'muskmelon': 6, 'apple': 4, 'orange': 5, 'chickpea': 8,
        'kidneybeans': 7, 'pigeonpeas': 7, 'mothbeans': 8, 'mungbean': 8,
        'blackgram': 7, 'lentil': 8
    }
    
    base_score = resilience_base.get(crop.lower(), 7)
    temp = pincode_conditions['temperature']
    
    # Adjust based on temperature suitability
    if 20 <= temp <= 35:
        temp_bonus = 1
    elif 15 <= temp <= 40:
        temp_bonus = 0
    else:
        temp_bonus = -1
    
    return min(10, max(1, base_score + temp_bonus))

def calculate_roi(crop, investment, land_area):
    """Calculate ROI based on crop type"""
    base_roi = {
        'rice': 1.4, 'wheat': 1.3, 'cotton': 1.6, 'sugarcane': 1.5,
        'maize': 1.3, 'banana': 1.8, 'mango': 2.0, 'grapes': 2.2,
        'coconut': 1.7, 'coffee': 2.5, 'jute': 1.2, 'pomegranate': 2.0,
        'papaya': 1.9, 'watermelon': 1.6, 'muskmelon': 1.7, 'apple': 1.8,
        'orange': 1.9, 'chickpea': 1.4, 'kidneybeans': 1.3, 'pigeonpeas': 1.3,
        'mothbeans': 1.2, 'mungbean': 1.3, 'blackgram': 1.3, 'lentil': 1.2
    }
    return investment * (base_roi.get(crop.lower(), 1.4))

def get_sowing_window(crop, pincode_conditions):
    """Get sowing window based on crop and pincode conditions"""
    current_month = datetime.now().month
    
    # Enhanced sowing windows for all crops
    sowing_windows = {
        'rice': [(6, 7), (1, 2)], 'wheat': [(10, 11)], 'cotton': [(4, 5), (6, 7)],
        'sugarcane': [(2, 3)], 'maize': [(6, 7), (1, 2)], 'banana': [(6, 8)],
        'mango': [(6, 8)], 'grapes': [(1, 2)], 'coconut': [(6, 8)],
        'coffee': [(6, 8)], 'jute': [(3, 4)], 'pomegranate': [(6, 7)],
        'papaya': [(6, 8)], 'watermelon': [(2, 3)], 'muskmelon': [(2, 3)],
        'apple': [(1, 2)], 'orange': [(6, 8)], 'chickpea': [(10, 11)],
        'kidneybeans': [(6, 7)], 'pigeonpeas': [(6, 7)], 'mothbeans': [(6, 7)],
        'mungbean': [(6, 7)], 'blackgram': [(6, 7)], 'lentil': [(10, 11)]
    }
    
    windows = sowing_windows.get(crop.lower(), [(6, 7)])
    for start, end in windows:
        if start <= current_month <= end:
            return f"Best sowing time: {datetime.now().strftime('%B')}-{datetime.now().replace(month=end).strftime('%B')}"
    return "Best sowing time: Next suitable season (check local calendar)"

def get_crop_recommendations(model_prediction, land_area, budget, pincode=None, api_key=None):
    """Get crop recommendations based on CSV dataset and real weather data from OpenWeather API"""
    
    # Clear debug: Print what we received
    print(f"[DEBUG] === NEW RECOMMENDATION REQUEST ===")
    print(f"[DEBUG] Pincode received: {pincode}")
    print(f"[DEBUG] Model prediction: {model_prediction}")
    print(f"[DEBUG] Budget: {budget}, Land: {land_area}")
    
    # IMPORTANT: Check if we're in pure pincode mode
    pure_pincode_mode = (model_prediction == "PINCODE_BASED")
    if pure_pincode_mode:
        print(f"[DEBUG] PURE PINCODE MODE: Ignoring ML model, using only pincode {pincode}")
    
    # Load the CSV dataset
    csv_path = os.path.join(os.path.dirname(__file__), "..", "Crop_recommendation.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "Crop_recommendation.csv")
    
    try:
        crop_df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

    # Ensure 'label' column exists
    if 'label' not in crop_df.columns:
        print("Error: CSV must have a 'label' column for crop names.")
        return []
    
    # Try to get real weather data first
    weather_data = None
    if api_key and pincode:
        lat, lon = get_lat_lon(pincode)
        weather_data = get_weather_data(lat, lon, api_key)
    
    # Use real weather data if available, otherwise fallback to pincode-based conditions
    if weather_data:
        pincode_conditions = {
            'temperature': weather_data['temperature'],
            'humidity': weather_data['humidity'],
            'rainfall': weather_data['rainfall'],
            'ph': 6.5  # Default pH since weather API doesn't provide this
        }
        print(f"[DEBUG] Real weather data for {pincode}: {pincode_conditions}")
    else:
        pincode_conditions = get_pincode_based_conditions(pincode)
        print(f"[DEBUG] Estimated conditions for {pincode}: {pincode_conditions}")

    def calculate_crop_suitability_score(row):
        """Calculate how well a crop suits the pincode conditions - LOWER score is BETTER"""
        # Calculate percentage differences (normalized scoring)
        temp_diff = abs(row['temperature'] - pincode_conditions['temperature']) / max(pincode_conditions['temperature'], 1) * 100
        hum_diff = abs(row['humidity'] - pincode_conditions['humidity']) / max(pincode_conditions['humidity'], 1) * 100
        rain_diff = abs(row['rainfall'] - pincode_conditions['rainfall']) / max(pincode_conditions['rainfall'], 1) * 100
        ph_diff = abs(row['ph'] - pincode_conditions['ph']) / max(pincode_conditions['ph'], 1) * 100
        
        # Weight factors - higher weight means more importance
        temp_weight = 4.0    # Temperature is most critical
        hum_weight = 3.0     # Humidity is very important
        rain_weight = 3.0    # Rainfall is very important  
        ph_weight = 2.0      # pH is important but less critical
        
        # Calculate weighted score
        base_score = (temp_diff * temp_weight + hum_diff * hum_weight + 
                     rain_diff * rain_weight + ph_diff * ph_weight) / (temp_weight + hum_weight + rain_weight + ph_weight)
        
        # Add regional preference bonus (negative = better match)
        regional_bonus = 0
        if pincode:
            pincode_num = int(pincode) if pincode.isdigit() else 110001
            crop_name = row['label'].lower()
            
            # Strong regional preferences - these crops are ideal for these regions
            if pincode_num < 200000:  # North India (000001-199999)
                if crop_name in ['wheat', 'rice', 'maize', 'chickpea', 'lentil', 'mustard', 'barley']:
                    regional_bonus = -15  # Strong preference
                elif crop_name in ['cotton', 'sugarcane', 'potato', 'onion']:
                    regional_bonus = -8   # Good preference
                elif crop_name in ['mango', 'apple', 'grapes']:
                    regional_bonus = -3   # Moderate preference
                else:
                    regional_bonus = 5    # Less suitable
                    
            elif pincode_num < 500000:  # West India (200000-499999) - FIXED to include 400xxx
                if crop_name in ['cotton', 'sugarcane', 'groundnut', 'mungbean', 'blackgram']:
                    regional_bonus = -15  # Strong preference
                elif crop_name in ['mango', 'grapes', 'pomegranate', 'watermelon', 'muskmelon']:
                    regional_bonus = -8   # Good preference
                elif crop_name in ['rice', 'wheat', 'maize']:
                    regional_bonus = -3   # Moderate preference
                else:
                    regional_bonus = 5    # Less suitable
                    
            elif pincode_num < 700000:  # South India (500000-699999) - FIXED range
                if crop_name in ['rice', 'coconut', 'banana', 'coffee']:
                    regional_bonus = -15  # Strong preference
                elif crop_name in ['papaya', 'orange', 'mango', 'sugarcane']:
                    regional_bonus = -8   # Good preference
                elif crop_name in ['maize', 'cotton', 'chickpea']:
                    regional_bonus = -3   # Moderate preference
                else:
                    regional_bonus = 5    # Less suitable
                    
            else:  # East India (700000+) - FIXED range
                if crop_name in ['rice', 'jute', 'potato', 'lentil', 'chickpea']:
                    regional_bonus = -15  # Strong preference
                elif crop_name in ['wheat', 'maize', 'sugarcane', 'banana']:
                    regional_bonus = -8   # Good preference
                elif crop_name in ['mango', 'coconut']:
                    regional_bonus = -3   # Moderate preference
                else:
                    regional_bonus = 5    # Less suitable
        
        final_score = base_score + regional_bonus
        return final_score
    
    # Calculate suitability scores for all crop entries in the dataset
    crop_df['suitability_score'] = crop_df.apply(calculate_crop_suitability_score, axis=1)
    
    # Group by crop label and get the BEST (lowest score) entry for each crop
    # This finds the most suitable variety of each crop for the given conditions
    best_crop_varieties = crop_df.groupby('label').apply(
        lambda group: group.loc[group['suitability_score'].idxmin()]
    ).reset_index(drop=True)
    
    # Sort crops by suitability score (best matches first)
    best_crop_varieties = best_crop_varieties.sort_values('suitability_score')
    
    # Select top crops for recommendations (limit to top 15 for better performance)
    top_crops = best_crop_varieties.head(15)
    
    print(f"[DEBUG] Top 15 crops for PIN {pincode}:")
    for _, row in top_crops.head(10).iterrows():
        print(f"  {row['label']}: Score {row['suitability_score']:.2f} (Temp: {row['temperature']:.1f}°C, Humidity: {row['humidity']:.1f}%, Rain: {row['rainfall']:.1f}mm, pH: {row['ph']:.1f})")
    
    # Map crop label to image path if exists
    image_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "images"))
    def get_crop_image(label):
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            img_path = os.path.join(image_dir, f"{label.lower()}{ext}")
            if os.path.exists(img_path):
                return img_path
        return None

    def get_critical_months(sowing_window):
        # Try to extract months from sowing_window string
        import re
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        found = re.findall(r"([A-Za-z]+)", sowing_window)
        found_months = [m for m in found if m in months]
        if found_months:
            return "-".join(found_months)
        return "-"

    import streamlit as st
    recommendations = []
    
    # Get regional information based on pincode
    def get_regional_info(pincode):
        if not pincode or not pincode.isdigit():
            return "Unknown Region", "General recommendations"
        
        pincode_num = int(pincode)
        if pincode_num < 200000:  # 000001-199999
            return "North India", "Wheat, Rice, Sugarcane, Cotton are popular in this region"
        elif pincode_num < 500000:  # 200000-499999 (FIXED: West India includes 400xxx)
            return "West India", "Cotton, Sugarcane, Groundnut, Mango, Grapes are commonly grown here"
        elif pincode_num < 700000:  # 500000-699999 (South India)
            return "South India", "Rice, Coconut, Banana, Coffee thrive in this climate"
        else:  # 700000+ (East India)
            return "East India", "Rice, Jute, Potato, Mustard are traditional crops here"
    
    region_name, region_info = get_regional_info(pincode)
    
    # Show pincode-based conditions and regional information
    st.info(f"🌤️ Conditions for PIN {pincode}: Temperature {pincode_conditions['temperature']:.1f}°C, Humidity {pincode_conditions['humidity']:.1f}%, Rainfall {pincode_conditions['rainfall']:.1f}mm, pH {pincode_conditions['ph']:.1f}")
    st.info(f"📍 Region: {region_name} - {region_info}")
    
    # Enhanced crop tips and warnings based on regions
    def get_crop_tips(crop_name, region_name):
        base_tips = {
            'rice': ["Maintain proper water level.", "Use disease-resistant varieties.", "Practice crop rotation."],
            'wheat': ["Sow at proper time.", "Use quality seeds.", "Monitor for rust diseases."],
            'cotton': ["Use certified seeds.", "Avoid waterlogging.", "Timely pest management is crucial."],
            'sugarcane': ["Plant in well-prepared soil.", "Maintain proper spacing.", "Control weeds regularly."],
            'maize': ["Ensure good drainage.", "Use balanced fertilizers.", "Control pests early."],
        'banana': ["Ensure well-drained soil.", "Protect from strong winds.", "Regular irrigation is important."],
            'mango': ["Plant in well-drained soil.", "Prune regularly.", "Protect from fruit flies."],
            'grapes': ["Use trellis system.", "Prune in winter.", "Control powdery mildew."],
            'coconut': ["Plant in sandy loam soil.", "Provide adequate spacing.", "Protect from cyclones."],
            'coffee': ["Plant in shade.", "Maintain soil acidity.", "Prune regularly."],
            'jute': ["Ret in clean water.", "Use quality seeds.", "Harvest at right time."],
            'pomegranate': ["Prune trees after harvest.", "Avoid over-irrigation.", "Monitor for fruit borer pests."],
            'papaya': ["Plant in well-drained soil.", "Provide wind protection.", "Control papaya ring spot virus."],
            'watermelon': ["Use raised beds.", "Ensure good drainage.", "Control powdery mildew."],
            'muskmelon': ["Plant in warm soil.", "Use mulch.", "Control cucumber beetles."],
            'apple': ["Plant in cool climate.", "Prune in winter.", "Control apple scab."],
            'orange': ["Plant in well-drained soil.", "Provide full sun.", "Control citrus canker."],
            'chickpea': ["Sow in cool season.", "Use disease-free seeds.", "Control pod borer."],
            'lentil': ["Sow in cool season.", "Use certified seeds.", "Control rust diseases."],
            'mungbean': ["Sow in warm season.", "Use short duration varieties.", "Control yellow mosaic virus."],
            'blackgram': ["Sow in warm season.", "Use disease-resistant varieties.", "Control leaf spot."],
            'kidneybeans': ["Sow in warm season.", "Use trellis for climbing varieties.", "Control anthracnose."],
            'pigeonpeas': ["Sow in warm season.", "Use long duration varieties.", "Control wilt diseases."],
            'mothbeans': ["Sow in warm season.", "Use short duration varieties.", "Control yellow mosaic virus."]
        }
        
        region_tips = {
            'North India': ["Consider winter crops.", "Plan for irrigation needs.", "Monitor temperature changes."],
            'West India': ["Manage water efficiently.", "Consider drought-resistant varieties.", "Plan for monsoon timing."],
            'South India': ["Consider perennial crops.", "Plan for heavy rainfall.", "Use organic methods."],
            'East India': ["Consider flood-resistant varieties.", "Plan for cyclone season.", "Use traditional methods."]
        }
        
        tips = base_tips.get(crop_name.lower(), ["Follow general farming practices."])
        tips.extend(region_tips.get(region_name, []))
        return tips[:5]  # Limit to 5 tips
    
    def get_crop_warnings(crop_name, region_name):
        base_warnings = {
            'rice': ["Avoid waterlogging.", "Do not use contaminated water."],
            'wheat': ["Avoid late sowing.", "Do not over-irrigate."],
            'cotton': ["Avoid late sowing.", "Do not overuse nitrogen fertilizers."],
            'sugarcane': ["Avoid waterlogging.", "Do not plant in saline soils."],
            'maize': ["Avoid water stress.", "Do not plant too deep."],
        'banana': ["Avoid water stagnation.", "Do not plant in saline soils."],
            'mango': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'grapes': ["Avoid over-irrigation.", "Do not plant in waterlogged areas."],
            'coconut': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'coffee': ["Avoid over-fertilization.", "Do not plant in full sun."],
            'jute': ["Avoid over-retting.", "Do not plant in waterlogged areas."],
            'pomegranate': ["Avoid heavy clay soils.", "Do not let weeds grow near base."],
            'papaya': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'watermelon': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'muskmelon': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'apple': ["Avoid hot climates.", "Do not plant in waterlogged areas."],
            'orange': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'chickpea': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'lentil': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'mungbean': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'blackgram': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'kidneybeans': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'pigeonpeas': ["Avoid waterlogging.", "Do not plant in heavy clay."],
            'mothbeans': ["Avoid waterlogging.", "Do not plant in heavy clay."]
        }
        
        region_warnings = {
            'North India': ["Beware of frost damage.", "Monitor for heat stress."],
            'West India': ["Beware of drought conditions.", "Monitor soil salinity."],
            'South India': ["Beware of heavy rainfall.", "Monitor for waterlogging."],
            'East India': ["Beware of floods.", "Monitor for cyclones."]
        }
        
        warnings = base_warnings.get(crop_name.lower(), ["Follow general precautions."])
        warnings.extend(region_warnings.get(region_name, []))
        return warnings[:4]  # Limit to 4 warnings
    
    # Generate recommendations for top crops
    for _, row in top_crops.head(10).iterrows():
        crop_name = row['label']
        investment = budget * 0.8
        roi = calculate_roi(crop_name, budget, land_area)
        profit = roi - investment
        sowing_window = get_sowing_window(crop_name, pincode_conditions)
        critical_months = get_critical_months(sowing_window)
        
        # Determine suitability level based on score
        score = row['suitability_score']
        if score <= 5:
            suitability = "Excellent"
        elif score <= 15:
            suitability = "Very Good"
        elif score <= 25:
            suitability = "Good"
        elif score <= 40:
            suitability = "Moderate"
        else:
            suitability = "Fair"
        
        rec = {
            'name': crop_name,
            'roi': roi,
            'profit': profit,
            'resilience': calculate_resilience_score(crop_name, pincode_conditions),
            'investment': investment,
            'harvest_time': 4,
            'sowing_window': sowing_window,
            'critical_months': critical_months,
            'weather_impact': {
                "Temperature": f"{row['temperature']:.1f}°C (crop needs) vs {pincode_conditions['temperature']:.1f}°C (your area)",
                "Humidity": f"{row['humidity']:.1f}% (crop needs) vs {pincode_conditions['humidity']:.1f}% (your area)",
                "Rainfall": f"{row['rainfall']:.1f}mm (crop needs) vs {pincode_conditions['rainfall']:.1f}mm (your area)",
                "pH": f"{row['ph']:.1f} (crop needs) vs {pincode_conditions['ph']:.1f} (your area)",
                "Suitability": f"{suitability} (Score: {score:.1f})"
            },
            'price_trend': 1.0,
            'demand': 'High',
            'land_preparation': ["General preparation"],
            'water_requirements': ["General watering"],
            'fertilizer_schedule': ["General fertilizer"],
            'tips': get_crop_tips(crop_name, region_name),
            'warnings': get_crop_warnings(crop_name, region_name),
            'local_resources': ["General resources"],
            'weather_forecast': pd.DataFrame(
                np.random.randn(7, 2),
                columns=['temperature', 'rainfall']
            ),
            'image': get_crop_image(crop_name),
            'debug_score': score
        }
        recommendations.append(rec)
    
    if not recommendations:
        print("[DEBUG] No crops found. Showing top 3 closest crops.")
        for _, row in top_crops.head(3).iterrows():
            crop_name = row['label']
            investment = budget * 0.8
            roi = calculate_roi(crop_name, budget, land_area)
            profit = roi - investment
            sowing_window = get_sowing_window(crop_name, pincode_conditions)
            critical_months = get_critical_months(sowing_window)
            
            rec = {
                'name': crop_name,
                'roi': roi,
                'profit': profit,
                'resilience': calculate_resilience_score(crop_name, pincode_conditions),
                'investment': investment,
                'harvest_time': 4,
                'sowing_window': sowing_window,
                'critical_months': critical_months,
                'weather_impact': {
                    "Temperature": f"{row['temperature']:.1f}°C",
                    "Rainfall": f"{row['rainfall']:.1f}mm"
                },
                'price_trend': 1.0,
                'demand': 'High',
                'land_preparation': ["General preparation"],
                'water_requirements': ["General watering"],
                'fertilizer_schedule': ["General fertilizer"],
                'tips': get_crop_tips(crop_name, region_name),
                'warnings': get_crop_warnings(crop_name, region_name),
                'local_resources': ["General resources"],
                'weather_forecast': pd.DataFrame(
                    np.random.randn(7, 2),
                    columns=['temperature', 'rainfall']
                ),
                'image': get_crop_image(crop_name)
            }
            recommendations.append(rec)

    return recommendations
