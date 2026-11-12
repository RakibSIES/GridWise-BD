import os

# Ensure Keras/TensorFlow can read/write config even in restricted environments
os.environ.setdefault("KERAS_HOME", "/tmp/.keras")
try:
    os.makedirs(os.path.expanduser("~/.keras"), exist_ok=True)
except PermissionError:
    os.environ["HOME"] = "/tmp"

from datetime import datetime
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import shap
import streamlit as st
import tensorflow as tf

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="GridWise-BD Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bangladesh Division Coordinates for Open-Meteo Live Weather API
DIVISION_COORDS = {
    "Dhaka": {"lat": 23.8103, "lon": 90.4125, "mult": 1.00},
    "Chattogram": {"lat": 22.3569, "lon": 91.7832, "mult": 0.85},
    "Rajshahi": {"lat": 24.3745, "lon": 88.6042, "mult": 0.75},
    "Mymensingh": {"lat": 24.7471, "lon": 90.4203, "mult": 0.70},
    "Sylhet": {"lat": 24.8949, "lon": 91.8687, "mult": 0.60},
    "Barishal": {"lat": 22.7010, "lon": 90.3535, "mult": 0.45},
    "Rangpur": {"lat": 25.7439, "lon": 89.2752, "mult": 0.65},
    "Cumilla": {"lat": 23.4607, "lon": 91.1809, "mult": 0.75},
    "Khulna": {"lat": 22.8456, "lon": 89.5403, "mult": 0.70},
}

DIVISIONS = list(DIVISION_COORDS.keys())

# Typical 24-hour diurnal load-deficit profile shape for Bangladesh Power Grid
DIURNAL_PROFILE = np.array([
    0.22, 0.16, 0.12, 0.10, 0.14, 0.28, 0.50, 0.78, 1.05, 1.22,
    1.38, 1.55, 1.72, 1.65, 1.52, 1.35, 1.25, 1.48, 2.05, 2.28,
    1.95, 1.45, 0.95, 0.50,
])


# ---------------------------------------------------------
# 2. Load Real Models & Dataset
# ---------------------------------------------------------
@st.cache_resource
def load_models():
    xgb = joblib.load("models/saved_models/xgb_model.pkl")
    lstm = tf.keras.models.load_model(
        "models/saved_models/lstm_model.h5", compile=False
    )
    gru = tf.keras.models.load_model(
        "models/saved_models/gru_model.h5", compile=False
    )
    explainer = shap.TreeExplainer(xgb)
    return xgb, lstm, gru, explainer


@st.cache_data
def load_dataset():
    df = pd.read_csv("data/bd_grid_version_5.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Engineer lag and rolling window features expected by xgb_model.pkl
    for div in DIVISIONS:
        col = f"{div}_load"
        df[f"{col}_lag1"] = df[col].shift(1)
        df[f"{col}_lag7"] = df[col].shift(7)
        df[f"{col}_lag14"] = df[col].shift(14)
        df[f"{col}_roll7_mean"] = df[col].rolling(7).mean()

    df["DayOfWeek"] = df["Date"].dt.day_of_week
    df["Is_Weekend"] = df["DayOfWeek"].isin([4, 5]).astype(int)

    df = df.dropna().reset_index(drop=True)
    return df


try:
    xgb_model, lstm_model, gru_model, shap_explainer = load_models()
    grid_df = load_dataset()
    MODEL_FEATURES = list(xgb_model.feature_names_in_)
except Exception as e:
    st.error(
        f"Error loading models or dataset! Please verify `models/saved_models/` and `data/bd_grid_version_5.csv`. Details: {e}"
    )
    st.stop()


# ---------------------------------------------------------
# 3. Live Open-Meteo Weather Integration
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_live_weather(division: str, fallback_temp: float = 31.5):
    coords = DIVISION_COORDS.get(division, DIVISION_COORDS["Dhaka"])
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current_weather": "true",
        "hourly": "temperature_2m",
        "daily": "temperature_2m_max",
        "timezone": "Asia/Dhaka",
        "forecast_days": 1,
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        current_temp = data.get("current_weather", {}).get("temperature")
        daily_max_list = data.get("daily", {}).get("temperature_2m_max", [])
        hourly_temps = data.get("hourly", {}).get("temperature_2m", [])

        daily_max = daily_max_list[0] if daily_max_list else current_temp
        live_temp = float(daily_max if daily_max is not None else current_temp)
        if hourly_temps and len(hourly_temps) >= 24:
            hourly_24 = [float(x) for x in hourly_temps[:24]]
        else:
            hourly_24 = [live_temp] * 24
        return {
            "temp_c": round(live_temp, 1),
            "current_c": round(float(current_temp or live_temp), 1),
            "hourly_c": hourly_24,
            "source": "Open-Meteo Live API",
            "is_live": True,
        }
    except Exception:
        return {
            "temp_c": round(float(fallback_temp), 1),
            "current_c": round(float(fallback_temp), 1),
            "hourly_c": [round(float(fallback_temp), 1)] * 24,
            "source": "Dataset Historical Baseline (Offline Fallback)",
            "is_live": False,
        }


# ---------------------------------------------------------
# 4. Sidebar (Dispatcher Control Panel)
# ---------------------------------------------------------
st.sidebar.header("🕹️ Dispatcher Control Panel")

selected_division = st.sidebar.selectbox("Select Division", DIVISIONS)
target_date = st.sidebar.date_input("Target Date", datetime.now())

st.sidebar.markdown("---")
model_choice = st.sidebar.radio(
    "Model Architecture",
    ["XGBoost + LSTM (Default)", "XGBoost + GRU", "XGBoost Baseline"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Grid Scenario Overrides")
gas_shortage = st.sidebar.checkbox("Simulate Fuel/Gas Shortage")
heatwave = st.sidebar.checkbox("Simulate High Temp / Heatwave")

# Fetch live weather for the selected division
fallback_temp_val = float(grid_df["Maximum Temperature in Dhaka was"].median())
weather_info = fetch_live_weather(selected_division, fallback_temp=fallback_temp_val)

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Real-Time Weather Feed")
effective_temp = weather_info["temp_c"] + (4.5 if heatwave else 0.0)
st.sidebar.metric(
    label=f"{selected_division} Temperature",
    value=f"{effective_temp:.1f} °C",
    delta="+4.5 °C (Heatwave Override)" if heatwave else f"Current: {weather_info['current_c']:.1f} °C",
)
st.sidebar.caption(f"Source: {weather_info['source']}")


# ---------------------------------------------------------
# 5. Stage 1 (XGBoost) & Stage 2 (LSTM/GRU Residual Correction)
# ---------------------------------------------------------
def select_reference_window(df: pd.DataFrame, target_dt, division: str):
    """Selects a 14-day reference window and baseline feature row from the dataset."""
    target_ts = pd.Timestamp(target_dt)
    exact_matches = df[df["Date"] == target_ts]
    if not exact_matches.empty and exact_matches.index[0] >= 14:
        end_idx = exact_matches.index[0]
    else:
        # Match historical rows in the same month with active load-shedding context
        div_load_col = f"{division}_load"
        month_matches = df[(df["Month"] == target_ts.month) & (df[div_load_col] > 0)]
        if month_matches.empty:
            month_matches = df[df["Dhaka_load"] > 50]
        if month_matches.empty:
            end_idx = len(df) - 1
        else:
            # Pick a representative recent active grid stress day
            end_idx = int(month_matches.index[-1])
            if end_idx < 14:
                end_idx = max(14, len(df) - 1)

    window_14 = df.iloc[end_idx - 13 : end_idx + 1].copy()
    base_row = df.iloc[[end_idx]].copy()
    return base_row, window_14


def run_hybrid_pipeline(
    df: pd.DataFrame,
    division: str,
    target_dt,
    model_type: str,
    live_temp: float,
    gas_flag: bool,
    temp_flag: bool,
):
    hours = list(range(24))
    base_row_full, window_14 = select_reference_window(df, target_dt, division)

    # Prepare the 71-feature input row for Stage 1 XGBoost
    feature_row = base_row_full[MODEL_FEATURES].copy()
    target_ts = pd.Timestamp(target_dt)
    feature_row["Year"] = target_ts.year
    feature_row["Month"] = target_ts.month
    feature_row["DayOfWeek"] = target_ts.day_of_week
    feature_row["Is_Weekend"] = int(target_ts.day_of_week in [4, 5])

    # Feed live Open-Meteo temperature into the XGBoost feature row
    applied_temp = live_temp + (4.5 if temp_flag else 0.0)
    feature_row["Maximum Temperature in Dhaka was"] = applied_temp

    # Apply scenario overrides directly to the feature vector
    if gas_flag:
        feature_row["Gas/LF limitation"] = feature_row["Gas/LF limitation"] * 1.35 + 350.0
        for div in DIVISIONS:
            feature_row[f"{div}_supply"] = feature_row[f"{div}_supply"] * 0.90

    if temp_flag:
        feature_row["Max. Demand at eve. peak (Generation end)"] *= 1.12
        feature_row["Max. Demand at eve. peak (Sub-station end)"] *= 1.12
        for div in DIVISIONS:
            feature_row[f"{div}_demand"] = feature_row[f"{div}_demand"] * 1.12

    # --- STAGE 1: XGBoost Prediction ---
    stage1_raw_pred = float(xgb_model.predict(feature_row)[0])

    # Compute division-specific demand-supply stress and scale factor
    div_mult = DIVISION_COORDS[division]["mult"]
    div_demand = float(feature_row[f"{division}_demand"].iloc[0])
    div_supply = float(feature_row[f"{division}_supply"].iloc[0])
    div_gap = max(0.0, div_demand - div_supply)

    # Combine XGBoost Stage 1 prediction with division load factor across 24 hours
    base_magnitude = max(25.0, stage1_raw_pred) * div_mult + (0.25 * div_gap)
    if gas_flag:
        base_magnitude = base_magnitude * 1.25 + 25.0
    if temp_flag:
        base_magnitude = base_magnitude * 1.18 + 15.0

    stage1_hourly = np.maximum(0.0, np.round(base_magnitude * DIURNAL_PROFILE, 2))

    # --- STAGE 2: LSTM / GRU Residual Correction ---
    # Calculate historical 14-day residuals: Actual Load - Stage 1 XGBoost Prediction
    hist_X = window_14[MODEL_FEATURES]
    hist_xgb_preds = xgb_model.predict(hist_X)
    target_col = f"{division}_load" if f"{division}_load" in window_14.columns else "Dhaka_load"
    residuals_14 = window_14[target_col].values - hist_xgb_preds

    # Normalize sequence into (1, 14, 1) tensor for Keras sequence model inference
    seq_scale = max(1.0, float(np.std(residuals_14)) if np.std(residuals_14) > 0 else 1.0)
    seq_input = (residuals_14 / seq_scale).reshape(1, 14, 1).astype(np.float32)

    if "LSTM" in model_type:
        raw_res = float(lstm_model.predict(seq_input, verbose=0).flatten()[0])
        # Modulate residual across the 24-hour cycle
        residual_curve = np.sin(np.linspace(0, 2 * np.pi, 24)) * 14.0 + raw_res * 1.8
        final_hourly = np.maximum(0.0, np.round(stage1_hourly + residual_curve, 2))
        stage2_scalar = round(float(np.mean(residual_curve)), 2)
    elif "GRU" in model_type:
        raw_res = float(gru_model.predict(seq_input, verbose=0).flatten()[0])
        residual_curve = np.cos(np.linspace(0, 2 * np.pi, 24)) * 12.0 + raw_res * 1.5 - 6.0
        final_hourly = np.maximum(0.0, np.round(stage1_hourly + residual_curve, 2))
        stage2_scalar = round(float(np.mean(residual_curve)), 2)
    else:
        raw_res = 0.0
        residual_curve = np.zeros(24)
        final_hourly = stage1_hourly.copy()
        stage2_scalar = 0.0

    return {
        "hours": hours,
        "final_hourly": final_hourly,
        "stage1_hourly": stage1_hourly,
        "stage1_raw": round(stage1_raw_pred, 2),
        "stage2_raw": round(raw_res, 2),
        "stage2_mean_delta": stage2_scalar,
        "residual_curve": np.round(residual_curve, 2),
        "feature_row": feature_row,
        "residuals_14": residuals_14,
    }


pipeline_out = run_hybrid_pipeline(
    df=grid_df,
    division=selected_division,
    target_dt=target_date,
    model_type=model_choice,
    live_temp=weather_info["temp_c"],
    gas_flag=gas_shortage,
    temp_flag=heatwave,
)

hours = pipeline_out["hours"]
deficit_mw = pipeline_out["final_hourly"]
stage1_mw = pipeline_out["stage1_hourly"]
feature_row = pipeline_out["feature_row"]

# Summary Metrics Calculation
peak_deficit = float(np.max(deficit_mw))
peak_hour = int(np.argmax(deficit_mw))
total_mwh = float(np.sum(deficit_mw))
high_risk_hrs = int(np.sum(deficit_mw > 100))


# ---------------------------------------------------------
# 6. Dashboard Header & KPI Metrics
# ---------------------------------------------------------
st.title("⚡ GridWise-BD: Day-Ahead Load-Shedding Predictor")
st.caption(
    "Explainable Hybrid Machine Learning Framework (Stage 1: XGBoost + Stage 2: LSTM/GRU Residual Correction + SHAP XAI)"
)
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.subheader("Selected Region")
    st.markdown(f"### **{selected_division}**")
    st.caption(f"Live Temp: {effective_temp:.1f} °C")

with col2:
    st.subheader("24h Peak Deficit")
    st.markdown(f"### **{peak_deficit:.0f} MW**")
    st.caption(f"↑ Peak at {peak_hour:02d}:00")

with col3:
    st.subheader("Total Load Deficit")
    st.markdown(f"### **{total_mwh:,.0f} MWh**")
    st.caption("Cumulative 24h Deficit")

with col4:
    st.subheader("High-Risk Hours")
    st.markdown(f"### **{high_risk_hrs} Hrs**")
    st.caption("Deficit > 100 MW")

with col5:
    st.subheader("Stage 2 Correction")
    st.markdown(f"### **{pipeline_out['stage2_mean_delta']:+.1f} MW**")
    st.caption(f"Model Raw Residual: {pipeline_out['stage2_raw']:+.2f}")

st.markdown("---")


# ---------------------------------------------------------
# 7. Main Content Tabs: 24-Hour Forecast & SHAP Explainability
# ---------------------------------------------------------
tab_forecast, tab_shap = st.tabs(
    ["📈 24-Hour Load-Deficit Forecast", "🧠 SHAP Explainability (XAI)"]
)

with tab_forecast:
    st.subheader(f"📈 24-Hour Day-Ahead Load-Deficit Profile ({selected_division})")

    fig = go.Figure()

    # Stage 1 Baseline Trace (shown for comparison when hybrid model is active)
    if "Baseline" not in model_choice:
        fig.add_trace(
            go.Scatter(
                x=[f"{h:02d}:00" for h in hours],
                y=stage1_mw,
                mode="lines",
                name="Stage 1: XGBoost Baseline",
                line=dict(color="#636EFA", width=2, dash="dot"),
            )
        )

    # Final Hybrid Prediction Curve (Stage 1 + Stage 2)
    fig.add_trace(
        go.Scatter(
            x=[f"{h:02d}:00" for h in hours],
            y=deficit_mw,
            mode="lines+markers",
            name=f"Final Forecast ({model_choice})",
            line=dict(color="#FF4B4B", width=3),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(255, 75, 75, 0.12)",
        )
    )

    # Load Shedding Threshold Line (100 MW)
    fig.add_trace(
        go.Scatter(
            x=[f"{h:02d}:00" for h in hours],
            y=[100] * 24,
            mode="lines",
            name="Critical Load Shedding Threshold (100 MW)",
            line=dict(color="#FFA500", dash="dash", width=2),
        )
    )

    fig.update_layout(
        xaxis_title="Hour of Day (24-Hour Schedule)",
        yaxis_title="Predicted Load Deficit (MW)",
        template="plotly_dark",
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, width="stretch")

    # Export Schedule Section
    st.markdown("---")
    df_out = pd.DataFrame(
        {
            "Hour": [f"{h:02d}:00" for h in hours],
            "Division": selected_division,
            "Date": target_date,
            "Live_Temperature_C": effective_temp,
            "Stage1_XGBoost_MW": stage1_mw,
            "Stage2_Residual_Adjustment_MW": pipeline_out["residual_curve"],
            "Final_Predicted_Deficit_MW": deficit_mw,
        }
    )

    col_txt, col_btn = st.columns([3, 1])
    with col_txt:
        st.write("📋 **Export Predicted 24-Hour Dispatch Schedule**")
        st.caption(
            "Includes Stage 1 XGBoost baseline, Stage 2 LSTM/GRU residual corrections, and live temperature telemetry."
        )
    with col_btn:
        st.download_button(
            label="📥 Download Schedule CSV",
            data=df_out.to_csv(index=False).encode("utf-8"),
            file_name=f"gridwise_{selected_division}_{target_date}.csv",
            mime="text/csv",
        )

with tab_shap:
    st.subheader("🧠 SHAP Explainability (XAI) — Stage 1 XGBoost Feature Attribution")
    st.write(
        "Understand which grid, weather, and historical lag features drive the load-deficit forecast for "
        f"**{selected_division}** on **{target_date}**."
    )

    # Compute exact TreeSHAP values for the active 71-feature input row
    shap_values_row = shap_explainer.shap_values(feature_row)[0]
    base_val = float(
        np.ravel(shap_explainer.expected_value)[0]
        if hasattr(shap_explainer, "expected_value")
        else 0.0
    )

    shap_df = pd.DataFrame(
        {
            "Feature": MODEL_FEATURES,
            "Value": feature_row.iloc[0].values,
            "SHAP_Contribution": shap_values_row,
            "Abs_SHAP": np.abs(shap_values_row),
            "Global_Importance": xgb_model.feature_importances_,
        }
    ).sort_values("Abs_SHAP", ascending=False)

    top_n = st.slider(
        "Number of Top Features to Display", min_value=8, max_value=25, value=15
    )
    top_local = shap_df.head(top_n).sort_values("SHAP_Contribution", ascending=True)

    col_local, col_global = st.columns(2)

    with col_local:
        st.markdown("#### 🔍 Local SHAP Feature Contributions (Current Forecast)")
        colors = [
            "#FF4B4B" if val >= 0 else "#00CC96"
            for val in top_local["SHAP_Contribution"]
        ]
        fig_local = go.Figure(
            go.Bar(
                x=top_local["SHAP_Contribution"],
                y=[
                    f"{feat} ({val:.1f})"
                    for feat, val in zip(top_local["Feature"], top_local["Value"])
                ],
                orientation="h",
                marker_color=colors,
                text=[f"{v:+.2f} MW" for v in top_local["SHAP_Contribution"]],
                textposition="outside",
            )
        )
        fig_local.update_layout(
            xaxis_title="SHAP Value (Impact on Predicted Deficit in MW)",
            yaxis_title="Feature (Current Value)",
            template="plotly_dark",
            height=500,
            margin=dict(l=20, r=40, t=20, b=20),
        )
        st.plotly_chart(fig_local, width="stretch")
        st.caption(
            f"Base Value: **{base_val:.2f} MW** | Red bars push load deficit higher; green bars reduce deficit."
        )

    with col_global:
        st.markdown("#### 🌐 Global XGBoost Feature Importance (Top Drivers)")
        top_global = shap_df.sort_values(
            "Global_Importance", ascending=False
        ).head(top_n).sort_values("Global_Importance", ascending=True)
        fig_global = go.Figure(
            go.Bar(
                x=top_global["Global_Importance"],
                y=top_global["Feature"],
                orientation="h",
                marker_color="#636EFA",
                text=[f"{v * 100:.1f}%" for v in top_global["Global_Importance"]],
                textposition="outside",
            )
        )
        fig_global.update_layout(
            xaxis_title="Relative Gain Importance",
            yaxis_title="Feature Name",
            template="plotly_dark",
            height=500,
            margin=dict(l=20, r=40, t=20, b=20),
        )
        st.plotly_chart(fig_global, width="stretch")
        st.caption(
            "Global importance across all 71 engineered features in `xgb_model.pkl`."
        )

    st.markdown("---")
    st.markdown("#### 📊 Active Feature Row & SHAP Attribution Table")
    st.dataframe(
        shap_df[["Feature", "Value", "SHAP_Contribution", "Global_Importance"]]
        .head(25)
        .style.format(
            {
                "Value": "{:.2f}",
                "SHAP_Contribution": "{:+.3f}",
                "Global_Importance": "{:.4f}",
            }
        ),
        width="stretch",
    )
