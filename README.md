# 🌾 KrishiMitra AI

**Crop recommendations and farming help for Indian farmers** — built with Streamlit, scikit-learn and Google Gemini.

Enter a PIN code, land size, budget and soil values. KrishiMitra AI checks the local weather, ranks the **top 3 crops** with a match score, and shows estimated costs, profit, market prices, sowing windows and cultivation tips. It can also answer farming questions in the farmer's own language.

## ✨ Features

| Tab | What it does |
|---|---|
| **Get Recommendations** | Top-3 crops from an ML model (22 crops) with match %, financial estimates, live weather, mandi prices, PDF report |
| **Crop Calendar** | Kharif / Rabi / Zaid sowing and harvest windows by month |
| **Crop Diseases** | Disease database and leaf-photo diagnosis (Vision Transformer model) |
| **Farming Guidelines** | Practical crop-wise guidance |
| **AI Assistant** | Chat with Gemini for farming questions (replies in the selected language) |
| **Crop Recommendation by AI** | Describe soil, climate and water; get Gemini suggestions |
| **Fertilizer Guide** | Urea / DAP / MOP quantities and cost for your plot size and budget |
| **Government Schemes** | National schemes (PM-KISAN, PMFBY, KCC, Soil Health Card, ...) with official links |
| **Community** | National helplines (Kisan Call Centre, etc.) and community advice |

Also: light agriculture-themed UI, English/Hindi interface, read-aloud (text-to-speech) in the chosen language.

## 🧠 How recommendations work

1. PIN code → latitude/longitude (local PIN database, OpenWeather fallback).
2. Weather (temperature, humidity) from OpenWeather. **Rainfall fed to the model is the state's typical monthly rainfall**, because the model was trained on monthly-scale rainfall — not the short-term forecast.
3. A Random Forest model (`crop_model.pkl`) trained on `Crop_recommendation.csv` scores 22 crops from N, P, K, temperature, humidity, pH and rainfall.
4. Financials come from `app/crop_data.py`, scaled by land area. Values are **indicative per-acre estimates** for planning, not guarantees.
5. Soil warnings (low N/P, acidic/alkaline pH) adjust tips and costs.

## 🚀 Run locally

```bash
git clone https://github.com/jaygautam-creator/KrishiMitraAI.git
cd KrishiMitraAI
pip install -r requirements.txt
```

Create `app/.env` (it is git-ignored):

```
OPENWEATHER_API_KEY=your_openweather_key      # required
GEMINI_API_KEY=your_gemini_key                # for the AI tabs
AGMARKNET_API_KEY=your_data_gov_in_key        # optional: live mandi prices (local CSV used otherwise)
```

Start the app:

```bash
./run.sh            # or: PORT=8502 ./run.sh
```

`run.sh` sets `USE_TF=0 USE_FLAX=0` so `transformers` does not import TensorFlow, which can hang the app on some machines. If you start Streamlit manually, use:
`USE_TF=0 USE_FLAX=0 streamlit run app/app.py`.

The first use of leaf-disease detection downloads the Hugging Face model (~350 MB).

## 📁 Project structure

```
KrishiMitraAI/
├── app/
│   ├── app.py                    # Streamlit UI and app logic
│   ├── crop_data.py              # Per-crop cost/revenue/tips for all 22 model crops
│   ├── export_pdf.py             # PDF report
│   ├── recommendation.py, fresh_recommendations.py, data_preprocessing.py
│   ├── pincodes.csv              # PIN → lat/lon/district/state
│   ├── crop_yield.csv            # State rainfall and yields
│   ├── static_prices.csv         # Mandi price snapshot (Rs/quintal)
│   └── regional_crop_data.json
├── images/                       # Crop photos
├── crop_model.pkl                # Trained model + label encoder
├── train_model.py                # Retrain from Crop_recommendation.csv
├── .streamlit/config.toml        # Light theme
├── run.sh
└── requirements.txt
```

## ⚠️ Notes and limitations

- Recommendations are decision support, not a substitute for local agronomy advice; confirm with your Krishi Vigyan Kendra or district agriculture office.
- `crop_model.pkl` was saved with scikit-learn 1.7.1; newer versions load it with a warning. Re-run `train_model.py` to refresh it.
- Mandi prices use `static_prices.csv` unless an AgMarkNet key is set; not every crop has a matching commodity.
- Never commit `.env` files (they are in `.gitignore`).

## 🔮 Ideas for next steps

- District-level rainfall and soil data; automatic soil values from Soil Health Card
- Marathi, Telugu, Gujarati and other translated UI strings
- Live price trends and price alerts
- Offline mode and a mobile-friendly PWA

## 📄 License

MIT
