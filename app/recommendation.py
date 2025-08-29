# recommendation.py

from crop_data import CROP_DATA
from datetime import datetime
import numpy as np

def calculate_resilience_score(crop_name):
    """
    Dummy resilience calculation based on randomness or later weather input
    """
    return np.random.randint(6, 10)

def calculate_roi_per_crop(crop_name, investment_per_acre, roi_per_acre, land_area):
    """
    Calculate ROI based on area and per-acre values
    """
    total_investment = investment_per_acre * land_area
    total_roi = roi_per_acre * land_area
    profit = total_roi - total_investment
    return total_investment, total_roi, profit

def get_crop_recommendations(crop_name, land_area=1.0, budget=50000):
    """
    Main function to recommend top 3 crops based on model prediction + dynamic filters
    """
    recommended_crop = crop_name.lower()
    current_month = datetime.now().strftime("%b")  # Example: 'Aug'

    matches = []

    for crop, details in CROP_DATA.items():
        investment_per_acre = details.get("investment_per_acre", 20000)
        roi_per_acre = details.get("roi_per_acre", 35000)

        total_investment, total_roi, profit = calculate_roi_per_crop(
            crop, investment_per_acre, roi_per_acre, land_area
        )

        if total_investment > budget:
            continue  # skip if it exceeds user budget

        model_match = (crop == recommended_crop)
        seasonal_match = current_month in details["sowing_window"]

        score = 0
        if model_match:
            score += 2
        if seasonal_match:
            score += 1
        if details.get("price_trend", 0) > 0:
            score += 1
        if details.get("demand", "High") == "High":
            score += 1

        matches.append({
            "name": crop.title(),
            "investment": total_investment,
            "roi": total_roi,
            "profit": profit,
            "harvest_time": details["harvest_time"],
            "resilience": calculate_resilience_score(crop),
            "sowing_window": details["sowing_window"],
            "critical_months": details["critical_months"],
            "price_trend": details["price_trend"],
            "demand": details["demand"],
            "weather_impact": details["weather_impact"],
            "tips": details["tips"],
            "warnings": details["warnings"],
            "score": score
        })

    # Sort by score and then profit
    matches.sort(key=lambda x: (x["score"], x["profit"]), reverse=True)

    return matches[:3]
