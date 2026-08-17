import os
from airflow.decorators import dag, task
from datetime import datetime, timedelta, timezone
import pandas as pd
from dotenv import load_dotenv

from src.extractors.mongo_extractor import MongoVentasExtractor
from src.extractors.api_extractor import HolidayAPIExtractor
from src.transformers.bronze_to_silver import BronzeToSilverTransformer
from src.transformers.silver_to_gold import SilverToGoldTransformer
from src.loaders.gcs_loader import GCSLoader
from src.loaders.bigquery_loader import BigQueryLoader

load_dotenv()

# Bucket
gsc_bucket = os.getenv('GCS_BUCKET')

# Tiempos de ejecución
execution_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
execution_time = datetime.now(timezone.utc).strftime("%H%M%S")

default_args = {
    'owner': 'felipe-rdz',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

@dag(
    dag_id='walmart_etl_dag',
    default_args=default_args,
    description='Pipeline ETL para la empresa Walmart: MongoDB(csv) + API -> GCS -> BigQuery',
    start_date=datetime(2026, 8, 16),
    schedule=None,
    catchup=False,
    tags=["ETL","BSG","CLOUD","WALMART"]
)

def task_flow():

    @task
    def extract():
        # Extracción
        sales_raw = MongoVentasExtractor().extract_ventas()
        holidays_raw = HolidayAPIExtractor().extract_holidays()

        # Carga Bronze a GCS
        bronze_sales_path = f"bronze/walmart_sales/event_date={execution_date}/sales_{execution_time}.parquet"
        bronze_holidays_path = f"bronze/holidays_api/event_date={execution_date}/holidays_{execution_time}.parquet"

        loader = GCSLoader()
        loader.upload_parquet(sales_raw, bronze_sales_path)
        loader.upload_parquet(holidays_raw, bronze_holidays_path)

        return {
            "bronze_sales_path": f"gs://{gsc_bucket}/{bronze_sales_path}",
            "bronze_holidays_path": f"gs://{gsc_bucket}/{bronze_holidays_path}"
        }

    @task
    def transform(paths):
        sales_raw = pd.read_parquet(paths["bronze_sales_path"])
        holidays_raw = pd.read_parquet(paths["bronze_holidays_path"])
        
        # Transformación Bronze -> Silver
        transformer = BronzeToSilverTransformer()
        df_silver = transformer.transform(sales_raw, holidays_raw)
        # Transformación Silver -> Gold
        df_gold = SilverToGoldTransformer().transform(df_silver)
        
        # Carga Silver y Gold a GCS
        silver_sales_curated_path = f"silver/walmart_sales_curated/event_date={execution_date}/sales_curated_{execution_time}.parquet"
        gold_table_path = f"gold/bsg_walmart/event_date={execution_date}/holiday_sales_impact_{execution_time}.parquet"

        loader = GCSLoader()
        loader.upload_parquet(df_silver, silver_sales_curated_path)
        loader.upload_parquet(df_gold, gold_table_path)

        return f"gs://{gsc_bucket}/{gold_table_path}"
    
    @task
    def load(gold_path):
        df_gold = pd.read_parquet(gold_path)
        
        # Carga Gold BigQuery
        bq_loader = BigQueryLoader()
        bq_loader.load_table(df_gold)

    e = extract()
    t = transform(paths=e)
    l = load(gold_path=t)

    e >> t >> l

task_flow()