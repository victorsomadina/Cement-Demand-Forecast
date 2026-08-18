import numpy as np
import pandas as pd

FEATURES = [
    'planned_pour_tonnes', 'rain_mm', 'avg_temp_c',
    'deliveries_tonnes', 'opening_inventory_tonnes','silo_capacity'
]

AGG_RULES = {
    'consumed_tonnes': 'sum',
    'planned_pour_tonnes': 'sum',
    'deliveries_tonnes': 'sum',
    'opening_inventory_tonnes': 'first',
    'rain_mm': 'sum',
    'avg_temp_c': 'mean',
    'silo_capacity': 'last',
}

EXOG_COLS = [
    'planned_pour_tonnes', 'rain_mm', 'avg_temp_c',
    'opening_inventory_tonnes', 'deliveries_tonnes', 'silo_capacity',
]


def resample_weekly(df, site_id):
    site_df = df[df['site_id'] == site_id].copy()
    site_df['date'] = pd.to_datetime(site_df['date'])
    site_df = site_df.set_index('date').sort_index()
    return site_df.resample('W').agg(AGG_RULES)


def build_weekly_panel(df, site_ids=None, test_size=0.2):
    site_ids = site_ids or sorted(df['site_id'].unique())
    train_frames, test_frames = [], []

    for site_id in site_ids:
        weekly = resample_weekly(df, site_id)
        split_index = int(len(weekly) * (1 - test_size))
        train_frames.append(weekly.iloc[:split_index])
        test_frames.append(weekly.iloc[split_index:])

    return pd.concat(train_frames), pd.concat(test_frames)