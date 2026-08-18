import sqlite3
import pandas as pd


def load_data(db_path = "../data/MIG_Cement_Records.db"):
    conn = sqlite3.connect(db_path)

    query = """SELECT
            o.date, o.site_id, s.region, s.behavior, o.cement_type, o.planned_pour_tonnes, o.consumed_tonnes, o.opening_inventory_tonnes, o.deliveries_tonnes, o.closing_inventory_tonnes, o.rain_mm, o.avg_temp_c, o.silo_capacity
            FROM
            Operations o
            JOIN Sites s ON o.site_id = s.site_id
            """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df