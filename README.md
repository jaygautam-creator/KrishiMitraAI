# KrishiMitra AI 🌾

An **AI-powered intelligent crop recommendation system** designed for Indian farmers.
It suggests the most suitable and profitable crops based on **location, land size, budget, and weather conditions**.

---

## ✨ Features

* **Smart Crop Recommendations** using:

  * Location (PIN code / GPS)
  * Land area
  * Budget constraints

* **Detailed Crop Analysis** including:

  * Expected Return on Investment (ROI)
  * Crop resilience score
  * Optimal sowing window
  * Weather-based insights

---

## 🛠 Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **Machine Learning Models**: scikit-learn, XGBoost
* **Data Sources**:

  * [OpenWeatherMap API](https://openweathermap.org/api) – weather data
  * [Soil Health Card (ICAR)](https://soilhealth.dac.gov.in/)
  * [AgMarkNet](https://agmarknet.gov.in/) – market prices
  * [ICRISAT](https://www.icrisat.org/) / FAO – crop yield data

---

## ⚡ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/jaygautam-creator/KrishiMitra-AI.git
   cd KrishiMitra-AI
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate       # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**

   * Create a `.env` file in the root directory
   * Add your API key:

     ```
     OPENWEATHERMAP_API_KEY=your_api_key_here
     ```

5. **Run the application**

   ```bash
   streamlit run app/app.py
   ```

---

## 📂 Project Structure

```
KrishiMitra-AI/
├── app/
│   ├── app.py                  # Streamlit frontend
│   ├── recommendation.py       # Crop recommendation engine
│   ├── data_preprocessing.py   # Data preprocessing pipeline
│   └── export_pdf.py           # Report generation
├── models/
│   └── crop_model.pkl          # Trained ML model
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

---

## 🚀 Future Roadmap

* 🌐 Multi-language support (Hindi, Marathi, Telugu, etc.)
* 📱 Mobile app version
* 🌱 IoT soil sensor integration
* 💹 Real-time market price updates
* 👨‍🌾 Community features for farmers

---

## 🤝 Contributing

Contributions are always welcome!

1. Fork the repo
2. Create a new branch (`feature/my-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 👥 Authors

* **Jay Gautam**
* **Vaibhav Chaudhary**
* **Abhishek Singh**
