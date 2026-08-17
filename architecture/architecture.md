# Diseño Lógico del Pipeline
```mermaid
graph LR
    A[(MongoDB Local / Docker)] -->|"Extracción (E)"| D[Airflow Orquestador / main.py]
    B[API Public Holidays] -->|"Extracción (E)"| D
    D -->|Carga Raw Parquet| E[(GCS Bronze Bucket)]
    E -->|"Transformación (T)"| F[(GCS Silver Bucket)]
    F -->|"Carga (L)"| G[(BigQuery Gold Table)]