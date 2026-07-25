# 🌤️ AI-Based Weather Feel Predictor Web Application

A full-stack, futuristic AI Weather Feel Predictor web application built with **Python Flask**, **Scikit-Learn (Random Forest)**, **SQLite**, and a modern **Glassmorphism Frontend** (HTML5, CSS3, JavaScript, Chart.js).

---

## 🌟 Key Features

1. **AI Weather Prediction Model**:
   - Random Forest Classifier trained on weather parameters (Temperature, Humidity, Wind Speed, Pressure, UV Index, Rain Probability, Season, Time of Day).
   - Predicts categories from **-20°C to +50°C**: `Very Freezing`, `Freezing`, `Very Cold`, `Cold`, `Cool`, `Pleasant`, `Comfortable`, `Warm`, `Hot`, `Very Hot`, `Extreme Heat`.
2. **Real-Time Auto-Prediction**:
   - Sliders automatically trigger debounced AJAX fetch requests to `/api/predict`. No page reloads or "Predict" button required!
3. **Animated Weather Backgrounds**:
   - Canvas particle engine that renders falling **Snow**, **Rain**, **Clouds**, **Sunshine**, and **Heatwaves** dynamically based on temperature & weather feeling.
4. **Comfort Gauge**:
   - Circular SVG animated gauge showing Comfort Score (0-100%) with dynamic color shifts (Blue, Green, Orange, Red).
5. **Dashboard & Chart.js Analytics**:
   - Real-time statistics, Temperature & Comfort trends, prediction frequency doughnut charts, daily quotes, and weather recommendations.
6. **Prediction History & PDF Export**:
   - Searchable prediction logs with single-click deletion and one-click PDF Report export.
7. **Admin Panel**:
   - Manage users, inspect system status, and retrain the Scikit-Learn ML model on-demand.
8. **Voice Text-To-Speech (TTS)**:
   - Click "Speak Prediction" to listen to spoken AI recommendations using HTML5 SpeechSynthesis.

---

## 📁 Project Structure

```
WeatherPredictor/
├── app.py                  # Flask Web Server & REST API
├── train_model.py          # Synthetic Dataset Generator & ML Training Script
├── requirements.txt        # Python Dependencies
├── database.db             # SQLite Database (Auto-created on launch)
├── dataset/
│   └── weather_data.csv    # Synthetic Weather Training Data
├── model/
│   └── weather_model.pkl   # Trained Scikit-Learn Model Pipeline
├── static/
│   ├── css/
│   │   └── style.css       # Glassmorphism & Responsive Stylesheet
│   ├── js/
│   │   ├── weather_effects.js # Canvas Animated Weather Particle System
│   │   ├── main.js         # Interactive Sliders, AJAX, Speech & UI logic
│   │   └── charts.js       # Chart.js Visualizations
│   └── images/
├── templates/
│   ├── base.html           # Layout Template & Navigation
│   ├── login.html          # Authentication (Login / Register / Forgot)
│   ├── dashboard.html      # Weather Summary & Charts Dashboard
│   ├── predict.html        # Interactive Real-Time Predictor & Comfort Meter
│   ├── history.html        # History Logs & PDF Export
│   └── admin.html          # Admin User Management & Retraining Panel
└── README.md               # Documentation & Setup Instructions
```

---

## 🚀 How to Run the Application

### 1. Prerequisite Setup
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Train/Retrain the ML Model
```bash
python train_model.py
```

### 4. Start the Flask Server
```bash
python app.py
```

### 5. Access in Web Browser
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Demo Credentials

- **Standard User**:
  - Username: `demo`
  - Password: `demo123`

- **Administrator**:
  - Username: `admin`
  - Password: `admin123`
