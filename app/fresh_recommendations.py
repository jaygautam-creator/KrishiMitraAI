# Fresh recommendation function - bypasses all caching
import os
import pandas as pd
import numpy as np
import requests
import streamlit as st
from datetime import datetime

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
    elif pincode_num < 500000:  # West India
        base_temp = 28 + (pincode_num % 12)  # 28-40°C
        base_humidity = 40 + (pincode_num % 40)  # 40-80%
        base_rainfall = 50 + (pincode_num % 150)  # 50-200mm
        base_ph = 6.5 + (pincode_num % 15) / 10  # 6.5-8.0
    elif pincode_num < 700000:  # South India
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

def get_fresh_crop_recommendations(pincode, land_area, budget):
    """Get completely fresh crop recommendations - no caching"""
    
    print(f"[FRESH] Getting recommendations for PIN {pincode}")
    
    # Load the CSV dataset fresh
    csv_path = os.path.join(os.path.dirname(__file__), "..", "Crop_recommendation.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "Crop_recommendation.csv")
    
    try:
        crop_df = pd.read_csv(csv_path)
        print(f"[FRESH] Loaded {len(crop_df)} crop entries")
    except Exception as e:
        print(f"[FRESH] Error loading CSV: {e}")
        return []

    if 'label' not in crop_df.columns:
        return []
    
    # Get pincode conditions
    pincode_conditions = get_pincode_based_conditions(pincode)
    print(f"[FRESH] Conditions for {pincode}: {pincode_conditions}")
    
    def calculate_suitability_score(row):
        """Calculate suitability - LOWER score is BETTER"""
        # Percentage differences
        temp_diff = abs(row['temperature'] - pincode_conditions['temperature']) / max(pincode_conditions['temperature'], 1) * 100
        hum_diff = abs(row['humidity'] - pincode_conditions['humidity']) / max(pincode_conditions['humidity'], 1) * 100
        rain_diff = abs(row['rainfall'] - pincode_conditions['rainfall']) / max(pincode_conditions['rainfall'], 1) * 100
        ph_diff = abs(row['ph'] - pincode_conditions['ph']) / max(pincode_conditions['ph'], 1) * 100
        
        # Weighted score
        base_score = (temp_diff * 4.0 + hum_diff * 3.0 + rain_diff * 3.0 + ph_diff * 2.0) / 12.0
        
        # Regional preferences
        regional_bonus = 0
        if pincode:
            pincode_num = int(pincode) if pincode.isdigit() else 110001
            crop_name = row['label'].lower()
            
            if pincode_num < 200000:  # North India
                if crop_name in ['wheat', 'rice', 'maize', 'chickpea', 'lentil']:
                    regional_bonus = -15
                elif crop_name in ['cotton', 'sugarcane']:
                    regional_bonus = -8
                else:
                    regional_bonus = 5
                    
            elif pincode_num < 500000:  # West India  
                if crop_name in ['cotton', 'sugarcane', 'mungbean', 'blackgram']:
                    regional_bonus = -15
                elif crop_name in ['mango', 'grapes', 'pomegranate']:
                    regional_bonus = -8
                else:
                    regional_bonus = 5
                    
            elif pincode_num < 700000:  # South India
                if crop_name in ['rice', 'coconut', 'banana', 'coffee']:
                    regional_bonus = -15
                elif crop_name in ['papaya', 'orange', 'mango']:
                    regional_bonus = -8
                else:
                    regional_bonus = 5
                    
            else:  # East India
                if crop_name in ['rice', 'jute', 'lentil', 'chickpea']:
                    regional_bonus = -15
                elif crop_name in ['wheat', 'maize']:
                    regional_bonus = -8
                else:
                    regional_bonus = 5
        
        return base_score + regional_bonus
    
    # Calculate scores
    crop_df['suitability_score'] = crop_df.apply(calculate_suitability_score, axis=1)
    
    # Get best variety of each crop
    best_crops = crop_df.groupby('label').apply(
        lambda group: group.loc[group['suitability_score'].idxmin()]
    ).reset_index(drop=True)
    
    # Sort by score (best first)
    best_crops = best_crops.sort_values('suitability_score').head(10)
    
    print(f"[FRESH] Top 3 for PIN {pincode}:")
    for i, (_, row) in enumerate(best_crops.head(3).iterrows(), 1):
        print(f"[FRESH]   {i}. {row['label']}: Score {row['suitability_score']:.2f}")
    
    # Create recommendations
    recommendations = []
    for _, row in best_crops.iterrows():
        crop_name = row['label']
        score = row['suitability_score']
        
        rec = {
            'name': crop_name,
            'roi': budget * 1.4,
            'profit': budget * 0.8,
            'investment': budget * 0.8,
            'resilience': 7,
            'harvest_time': 4,
            'sowing_window': 'Season appropriate',
            'critical_months': 'Monitor weather',
            'weather_impact': {
                'Temperature': f"{row['temperature']:.1f}°C (crop) vs {pincode_conditions['temperature']:.1f}°C (area)",
                'Humidity': f"{row['humidity']:.1f}% (crop) vs {pincode_conditions['humidity']:.1f}% (area)",
                'Rainfall': f"{row['rainfall']:.1f}mm (crop) vs {pincode_conditions['rainfall']:.1f}mm (area)",
                'Suitability': f"Score: {score:.2f}"
            },
            'price_trend': 1.0,
            'demand': 'High',
            'tips': [f"Suitable for PIN {pincode}", "Follow regional practices"],
            'warnings': ["Monitor weather conditions"],
            'debug_score': score
        }
        recommendations.append(rec)
    
    return recommendations
