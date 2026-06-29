import pandas as pd
import sqlite3
from dotenv import load_dotenv

load_dotenv()


def load_data():
    df = pd.read_csv("data/hr_data.csv", encoding="utf-8-sig")

    if "Attrition" in df.columns:
        df["AttritionFlag"] = df["Attrition"].apply(
            lambda x: 1 if str(x).strip() == "Yes" else 0)

    return df

def load_db(df):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("employees", conn, index=False, if_exists="replace")
    return conn


def get_schema(df):
    schema = "TABLE: employees\n\nCOLUMNS:\n"
    for col in df.columns:
        schema += f"  {col} ({df[col].dtype})\n"
    schema += f"\nSAMPLE ROWS (first 5):\n{df.head(5).to_string(index=False)}"
    return schema