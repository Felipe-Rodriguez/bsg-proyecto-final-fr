import os
import pandas as pd
import functions_framework
from datetime import datetime, timezone

from src.extractors.api_extractor import HolidayAPIExtractor
from src.transformers.bronze_to_silver import BronzeToSilverTransformer
from src.transformers.silver_to_gold import SilverToGoldTransformer
from src.loaders.gcs_loader import GCSLoader
from src.loaders.bigquery_loader import BigQueryLoader

@functions_framework.cloud_event
def run_pipeline_gcp(cloud_event):
    # Cloud function que se ejecuta solo cuando se sube un archivo csv
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    # Solo se ejecuta el pipeline cuando el archivo cae en la carpeta "landing" y es un CSV
    if not file_name.startswith("landing/") or not file_name.endswith(".csv"):
        print(f"Archivo ignorado: {file_name}. Solo se procesan CSVs en landing/")
        return

    execution_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    execution_time = datetime.now(timezone.utc).strftime("%H%M%S")

    print(f"=========================================")
    print(f" INICIANDO PIPELINE ETL - MODO: CLOUD")
    print(f" Archivo detectado: gs://{bucket_name}/{file_name}")
    print(f"=========================================")

    # 1. Etapa de Extracción (E)
    print(" -> [Extracción] Leyendo CSV desde GCS y consumiendo API...")
    gcs_path = f"gs://{bucket_name}/{file_name}"

    df_ventas_raw = pd.read_csv(gcs_path)
    df_holidays_raw = HolidayAPIExtractor().extract_holidays()
    print(f"Extracción completada: {len(df_ventas_raw)} ventas, {len(df_holidays_raw)} festividades.")

    # 2. Etapa de Transformación (T)
    print(" -> [Transformación] Procesando capas Silver y Gold...")
    df_silver = BronzeToSilverTransformer().transform(df_ventas_raw, df_holidays_raw)
    df_gold = SilverToGoldTransformer().transform(df_silver)
    print(f"Transformación completada: Silver ({len(df_silver)}), Gold ({len(df_gold)}).")

    # 3. Etapa de Carga (L)
    print(" -> [Carga] Iniciando carga a GCS y BigQuery...")
    # Se setea la variable de entorno para los loaders
    os.environ["GCS_BUCKET"] = bucket_name 
    
    gcs_loader = GCSLoader()
    bq_loader = BigQueryLoader()

    gcs_loader.upload_parquet(df_ventas_raw, f"bronze/walmart_sales/event_date={execution_date}/sales_{execution_time}.parquet")
    gcs_loader.upload_parquet(df_holidays_raw, f"bronze/holidays_api/event_date={execution_date}/holidays_{execution_time}.parquet")
    gcs_loader.upload_parquet(df_silver, f"silver/walmart_sales_curated/event_date={execution_date}/sales_curated_{execution_time}.parquet")
    gcs_loader.upload_parquet(df_gold, f"gold/bsg_walmart/event_date={execution_date}/holiday_sales_impact_{execution_time}.parquet")
    
    bq_loader.load_table(df_gold)
    print("=====================================================================")
    print(" -> PIPELINE FINALIZADO EXITOSAMENTE")
    print("=====================================================================")