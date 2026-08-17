# Walmart Retail Analytics Data Pipeline

## 1. Resumen del Problema
La empresa de retail Walmart, necesita analizar el impacto de la inflación, el combustible, el desempleo y fechas festivas sobre el volumen de ventas semanales de sus tiendas para así mejorar la planificación de inventarios y presupuestos operativos.

## 2. Arquitectura Lógica
El pipeline sigue la **Arquitectura Medallion (Bronze -> Silver -> Gold)**, consumiendo datos desde múltiples fuentes (MongoDB y API de días festivos), almacenando las capas de la arquitectura en Google Cloud Storage (en formato Parquet) y presentando la información en Google BigQuery.

## 3. Cómo Ejecutar
### Modo Local:
1. Clonar repositorio y configurar variables en `.env`.
2. Iniciar contenedor de base de datos: `docker start mongodb-walmart`
3. Instalar dependencias: `make install`
4. Ejecutar tests: `make test`
5. Correr pipeline: `make run-local`

### Modo Cloud (GCP):
1. Clonar repositorio y configurar variables en `.env`.
2. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
3. Instalar dependencias: `make install`
4. Ejecutar tests: `make test`
5. Correr pipeline: `make run-cloud`

### Modo Hybrid (Local y GCP):
1. Clonar repositorio y configurar variables en `.env`.
2. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
3. Instalar dependencias: `make install`
4. Ejecutar tests: `make test`
5. Correr pipeline: `make run-hybrid`

### En Airflow (Nube):
1. Clonar repositorio y configurar variables en `.env`.
2. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
3. Instalar dependencias: `make install`
4. Ejecutar tests: `make test`
5. Instalar airflow: `make airflow-install`
6. Inicializar BD: `make airflow-init`
7. Crear usuario: airflow users create --username admin --firstname Nombre(s) --lastname Apellido(s) --role Admin --email email@ejemplo.com --password admin123
8. Iniciar Airflow: `make airflow-run`
9. Acceder a: `http://localhost:8081/`
10. Buscar y ejecutar DAG: `walmart_etl_dag`

## 4. Estructura de Datos
* **Bronze:** `bronze/walmart_sales/` y `bronze/holidays_api/` (datos raw en Parquet).
* **Silver:** `silver/walmart_sales_curated/` (datos limpios, tipados y cruzados).
* **Gold:** Tabla BigQuery `holiday_sales_impact` (métricas agregadas por tienda, año y festividad).

## 5. Decisiones Clave
* **Formato Parquet:** La compresión de estos archivos es eficiente y de bajo peso comparado con csv y, además, cuenta con tipado nativo columnar.
* **Contratos de Datos:** Esquemas JSON formales para garantizar consistencia entre capas.
* **Apache Airflow:** Plataforma de orquestación que permite el monitoreo y ejecución de un pipeline de datos.
* **Makefile:** Estandarización de comandos para una re-ejecución sencilla (`install`, `test`, `run`).

## 6. Costos y Seguridad
* Acceso restringido por roles mínimos necesarios en Service Account IAM.
* Variables sensibles y credenciales protegidas vía `.env` y excluidas del control de versiones (`.gitignore`).