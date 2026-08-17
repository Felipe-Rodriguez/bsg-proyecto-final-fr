import argparse
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone
from src.extractors.mongo_extractor import MongoVentasExtractor
from src.extractors.api_extractor import HolidayAPIExtractor
from src.transformers.bronze_to_silver import BronzeToSilverTransformer
from src.transformers.silver_to_gold import SilverToGoldTransformer
from src.loaders.gcs_loader import GCSLoader
from src.loaders.bigquery_loader import BigQueryLoader

load_dotenv()

def run_pipeline(mode: str = "hybrid"):
    execution_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    execution_time = datetime.now(timezone.utc).strftime("%H%M%S")

    print(f"=========================================")
    print(f" INICIANDO PIPELINE ETL - MODO: {mode.upper()}")
    print(f"=========================================")

    # Etapa de Extracción (E) según el modo deseado
    if mode == "local":
        mongodb_path = os.getenv("INPUT_FILE_PATH_MONGODB", "./data_samples/Walmart.csv")
        api_path = os.getenv("INPUT_FILE_PATH_API", "./data_samples/Holidays.csv")
        print(f"\n=====================================================================")
        print(" -> [Extracción] Leyendo CSV local de MongoDB y CSV Local de API ...")
        print(f"=====================================================================")
        df_ventas_raw = pd.read_csv(mongodb_path)
        df_holidays_raw = pd.read_csv(api_path)
        print(f"Etapa de extracción (E) completada, con {len(df_ventas_raw)} registros de ventas y {len(df_holidays_raw)} registros de festividades.")
    elif mode == "cloud":
        print(f"\n===============================================================")
        print(" -> [Extracción] Leyendo fuentes directas desde GCS y API...")
        print(f"===============================================================")
        gcs_path = f"gs://{os.getenv('GCS_BUCKET')}/landing/Walmart.csv"
        df_ventas_raw = pd.read_csv(gcs_path)
        df_holidays_raw = HolidayAPIExtractor().extract_holidays()
        print(f"Etapa de extracción (E) completada, con {len(df_ventas_raw)} registros de ventas y {len(df_holidays_raw)} registros de festividades.")
    else: # hybrid
        print(f"\n============================================================")
        print(" -> [Extracción] Extrayendo desde MongoDB local y API...")
        print(f"============================================================")
        df_ventas_raw = MongoVentasExtractor().extract_ventas()
        df_holidays_raw = HolidayAPIExtractor().extract_holidays()
        print(f"Etapa de extracción (E) completada, con {len(df_ventas_raw)} registros de ventas y {len(df_holidays_raw)} registros de festividades.")

    # Etapa de Transformación (T)
    print(f"\n=========================================================")
    print(" -> [Transformación] Procesando capas Silver y Gold...")
    print(f"=========================================================")
    df_silver = BronzeToSilverTransformer().transform(df_ventas_raw, df_holidays_raw)
    df_gold = SilverToGoldTransformer().transform(df_silver)
    print(f"Etapa de transformación (T) completada, con {len(df_silver)} registros de la capa silver y {len(df_gold)} registros de la capa gold.")

    # Etapa de Carga (L) según el modo deseado
    if mode == "local":
        out_dir = os.getenv("OUTPUT_DIR", "./out")
        os.makedirs(f"{out_dir}/bronze", exist_ok=True)
        os.makedirs(f"{out_dir}/silver", exist_ok=True)
        os.makedirs(f"{out_dir}/gold", exist_ok=True)
        
        df_ventas_raw.to_parquet(f"{out_dir}/bronze/sales_raw.parquet", index=False)
        df_holidays_raw.to_parquet(f"{out_dir}/bronze/holidays_raw.parquet", index=False)
        df_silver.to_parquet(f"{out_dir}/silver/sales_curated.parquet", index=False)
        df_gold.to_parquet(f"{out_dir}/gold/holiday_sales_impact.parquet", index=False)
        print(f"\n===============================================================")
        print(f" -> [Carga Local] Archivos Parquet guardados en {out_dir}/")
        print(f"===============================================================")
        print(f"Etapa de carga (L) completada, se cargó correctamente la tabla holiday_sales_impact con {len(df_gold)} registros.")
    else:
        # Modos hybrid y cloud guardan en GCS y BigQuery
        gcs_loader = GCSLoader()
        bq_loader = BigQueryLoader()

        gcs_loader.upload_parquet(df_ventas_raw, f"bronze/walmart_sales/event_date={execution_date}/sales_{execution_time}.parquet")
        gcs_loader.upload_parquet(df_holidays_raw, f"bronze/holidays_api/event_date={execution_date}/holidays_{execution_time}.parquet")
        gcs_loader.upload_parquet(df_silver, f"silver/walmart_sales_curated/event_date={execution_date}/sales_curated_{execution_time}.parquet")
        gcs_loader.upload_parquet(df_gold, f"gold/bsg_walmart/event_date={execution_date}/holiday_sales_impact_{execution_time}.parquet")
        print(f"\n=====================================================================")
        print(" -> [Carga Cloud] Datos almacenados exitosamente en GCS y BigQuery")
        print(f"=====================================================================")
        bq_loader.load_table(df_gold)
        print(f"Etapa de carga (L) completada, se cargó correctamente la tabla holiday_sales_impact con {len(df_gold)} registros.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=os.getenv("EXECUTION_MODE", "hybrid"), choices=["local", "hybrid", "cloud"])
    args = parser.parse_args()
    run_pipeline(mode=args.mode)