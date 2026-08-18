import json
import os
import urllib.error
import urllib.request
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="MIG Cement Demand Forecast")
st.title("MIG Cement Demand Forecast")
st.caption("Forecasts a site's cement consumption for a future week via the forecasting API.")

with st.form("predict_form"):
    site_id = st.text_input("Site ID", value="SITE_001")
    week_ending = st.date_input("Week ending")
    planned_pour_tonnes = st.number_input("Planned pour (tonnes)", min_value=0.0, value=300.0)
    rain_mm = st.number_input("Expected rain (mm)", min_value=0.0, value=0.0)
    avg_temp_c = st.number_input("Expected avg temp (°C)", value=15.0)
    opening_inventory_tonnes = st.number_input("Opening inventory (tonnes)", min_value=0.0, value=100.0)
    deliveries_tonnes = st.number_input("Expected deliveries (tonnes)", min_value=0.0, value=100.0)
    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "site_id": site_id,
        "week_ending": str(week_ending),
        "planned_pour_tonnes": planned_pour_tonnes,
        "rain_mm": rain_mm,
        "avg_temp_c": avg_temp_c,
        "opening_inventory_tonnes": opening_inventory_tonnes,
        "deliveries_tonnes": deliveries_tonnes,
    }
    request = urllib.request.Request(
        f"{API_URL}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read())
        st.metric("Forecasted consumption (tonnes)", f"{result['forecasted_consumption']:.2f}")
        st.caption(f"{result['site_id']} - week ending {result['week_ending']}")
    except urllib.error.HTTPError as e:
        detail = json.loads(e.read())
        st.error(detail.get("detail", "Request failed"))
    except urllib.error.URLError as e:
        st.error(f"Could not reach the forecasting API at {API_URL}: {e.reason}")
