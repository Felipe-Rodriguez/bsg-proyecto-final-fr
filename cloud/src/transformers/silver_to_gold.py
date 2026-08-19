import pandas as pd

class SilverToGoldTransformer:
    def __init__(self):
        pass

    def transform(self, df_silver: pd.DataFrame) -> pd.DataFrame:
        
        df = df_silver.copy()
        
        # Extraer el año del evento
        df["year"] = pd.to_datetime(df["event_date"]).dt.year
        
        # Lenar la información para los días no festivos
        df["holiday_name"] = df["holiday_name"].fillna("Regular Week")

        # Agregaciones analíticas por Tienda, Año y Festividad
        df_gold = df.groupby(["store_id", "year", "holiday_name"], as_index=False).agg(
            total_sales=("weekly_sales", "sum"),
            avg_weekly_sales=("weekly_sales", "mean"),
            avg_cpi=("cpi", "mean"),
            avg_unemployment=("unemployment_rate", "mean")
        )

        # Redondeo de las agregaciones calculadas
        df_gold["total_sales"] = df_gold["total_sales"].round(2)
        df_gold["avg_weekly_sales"] = df_gold["avg_weekly_sales"].round(4)
        df_gold["avg_cpi"] = df_gold["avg_cpi"].round(4)
        df_gold["avg_unemployment"] = df_gold["avg_unemployment"].round(4)

        return df_gold

if __name__ == "__main__":
    from src.extractors.mongo_extractor import MongoVentasExtractor
    from src.extractors.api_extractor import HolidayAPIExtractor
    from src.transformers.bronze_to_silver import BronzeToSilverTransformer

    ventas_raw = MongoVentasExtractor().extract_ventas()
    holidays_raw = HolidayAPIExtractor().extract_holidays()
    df_silver = BronzeToSilverTransformer().transform(ventas_raw, holidays_raw)

    print("--- Transformando Silver -> Gold ---")
    transformer_gold = SilverToGoldTransformer()
    df_gold = transformer_gold.transform(df_silver)

    print(f"Registros en Gold: {len(df_gold)}")
    print(df_gold.head(10))