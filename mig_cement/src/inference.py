import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from data_loader import load_data
from preprocessing import EXOG_COLS

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "..", "data", "MIG_Cement_Records.db")
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "rf_all.pkl")

app = FastAPI(title="MIG Cement Demand Forecasting API")

_model = None

def _get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(status_code=503, detail='Model not trained yet, run pipeline.py first')
        _model = joblib.load(MODEL_PATH)
    return _model


def _get_silo_capacity(df, site_id):
    site_rows = df[df['site_id'] == site_id]
    if site_rows.empty:
        return None
    return float(site_rows['silo_capacity'].iloc[-1])


class PredictionRequest(BaseModel):
    site_id: str = Field(examples=["SITE_001"])
    week_ending: str = Field(examples=["2025-01-12"], description="Future week this forecast is for")
    planned_pour_tonnes: float
    rain_mm: float
    avg_temp_c: float
    opening_inventory_tonnes: float
    deliveries_tonnes: float


class PredictionResponse(BaseModel):
    site_id: str
    week_ending: str
    forecasted_consumption: float


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    model = _get_model()

    df = load_data(DB_PATH)
    silo_capacity = _get_silo_capacity(df, request.site_id)
    if silo_capacity is None:
        raise HTTPException(status_code=404, detail=f'No data available for {request.site_id}')

    X = pd.DataFrame([{
        'planned_pour_tonnes': request.planned_pour_tonnes,
        'rain_mm': request.rain_mm,
        'avg_temp_c': request.avg_temp_c,
        'opening_inventory_tonnes': request.opening_inventory_tonnes,
        'deliveries_tonnes': request.deliveries_tonnes,
        'silo_capacity': silo_capacity,
    }])[EXOG_COLS]

    forecast = model.predict(X)[0]

    return PredictionResponse(
        site_id=request.site_id,
        week_ending=request.week_ending,
        forecasted_consumption=round(float(forecast), 2),
    )
