import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

class BigQueryLoader:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("BQ_DATASET", "bsg_walmart")
        self.table_name = os.getenv("BQ_TABLE_GOLD", "holiday_sales_impact")
        self.client = bigquery.Client(project=self.project_id)

    def load_table(self, df: pd.DataFrame, write_disposition: str = "WRITE_TRUNCATE"): # Se usó WRITE_TRUNCATE con el objetivo de lograr la idempotencia

        # Cargar un el df gold hacia una tabla en BQ
        table_id = f"{self.project_id}.{self.dataset_id}.{self.table_name}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True
        )
        
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Esperar a que finalice la carga
        print(f" [BigQuery] {len(df)} registros cargados exitosamente en: {table_id}")