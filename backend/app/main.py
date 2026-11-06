from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="GridWise-BD Intelligence API",
    description="Backend service for 24-Hour Day-Ahead Regional Power Deficit & Load-Shedding Prediction",
    version="1.0.0"
)

# Enable CORS for React Frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class DivisionMetrics(BaseModel):
    id: int
    name: str
    substation: str
    deficit: str
    outage: str
    driver: str
    risk: str
    riskColor: str
    arima_auc: float
    hybrid_auc: float
    shedding_rate: int

# Mocked / Real Experimental Dataset from Research Pipeline
DIVISIONS_DATA = [
    {
        "id": 0,
        "name": "Dhaka Division (Capital)",
        "substation": "400kV Meghnaghat",
        "deficit": "450 MW",
        "outage": "3 - 4 Hours",
        "driver": "Extreme Ambient Heat & Industrial Peak",
        "risk": "High Risk",
        "riskColor": "rose",
        "arima_auc": 0.72,
        "hybrid_auc": 0.88,
        "shedding_rate": 43
    },
    {
        "id": 1,
        "name": "Mymensingh Division",
        "substation": "Rural Transmission Grid",
        "deficit": "180 MW",
        "outage": "4 - 5 Hours",
        "driver": "Rural Distribution Feeder Overload",
        "risk": "High Risk",
        "riskColor": "rose",
        "arima_auc": 0.70,
        "hybrid_auc": 0.90,
        "shedding_rate": 56
    },
    {
        "id": 2,
        "name": "Rangpur Division",
        "substation": "Northern Interconnect",
        "deficit": "95 MW",
        "outage": "1 - 2 Hours",
        "driver": "Cross-Regional Transmission Lag",
        "risk": "Moderate Risk",
        "riskColor": "amber",
        "arima_auc": 0.74,
        "hybrid_auc": 0.91,
        "shedding_rate": 30
    },
    {
        "id": 3,
        "name": "Chattogram Division (Industrial & Port)",
        "substation": "230kV Anwara Grid",
        "deficit": "210 MW",
        "outage": "2 - 3 Hours",
        "driver": "Gas Supply Shortage",
        "risk": "High Risk",
        "riskColor": "rose",
        "arima_auc": 0.71,
        "hybrid_auc": 0.86,
        "shedding_rate": 38
    },
    {
        "id": 4,
        "name": "Khulna Division (Southern Coast)",
        "substation": "Rampal Transmission Line",
        "deficit": "140 MW",
        "outage": "2 Hours",
        "driver": "Plant Maintenance",
        "risk": "Moderate Risk",
        "riskColor": "amber",
        "arima_auc": 0.73,
        "hybrid_auc": 0.85,
        "shedding_rate": 35
    },
    {
        "id": 5,
        "name": "Rajshahi Division (North-West Agri Hub)",
        "substation": "Bheramara Interconnect",
        "deficit": "160 MW",
        "outage": "3 - 4 Hours",
        "driver": "Irrigation Surge",
        "risk": "Moderate Risk",
        "riskColor": "amber",
        "arima_auc": 0.75,
        "hybrid_auc": 0.87,
        "shedding_rate": 28
    },
    {
        "id": 6,
        "name": "Sylhet Division (Eastern Surma Valley)",
        "substation": "Bibiyana Gas Plant Subgrid",
        "deficit": "25 MW",
        "outage": "<30 Mins",
        "driver": "Low Risk",
        "risk": "Low Risk",
        "riskColor": "emerald",
        "arima_auc": 0.76,
        "hybrid_auc": 0.88,
        "shedding_rate": 22
    },
    {
        "id": 7,
        "name": "Barishal Division (Delta Coastal)",
        "substation": "Payra Thermal Subgrid",
        "deficit": "35 MW",
        "outage": "<45 Mins",
        "driver": "Low Risk",
        "risk": "Low Risk",
        "riskColor": "emerald",
        "arima_auc": 0.78,
        "hybrid_auc": 0.89,
        "shedding_rate": 4
    },
    {
        "id": 8,
        "name": "Cumilla Division (Eastern Hub)",
        "substation": "Tripura Interconnect",
        "deficit": "115 MW",
        "outage": "1.5 - 2.5 Hours",
        "driver": "Transformer Heat",
        "risk": "Moderate Risk",
        "riskColor": "amber",
        "arima_auc": 0.72,
        "hybrid_auc": 0.86,
        "shedding_rate": 32
    }
]

@app.get("/")
def read_root():
    return {"message": "GridWise-BD API is Running"}

@app.get("/api/metrics")
def get_metrics():
    return {
        "macro_metrics": {
            "stage2_hybrid_roc_auc": 0.861,
            "stage2_hybrid_pr_auc": 0.634,
            "tabular_xgboost_roc_auc": 0.814,
            "arima_baseline_roc_auc": 0.720,
            "forecast_horizon": "24h",
            "reliability_rate": "98.2%"
        },
        "divisions": DIVISIONS_DATA
    }

@app.get("/api/predict/{division_id}")
def predict_by_division(division_id: int):
    for div in DIVISIONS_DATA:
        if div["id"] == division_id:
            return {"status": "success", "prediction": div}
    return {"status": "error", "message": "Division not found"}

@app.get("/api/search")
def search_division(query: str):
    results = [
        div for div in DIVISIONS_DATA 
        if query.lower() in div["name"].lower() or query.lower() in div["substation"].lower()
    ]
    return {"status": "success", "results": results}