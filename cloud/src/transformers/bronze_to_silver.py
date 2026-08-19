import pandas as pd
from datetime import datetime, timezone

PIPELINE_VERSION = "1.0.0"

class BronzeToSilverTransformer:
    def __init__(self):
        pass

    def transform(self, df_ventas_raw: pd.DataFrame, df_holidays_raw: pd.DataFrame) -> pd.DataFrame:
        
        df_ventas = df_ventas_raw.copy()
        df_holidays = df_holidays_raw.copy()

        # Se renombran las columnas usando snake_case y minúsculas
        df_ventas = df_ventas.rename(columns={
            "Store": "store_id",
            "Date": "event_date",
            "Weekly_Sales": "weekly_sales",
            "Holiday_Flag": "is_holiday",
            "Temperature": "temperature",
            "Fuel_Price": "fuel_price",
            "CPI": "cpi",
            "Unemployment": "unemployment_rate"
        })

        # Conversión de fechas a formato YYYY-MM-DD
        df_ventas["event_date"] = pd.to_datetime(df_ventas["event_date"], format="%d-%m-%Y").dt.strftime("%Y-%m-%d")
        
        if not df_holidays.empty and "date" in df_holidays.columns:
            df_holidays["date"] = pd.to_datetime(df_holidays["date"]).dt.strftime("%Y-%m-%d")

            # Solo se necesita la fecha y el nombre de la festividad para este ejercicio
            df_holidays = df_holidays[["date", "name"]].rename(columns={"date": "event_date", "name": "holiday_name"})

            # Eliminación de duplicados de fecha en festividades
            df_holidays = df_holidays.drop_duplicates(subset=["event_date"])

            # INNER JOIN con el dataframe de las festividades
            df_silver = pd.merge(df_ventas, df_holidays, on="event_date", how="left")
        else:
            df_silver = df_ventas
            df_silver["holiday_name"] = None

        # Conversiones para seguir con el data contract de silver
        df_silver["store_id"] = df_silver["store_id"].astype(int)
        df_silver["weekly_sales"] = df_silver["weekly_sales"].astype(float)
        df_silver["is_holiday"] = df_silver["is_holiday"].astype(int).astype(bool)
        df_silver["temperature"] = df_silver["temperature"].astype(float)
        df_silver["fuel_price"] = df_silver["fuel_price"].astype(float)
        df_silver["cpi"] = df_silver["cpi"].astype(float)
        df_silver["unemployment_rate"] = df_silver["unemployment_rate"].astype(float)
        
        # Eliminar nulos y duplicados
        df_silver = df_silver.dropna(subset=["store_id", "event_date", "weekly_sales"])
        df_silver = df_silver.drop_duplicates(subset=["store_id", "event_date"])

        # Metadato de auditoría
        df_silver["_ingestion_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        df_silver["_pipeline_version"] = PIPELINE_VERSION
        df_silver["_source"] = "etl_walmart_retail"
        return df_silver

if __name__ == "__main__":
    from src.extractors.mongo_extractor import MongoVentasExtractor
    from src.extractors.api_extractor import HolidayAPIExtractor

    print("--- Extrayendo datos de prueba ---")
    sales_raw = MongoVentasExtractor().extract_ventas()
    holidays_raw = HolidayAPIExtractor().extract_holidays()

    print("--- Transformando Bronze -> Silver ---")
    transformer = BronzeToSilverTransformer()
    df_silver = transformer.transform(sales_raw, holidays_raw)
    
    print(f"Registros en Silver: {len(df_silver)}")
    print(df_silver.head())
    print("\nTipos de datos Silver:")
    print(df_silver.dtypes)