import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error
from data_loader import load_data
from preprocessing import EXOG_COLS, build_weekly_panel

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "..", "data", "MIG_Cement_Records.db")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "rf_all.pkl")

def train(df):
    train_panel, test_panel = build_weekly_panel(df)

    X_train, y_train = train_panel[EXOG_COLS], train_panel['consumed_tonnes']
    X_test, y_test = test_panel[EXOG_COLS], test_panel['consumed_tonnes']

    rf = RandomForestRegressor(n_estimators=300, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    mask = y_test != 0
    mape = mean_absolute_percentage_error(y_test[mask], y_pred[mask])
    print(f'Random Forest (entire dataset, weekly) MAPE: {mape:.3f}')

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(rf, MODEL_PATH)

    return rf, mape


if __name__ == '__main__':
    df = load_data(DB_PATH)
    train(df)
