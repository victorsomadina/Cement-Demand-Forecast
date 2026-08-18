import pytest
import pandas as pd
import inference
from fastapi.testclient import TestClient

# write a mock for the model
class DummyModel:
    def predict(self, X):
        return [42.0]

PAYLOAD={
    "site_id": "SITE_002",
    "week_ending": "2025-01-12",
    "planned_pour_tonnes": 120.0,
    "rain_mm": 15.0,
    "avg_temp_c": 27.5,
    "opening_inventory_tonnes": 80.0,
    "deliveries_tonnes": 70.0
}

@pytest.fixture
def client():
    return TestClient(inference.app)


def test_predict_endpoint(client, monkeypatch):
    monkeypatch.setattr(inference, "_get_model", lambda: DummyModel())
    monkeypatch.setattr(inference, "load_data", lambda db_path: pd.DataFrame({"site_id": ["SITE_002"], "silo_capacity": [500.0]}))

    response = client.post("/predict", json=PAYLOAD)
    body=response.json()

    assert response.status_code == 200
    assert "forecasted_consumption" in body
    assert body["site_id"] == "SITE_002"
    assert body["week_ending"] == "2025-01-12"
    assert body["forecasted_consumption"] == 42.0

