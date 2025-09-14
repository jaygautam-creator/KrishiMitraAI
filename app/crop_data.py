# crop_data.py

CROP_DATA = {
    "rice": {
        "investment_per_acre": 15000,
        "roi_per_acre": 28000,
        "harvest_time": 4,
        "resilience": 7,
        "sowing_window": "June–July",
        "critical_months": "Aug–Sep",
        "price_trend": 1,
        "demand": "High",
        "weather_impact": {
            "Rainfall": "Good rainfall improves yield",
            "Temperature": "Too high can reduce grain quality"
        },
        "tips": [
            "Maintain standing water for early growth",
            "Use certified seeds"
        ],
        "warnings": [
            "Avoid waterlogging during flowering stage",
            "Monitor for blast disease"
        ]
    },
    "wheat": {
        "investment_per_acre": 12000,
        "roi_per_acre": 24000,
        "harvest_time": 5,
        "resilience": 8,
        "sowing_window": "Oct–Nov",
        "critical_months": "Dec–Jan",
        "price_trend": 0,
        "demand": "Medium",
        "weather_impact": {
            "Humidity": "Excess moisture may cause rust",
            "Temperature": "Ideal is 20–25°C during growth"
        },
        "tips": [
            "Ensure timely sowing",
            "Use zero tillage if possible"
        ],
        "warnings": [
            "Avoid late sowing",
            "Monitor for rust fungus"
        ]
    },
    "maize": {
        "investment_per_acre": 10000,
        "roi_per_acre": 22000,
        "harvest_time": 3,
        "resilience": 6,
        "sowing_window": "June–July",
        "critical_months": "July–August",
        "price_trend": 1,
        "demand": "High",
        "weather_impact": {
            "Rainfall": "Excess water can harm root systems",
            "Temperature": "Grows best in 21–27°C"
        },
        "tips": [
            "Ensure good drainage",
            "Fertilize after 20 days"
        ],
        "warnings": [
            "Don't delay harvesting",
            "Avoid excessive irrigation"
        ]
    },
    "cotton": {
        "investment_per_acre": 18000,
        "roi_per_acre": 35000,
        "harvest_time": 6,
        "resilience": 5,
        "sowing_window": "May–June",
        "critical_months": "Aug–Sep",
        "price_trend": 1,
        "demand": "High",
        "weather_impact": {
            "Humidity": "High humidity may promote pests",
            "Temperature": "Prefers warm dry conditions"
        },
        "tips": [
            "Control pests using traps",
            "Remove weeds early"
        ],
        "warnings": [
            "Don't overwater",
            "Monitor for pink bollworm"
        ]
    },
    "potato": {
        "investment_per_acre": 20000,
        "roi_per_acre": 32000,
        "harvest_time": 3,
        "resilience": 6,
        "sowing_window": "Oct–Nov",
        "critical_months": "Nov–Dec",
        "price_trend": 0,
        "demand": "Medium",
        "weather_impact": {
            "Temperature": "Low temperatures help tuber formation",
            "Humidity": "Too much moisture can cause rot"
        },
        "tips": [
            "Use ridge planting",
            "Provide light irrigation"
        ],
        "warnings": [
            "Avoid flooding",
            "Protect from late blight"
        ]
    }
}
