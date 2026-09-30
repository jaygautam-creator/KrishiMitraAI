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


# ---------------------------------------------------------------------------
# Indicative estimates for the remaining crops the ML model can recommend.
# Figures are typical per-acre values for India (INR) and vary widely by region,
# variety, season and market - treat them as planning guidance, not guarantees.
# Fields: (investment_per_acre, revenue_per_acre, months_to_harvest, resilience/10,
#          sowing_window, critical_months, price_trend, demand)
# ---------------------------------------------------------------------------
_EXTRA = {
    "apple":       (120000, 300000, 6, 5, "Dec-Feb (planting)", "Apr-Jun (fruit set)", 1, "High",
                    {"Temperature": "Needs cold winters (chilling hours)", "Rainfall": "Well-distributed; avoid hail"},
                    ["Prune in winter", "Use drip irrigation"], ["Protect from hailstorms", "Watch for scab and codling moth"]),
    "banana":      (90000, 210000, 11, 5, "Feb-Mar or Jun-Jul", "Month 3-6", 0, "High",
                    {"Temperature": "Best at 20-35°C", "Humidity": "High humidity suits growth; wind can topple plants"},
                    ["Use tissue-culture plants", "Provide drip irrigation and mulch"], ["Protect from strong winds", "Watch for Panama wilt"]),
    "blackgram":   (8000, 20000, 3, 6, "Jun-Jul (Kharif) / Feb-Mar (summer)", "Flowering stage", 1, "High",
                    {"Rainfall": "Tolerates moderate rain; avoid waterlogging", "Temperature": "Best at 25-35°C"},
                    ["Treat seed with Rhizobium", "Sow in rows for weeding"], ["Avoid waterlogging", "Watch for yellow mosaic virus"]),
    "chickpea":    (9000, 24000, 4, 7, "Oct-Nov", "Flowering and pod filling", 1, "High",
                    {"Rainfall": "Grows well on residual soil moisture", "Temperature": "Cool, dry weather is ideal"},
                    ["Use wilt-resistant varieties", "Pinch tips for more branching"], ["Avoid excess irrigation", "Watch for pod borer"]),
    "coconut":     (60000, 130000, 12, 7, "Jun-Sep (planting)", "Summer months (water stress)", 1, "High",
                    {"Rainfall": "1000-2500 mm well distributed", "Humidity": "Humid coastal climate suits it"},
                    ["Apply organic manure yearly", "Irrigate in dry months"], ["Watch for rhinoceros beetle and red palm weevil", "Avoid waterlogging"]),
    "coffee":      (70000, 160000, 10, 5, "Jun-Jul (planting)", "Blossom showers (Mar-Apr)", 1, "Medium",
                    {"Rainfall": "1500-2500 mm; needs a dry spell before flowering", "Temperature": "15-28°C in shade"},
                    ["Grow under shade trees", "Prune after harvest"], ["Watch for berry borer and leaf rust", "Avoid frost"]),
    "grapes":      (150000, 380000, 5, 5, "Oct-Nov (pruning)", "Flowering and berry set", 1, "High",
                    {"Rainfall": "Rain during flowering harms fruit set", "Temperature": "Warm dry climate is ideal"},
                    ["Train vines on trellis", "Use drip irrigation"], ["Protect from downy mildew in humid weather", "Avoid rain at flowering"]),
    "jute":        (14000, 30000, 4, 6, "Mar-May", "Month 2-3", 0, "Medium",
                    {"Rainfall": "Needs high rainfall and humidity", "Temperature": "24-37°C"},
                    ["Thin plants at 15-20 days", "Retting in clean water gives better fibre"], ["Avoid drought at early stage", "Watch for stem rot"]),
    "kidneybeans": (14000, 34000, 4, 5, "Jun-Jul (hills) / Oct (plains)", "Flowering", 1, "High",
                    {"Temperature": "Prefers mild 15-25°C", "Rainfall": "Avoid heavy rain at flowering"},
                    ["Use staking for climbing types", "Sow in well-drained loam"], ["Avoid waterlogging", "Watch for anthracnose"]),
    "lentil":      (8000, 22000, 4, 7, "Oct-Nov", "Flowering", 1, "High",
                    {"Temperature": "Cool weather during growth", "Rainfall": "Low; grows on residual moisture"},
                    ["Use rust-resistant varieties", "Sow at proper depth"], ["Avoid excess irrigation", "Watch for rust and wilt"]),
    "mango":       (50000, 150000, 4, 6, "Jul-Aug (planting)", "Flowering (Jan-Feb)", 1, "High",
                    {"Temperature": "Warm; frost harms flowers", "Rainfall": "Dry weather at flowering improves fruit set"},
                    ["Prune after harvest", "Manage hoppers at flowering"], ["Avoid rain at flowering", "Watch for powdery mildew"]),
    "mothbeans":   (6000, 14000, 3, 8, "Jun-Jul", "Flowering", 0, "Medium",
                    {"Rainfall": "Very drought tolerant; suits arid regions", "Temperature": "Tolerates heat up to 40°C"},
                    ["Sow with first monsoon showers", "Keep weeds down early"], ["Avoid waterlogging", "Watch for yellow mosaic"]),
    "mungbean":    (8000, 21000, 3, 6, "Jun-Jul / Mar-Apr (summer)", "Flowering", 1, "High",
                    {"Temperature": "Warm; 25-35°C", "Rainfall": "Moderate; avoid heavy rain at maturity"},
                    ["Treat seed with Rhizobium", "Harvest pods as they mature"], ["Avoid waterlogging", "Watch for yellow mosaic virus"]),
    "muskmelon":   (30000, 90000, 3, 5, "Feb-Mar", "Fruit development", 0, "Medium",
                    {"Temperature": "Warm and dry (25-35°C)", "Humidity": "High humidity increases mildew"},
                    ["Use mulching and drip irrigation", "Limit fruits per vine"], ["Avoid water on leaves", "Watch for powdery mildew and fruit fly"]),
    "orange":      (70000, 170000, 9, 6, "Jul-Aug (planting)", "Fruit set and growth", 1, "High",
                    {"Temperature": "Subtropical; 15-30°C", "Rainfall": "Moderate; avoid waterlogging"},
                    ["Prune dead wood", "Apply micronutrients"], ["Watch for citrus canker and psylla", "Avoid waterlogging"]),
    "papaya":      (50000, 150000, 9, 5, "Feb-Mar / Sep-Oct", "Flowering", 0, "Medium",
                    {"Temperature": "Warm, frost-free (22-32°C)", "Rainfall": "Needs good drainage"},
                    ["Grow raised beds", "Irrigate regularly but avoid waterlogging"], ["Very sensitive to waterlogging", "Watch for papaya ring-spot virus"]),
    "pigeonpeas":  (10000, 26000, 6, 7, "Jun-Jul", "Flowering (Oct-Nov)", 1, "High",
                    {"Rainfall": "600-1000 mm; deep-rooted and drought tolerant", "Temperature": "Warm, 20-35°C"},
                    ["Intercrop with soybean or sorghum", "Sow on ridges in heavy soil"], ["Avoid waterlogging", "Watch for pod borer and wilt"]),
    "pomegranate": (80000, 220000, 6, 7, "Jul-Aug / Feb-Mar (planting)", "Flowering and fruit set", 1, "High",
                    {"Temperature": "Hot dry summers, cool winters", "Rainfall": "Drought tolerant; humidity harms fruit"},
                    ["Use drip irrigation", "Bag fruits to protect quality"], ["Watch for bacterial blight", "Avoid irregular watering (fruit cracking)"]),
    "watermelon":  (25000, 80000, 3, 5, "Jan-Mar", "Fruit development", 0, "Medium",
                    {"Temperature": "Hot and dry (24-35°C)", "Rainfall": "Low; sandy loam soils"},
                    ["Use mulch and drip irrigation", "Rotate with non-cucurbits"], ["Avoid waterlogging", "Watch for fusarium wilt and fruit fly"]),
}

for _name, (_inv, _rev, _months, _res, _sow, _crit, _trend, _dem, _wx, _tips, _warn) in _EXTRA.items():
    CROP_DATA.setdefault(_name, {
        "investment_per_acre": _inv, "roi_per_acre": _rev, "harvest_time": _months,
        "resilience": _res, "sowing_window": _sow, "critical_months": _crit,
        "price_trend": _trend, "demand": _dem, "weather_impact": _wx,
        "tips": _tips, "warnings": _warn,
    })
