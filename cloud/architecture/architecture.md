# Diagrama de arquitectura del Pipeline
```mermaid
graph LR
    %% Actores externos
    User([Usuario / Sistema]):::user
    API[Holiday API <br/> date.nager.at]:::api

    %% Entorno GCP
    subgraph Google Cloud Platform
        direction LR
        
        subgraph Data Lake - Cloud Storage
            direction TB
            Landing[(Landing Zone <br/> Walmart.csv)]:::storage
            Bronze[(Bronze Layer <br/> Raw Parquet)]:::storage
            Silver[(Silver Layer <br/> Curated Parquet)]:::storage
            GoldGCS[(Gold Layer <br/> Aggregated Parquet)]:::storage
        end

        Eventarc((Eventarc <br/> Trigger)):::gcp
        CF[Cloud Function Gen 2 <br/> ETL Pipeline Python]:::gcp
        
        subgraph Data Warehouse
            BQ[(BigQuery <br/> holiday_sales_impact)]:::bq
        end
    end

    %% Flujo del proceso
    User -- "1. Sube CSV" --> Landing
    Landing -- "2. Evento Finalized" --> Eventarc
    Eventarc -- "3. Dispara ejecución" --> CF
    CF -- "4. Extrae festividades" --> API
    API -- "Respuesta JSON" --> CF
    
    CF -- "5. Guarda Raw" --> Bronze
    CF -- "6. Guarda Curated" --> Silver
    CF -- "7. Guarda Aggregated" --> GoldGCS
    CF -- "8. Carga Tabla Gold" --> BQ
```

# Decisiones de diseño
## 1. Eventarc como orquestador
**Decisión:** Usar Eventarc como orquestador.  
**Justificación:**
- Permite la detección de eventos y orquestar un flujo con base a esta acción (en este caso detectar la ingesta de CSVs).
- Utilizar Apache Airflow en Cloud Composer puede ser caro.

## 2. Cloud Function como procesador de la información
**Decisión:** Usar Cloud Function para procesar la información del pipeline.  
**Justificación:**
- La migración de pipeline local es más sencilla hacía esta herramienta.
- Se encadenan los los pasos del script del pipeline ligado al evento.
- Permite el consumo de APIs externas.

## 3. Nube GCP
**Decisión:** Se utilizó la nube de GCP.  
**Justificación:**
- Es la nube con la que cuento con mayor experiencia y puedo desarrollar un mejor pipeline.