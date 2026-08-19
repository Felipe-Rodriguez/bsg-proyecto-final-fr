# Walmart Retail Analytics Data Pipeline

## 1. Resumen del Problema
La empresa de retail Walmart, necesita analizar el impacto de la inflación, el desempleo y fechas festivas sobre el volumen de ventas semanales de sus tiendas para así mejorar la planificación de inventarios y presupuestos operativos.

## 2. Arquitectura Lógica
El pipeline sigue la **Arquitectura Medallion (Bronze -> Silver -> Gold)**, consumiendo datos desde múltiples fuentes (CSV y API de días festivos), almacenando las capas de la arquitectura en Google Cloud Storage (en formato Parquet) y presentando la información en Google BigQuery.

## 3. Cómo Ejecutar
1. Clonar repositorio `git clone https://github.com/<tu-usuario>/bsg-proyecto-final-fr.git` desde Cloud Shell (autotizar esta última)
2. Pocisionarte en: `cd bsg-proyecto-final-fr/cloud/`
2. Crear Bucket en Cloud Storage (con región us-central1).
3. Crear carpeta `landing` en bucket.
4. Crear DataSet en BigQuery `bsg_walmart`.
6. Guardar ID del proyecto: `PROJECT_ID="TU_PROJECT_ID"`
7. Obtener el número de Proyecto para las cuentas de servicio: `PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")`
8. Se da permiso a Cloud Storage para notificar cuando se suba un archivo: 
```code
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"
```
9. Se da permiso a la cuenta de servicio para recibir la notificación de la carga de archivos: 
```code
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/eventarc.eventReceiver"
```
10. Desplegar Cloud Function:
```code
gcloud functions deploy walmart-etl-pipeline \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=run_pipeline_gcp \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=TU_BUCKET_AQUI" \
  --memory=1024MB \
  --timeout=300s \
  --set-env-vars GCP_PROJECT_ID=TU_PROJECT_ID,BQ_DATASET=bsg_walmart,BQ_TABLE_GOLD=holiday_sales_impact
```
11. Entra al bucket creado y sube el CSV "Walmart.csv" en la carpeta `landing`
12. Recargar Cloud Storage y BigQuery para observar la creación de los archivos.
13. Si se dirige a "Cloud Run -> Servicios -> walmart-etl-pipeline(u otro nombre si se cambio) -> Registros" se puede observar los logs del pipeline.

## 4. Estructura de Datos
- **Bronze:** `bronze/walmart_sales/` y `bronze/holidays_api/` (datos raw en Parquet).
- **Silver:** `silver/walmart_sales_curated/` (datos limpios, tipados y cruzados).
- **Gold:** `gold/bsg_walmart/` y Tabla BigQuery `holiday_sales_impact` (métricas agregadas por tienda, año y festividad).

## 5. Decisiones Clave
- **Formato Parquet:** La compresión de estos archivos es eficiente y de bajo peso comparado con csv y, además, cuenta con tipado nativo columnar.
- **Eventarc:** Permite la detección de eventos y orquestar un flujo con base a esta acción (en este caso detectar la ingesta de CSVs).
- **Cloud Function:** Procesamiento de la información y monitoreo mediante logs.

## 6. Costos y Seguridad
- Acceso restringido por roles mínimos necesarios en Service Account IAM.
- Componentes serverless, cobro por segundos de ejecución los cuales son bajos en este requerimiento.