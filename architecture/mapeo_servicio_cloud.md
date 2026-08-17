# Mapeo a Servicios Cloud (GCP)
- **Ingesta:** MongoDB (Docker) y API
- **Orquestación:** Python 3.12 / Apache Airflow.
- **Capa Bronze:** Google Cloud Storage (gs://<bucket>/bronze/) en formato Parquet.
- **Capa Silver:** Google Cloud Storage (gs://<bucket>/silver/) con tipado estricto y enriquecimiento.
- **Capa Gold:** Google BigQuery (bsg_walmart.holiday_sales_impact).