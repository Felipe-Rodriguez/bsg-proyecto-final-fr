import os
import json
import pytest
import pandas as pd
import numpy as np
from jsonschema import validate
from dotenv import load_dotenv

from src.transformers.bronze_to_silver import BronzeToSilverTransformer
from src.transformers.silver_to_gold import SilverToGoldTransformer

load_dotenv()

# Rutas relativas a los contratos de datos
silver_sch_path = os.getenv("SILVER_SCHEMA_PATH", "./data_contract/schema/silver_ventas.json")
gold_sch_path = os.getenv("GOLD_SCHEMA_PATH", "./data_contract/schema/gold_ventas.json")


def validate_schema(dataframe: pd.DataFrame, schema_path: str):
    """
    Convierte el DataFrame a registros nativos de Python y los valida
    contra el contrato JSON correspondiente.
    """
    if not os.path.exists(schema_path):
        pytest.skip(f"El esquema en {schema_path} no fue encontrado.")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # .to_json(orient='records') seguido de json.loads convierte tipos NumPy a tipos estándar de Python
    records = json.loads(dataframe.to_json(orient="records", date_format="iso"))

    for record in records:
        validate(instance=record, schema=schema)


@pytest.fixture
def sample_bronze_data():
    sales = pd.DataFrame([{
        "Store": 1,
        "Date": "05-02-2010",
        "Weekly_Sales": "1643690.90",
        "Holiday_Flag": 0,
        "Temperature": 42.31,
        "Fuel_Price": 2.572,
        "CPI": 211.0963582,
        "Unemployment": 8.106
    }])
    
    holidays = pd.DataFrame([{
        "date": "2010-02-05",
        "name": "Super Bowl"
    }])
    return sales, holidays


def test_bronze_to_silver_transformation(sample_bronze_data):
    ventas_raw, holidays_raw = sample_bronze_data
    transformer = BronzeToSilverTransformer()
    df_silver = transformer.transform(ventas_raw, holidays_raw)

    # 1. Aserciones funcionales
    assert len(df_silver) == 1
    assert df_silver["store_id"].iloc[0] == 1
    assert df_silver["event_date"].iloc[0] == "2010-02-05"
    assert df_silver["holiday_name"].iloc[0] == "Super Bowl"
    assert bool(df_silver["is_holiday"].iloc[0]) is False or isinstance(df_silver["is_holiday"].iloc[0], (bool, np.bool_))

    # 2. Validación de contrato de datos Silver
    validate_schema(df_silver, silver_sch_path)


def test_silver_to_gold_aggregation():
    silver_data = pd.DataFrame([
        {
            "store_id": 1,
            "event_date": "2010-02-05",
            "weekly_sales": 1000.0,
            "is_holiday": True,
            "temperature": 40.0,
            "fuel_price": 2.5,
            "cpi": 200.0,
            "unemployment_rate": 8.0,
            "holiday_name": "Super Bowl",
            "ingestion_date": "2024-01-01"
        },
        {
            "store_id": 1,
            "event_date": "2010-02-12",
            "weekly_sales": 2000.0,
            "is_holiday": True,
            "temperature": 42.0,
            "fuel_price": 2.6,
            "cpi": 200.0,
            "unemployment_rate": 8.0,
            "holiday_name": "Super Bowl",
            "ingestion_date": "2024-01-01"
        }
    ])
    transformer = SilverToGoldTransformer()
    df_gold = transformer.transform(silver_data)

    # 1. Aserciones funcionales
    assert len(df_gold) == 1
    assert df_gold["total_sales"].iloc[0] == 3000.0
    assert df_gold["avg_weekly_sales"].iloc[0] == 1500.0

    # 2. Validación de contrato de datos Gold
    validate_schema(df_gold, gold_sch_path)