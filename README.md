# ⚡ Predictive Modeling and Management of Load-Shedding in Bangladesh's Power Grid

An advanced engineering capstone project that addresses power supply-demand imbalances across all 9 administrative divisions of Bangladesh. The system integrates offline HOMER Pro microgrid/macro-grid simulation features with a hybrid Machine Learning architecture (**XGBoost + LSTM**) and Explainable AI (**SHAP**). It serves real-time predictions via a **FastAPI/Flask REST API** and visualizes them through a **React.js/Next.js interactive web dashboard**.

## 🎯 Project Overview & Objectives

Bangladesh’s power sector frequently faces severe operational challenges due to supply-demand mismatches during peak seasons, resulting in unannounced load-shedding. This project bridges the gap between traditional energy system simulation and data-driven forecasting by delivering an end-to-end intelligent dispatch prototype for grid operators.

### Key Objectives:

* **Day-Ahead Load-Shedding Prediction:** Predict 24-hour day-ahead load-shedding occurrences (Binary Classification) and power deficit volumes in MW (Regression) for all 9 divisions of Bangladesh.

* **Hybrid ML Pipeline:** Combine XGBoost (to capture non-linear fuel constraints and temperature spikes) with LSTM (to resolve temporal autoregressive residuals).

* **Explainable AI (SHAP):** Provide interpretability using TreeSHAP and KernelSHAP to identify root causes (e.g., gas shortage, heatwaves) behind dispatch decisions.

* **HOMER Pro Integration:** Incorporate baseline microgrid energy balances, reserve margins, and renewable fraction indicators from offline HOMER Pro simulations into the ML feature store.

* **Full-Stack Implementation:** Deliver a robust REST API backend with FastAPI/Flask and a responsive operator dashboard built with React/Next.js.

## 🏗️ System Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        Data Engineering Pipeline                          │
│  [ PGCB Historical Grid Logs ] + [ Regional Weather ] + [ HOMER Pro Logs ] │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                    Hybrid ML Model Engine (Backend API)                   │
│                                                                           │
│   ┌────────────────────────┐         ┌────────────────────────────────┐   │
│   │   Stage 1: XGBoost     │ ──────> │  Stage 2: LSTM Residual Logic  │   │
│   └────────────────────────┘         └────────────────────────────────┘   │
│                                                      │                    │
│                                                      ▼                    │
│                                      ┌────────────────────────────────┐   │
│                                      │   Explainable AI: SHAP Engine  │   │
│                                      └────────────────────────────────┘   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ REST API (JSON Response)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     Frontend Dashboard (React.js / Next.js)              │
│  • Interactive Bangladesh Division Map (9 Divisions)                     │
│  • 24-Hour Day-Ahead Load Deficit (MW) Time-Series Charts                 │
│  • Live SHAP Root-Cause Waterfall / Feature Importance Graphs             │
└───────────────────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

* **Division-Level Regional Forecasting:** Dynamic selection across Dhaka, Chattogram, Rajshahi, Khulna, Barishal, Sylhet, Rangpur, Mymensingh, and Cumilla zones.

* **Hybrid Residual Learning:** Stage-1 XGBoost maps complex non-linear feature interactions, while Stage-2 LSTM models temporal sequence dynamics.

* **Interactive Dispatch Dashboard:** Intuitive UI featuring Recharts / Chart.js for real-time load deficit curves and warning alerts.

* **SHAP Root-Cause Interpretability:** Explicit visibility into *why* a power outage is predicted (e.g., Temperature-Humidity Index spike vs. Generation Reserve failure).

* **HOMER Baseline Feature Store:** Uses offline HOMER simulation metrics to establish baseline vulnerability thresholds under peak demand stress.

## 🛠️ Technology Stack

| Layer | Technology / Tools | 
| ----- | ----- | 
| **Programming Language** | Python 3.10+, JavaScript / TypeScript | 
| **Data & Feature Engineering** | Pandas, NumPy, Scikit-Learn | 
| **Machine Learning Models** | XGBoost, TensorFlow / PyTorch (LSTM) | 
| **Model Interpretability** | SHAP (TreeSHAP & KernelSHAP) | 
| **Energy Simulation** | HOMER Pro (Offline Feature Baseline Generator) | 
| **Backend API** | FastAPI / Flask REST Gateway | 
| **Frontend UI** | React.js / Next.js, Tailwind CSS, Recharts / Plotly.js | 
| **Model Serialization** | Joblib / ONNX | 

## 📊 Feature Engineering & Target Variables

### Target Variables

1. **Binary Classification:** Will load-shedding occur in the next 24 hours? (`Yes` / `No`)

2. **Regression:** What is the magnitude of the deficit in Megawatts (`MW`) and expected duration in hours?

### Engineered Input Features

* **Temporal Features:** Hour of day, day of week, seasonality, national holidays.

* **Weather & Cooling Load:** Temperature-Humidity Index (THI), ambient temperature anomalies.

* **Grid State Variables:** Rolling average demand (24h/168h lags), Available Installed Generation Capacity, Generation Reserve Margin.

* **HOMER Simulation Baseline:** Regional renewable energy fraction, storage capacity buffer.

## 📁 Project Structure

```
bangladesh-grid-forecasting/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI / Flask endpoints
│   │   ├── core/               # Preprocessing & pipeline configs
│   │   ├── models/             # Trained XGBoost, LSTM & SHAP artifacts
│   │   └── services/           # Inference & feature engineering logic
│   ├── main.py                 # Backend entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Map, Chart, and SHAP visualizer components
│   │   ├── pages/              # Division dashboard pages
│   │   └── services/           # API integration HTTP client
│   ├── package.json
│   └── tailwind.config.js
├── ml_pipeline/
│   ├── notebooks/              # Data analysis & model training (EDA)
│   ├── homer_data/             # Processed HOMER Pro simulation outputs
│   └── train_hybrid.py         # XGBoost + LSTM training script
└── README.md
```

## 🔌 API Documentation Example

### **Endpoint:** Predict 24-Hour Day-Ahead Outage & Deficit

```
POST /api/v1/forecast/predict
Content-Type: application/json
```

**Sample Request Body:**

```json
{
  "division": "Dhaka",
  "forecast_date": "2026-11-06",
  "temperature_c": 34.5,
  "humidity_percent": 78,
  "available_generation_mw": 11500,
  "historical_lag_24h_demand_mw": 12800
}
```

**Sample Response Body:**

```json
{
  "division": "Dhaka",
  "is_load_shedding_predicted": true,
  "peak_deficit_mw": 1300.5,
  "probability_score": 0.91,
  "top_root_causes": [
    {"feature": "Gas Shortage / Reserve Margin", "shap_value": 0.42},
    {"feature": "THI (Cooling Demand)", "shap_value": 0.35}
  ]
}
```

## 👥 Authors & Acknowledgments

* <!-- Add Team Members here -->
* <!-- Add Supervisors & Institutions here -->