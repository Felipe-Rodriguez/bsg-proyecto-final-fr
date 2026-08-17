from airflow.decorators import dag, task
from datetime import datetime, timedelta

from src.extractors.mongo_extractor import MongoVentasExtractor
from src.extractors.api_extractor import HolidayAPIExtractor
from src.transformers.bronze_to_silver import BronzeToSilverTransformer
from src.transformers.silver_to_gold import SilverToGoldTransformer
from src.loaders.gcs_loader import GCSLoader
from src.loaders.bigquery_loader import BigQueryLoader

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
    def extract_and_load_bronze(**kwargs):
        exec_date = kwargs['ds_nodash']
        # Extracción
        sales_raw = MongoVentasExtractor().extract_ventas()
        holidays_raw = HolidayAPIExtractor().extract_holidays()
        # Carga Bronze
        loader = GCSLoader()
        loader.upload_parquet(sales_raw, f"bronze/walmart_sales/sales_{exec_date}.parquet")
        loader.upload_parquet(holidays_raw, f"bronze/holidays_api/holidays_{exec_date}.parquet")

    @task
    def transform_and_load_silver(**kwargs):
        exec_date = kwargs['ds_nodash']
        sales_raw = MongoVentasExtractor().extract_ventas()
        holidays_raw = HolidayAPIExtractor().extract_holidays()
        
        # Transformación Bronze -> Silver
        transformer = BronzeToSilverTransformer()
        df_silver = transformer.transform(sales_raw, holidays_raw)
        
        # Carga Silver
        loader = GCSLoader()
        loader.upload_parquet(df_silver, f"silver/walmart_sales_curated/sales_curated_{exec_date}.parquet")
    
    @task
    def transform_and_load_gold(**kwargs):
        sales_raw = MongoVentasExtractor().extract_ventas()
        holidays_raw = HolidayAPIExtractor().extract_holidays()
        df_silver = BronzeToSilverTransformer().transform(sales_raw, holidays_raw)
        
        # Transformación Silver -> Gold
        df_gold = SilverToGoldTransformer().transform(df_silver)
        
        # Carga Gold BigQuery
        bq_loader = BigQueryLoader()
        bq_loader.load_table(df_gold)

    bronze = extract_and_load_bronze()
    silver = transform_and_load_silver()
    gold = transform_and_load_gold()

    bronze >> silver >> gold

task_flow()