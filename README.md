# Walmart Retail Analytics Data Pipeline

## 1. Resumen del Problema
La empresa de retail Walmart, necesita analizar el impacto de la inflación, el desempleo y fechas festivas sobre el volumen de ventas semanales de sus tiendas para así mejorar la planificación de inventarios y presupuestos operativos.

## 2. Arquitectura Lógica
El pipeline sigue la **Arquitectura Medallion (Bronze -> Silver -> Gold)**, consumiendo datos desde múltiples fuentes (MongoDB y API de días festivos), almacenando las capas de la arquitectura en Google Cloud Storage (en formato Parquet) y presentando la información en Google BigQuery.

## 3. Cómo Ejecutar
### Requisitos previos
- Python 3.12 instalado.
- Git instalado.
- Docker Desktop.

### Modo Local:
1. Clonar repositorio `git clone https://github.com/<tu-usuario>/bsg-proyecto-final-fr.git`
2. Instalar dependencias: `make install`
3. Configurar variables en .env: `cp .env.example .env`.
4. Ejecutar tests: `make test`
5. Correr pipeline: `make run-local`

### Modo Cloud (GCP):
1. Clonar repositorio `git clone https://github.com/<tu-usuario>/bsg-proyecto-final-fr.git`
2. Instalar dependencias: `make install`
3. Configurar variables en .env: `cp .env.example .env`.
4. Crear Bucket en Cloud Storage.
5. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
6. Crear DataSet en BigQuery.
7. Ejecutar tests: `make test`
8. Correr pipeline: `make run-cloud`

### Modo Hybrid (Local y GCP):
1. Clonar repositorio `git clone https://github.com/<tu-usuario>/bsg-proyecto-final-fr.git`
2. Instalar dependencias: `make install`
3. Configurar variables en .env: `cp .env.example .env`.
4. Crear docker con MongoDB en Docker Desktop: `docker run -d --name mongodb-walmart -p 27017:27017 -v mongo_data:/data/db mongo:latest`
5. Iniciar contenedor de base de datos: `docker start mongodb-walmart`
6. Cargar csv a Mongodb: `make ingest-mongodb`
7. Crear Bucket en Cloud Storage.
8. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
9. Crear DataSet en BigQuery.
10. Ejecutar tests: `make test`
11. Correr pipeline: `make run-hybrid`

### En Airflow (Nube):
1. Clonar repositorio `git clone https://github.com/<tu-usuario>/bsg-proyecto-final-fr.git`
2. Instalar dependencias: `make install`
3. Configurar variables en .env: `cp .env.example .env`.
4. Crear docker con MongoDB en Docker Desktop: `docker run -d --name mongodb-walmart -p 27017:27017 -v mongo_data:/data/db mongo:latest`
5. Iniciar contenedor de base de datos: `docker start mongodb-walmart`
6. Cargar csv a Mongodb: `make ingest-mongodb`
7. Crear Bucket en Cloud Storage.
8. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
9. Crear DataSet en BigQuery.
10. Ejecutar tests: `make test`
11. Instalar airflow: `make airflow-install`
12. Inicializar BD: `make airflow-init`
13. Activar entorno virtual: `source .venv/bin/activate`
14. Crear usuario: airflow users create --username admin --firstname Nombre(s) --lastname Apellido(s) --role Admin --email email@ejemplo.com --password admin123
15. Desactivar entorno virtual: `deactivate`
16. Iniciar Airflow: `make airflow-run`
17. Acceder a: `http://localhost:8081/`
18. Buscar y ejecutar DAG: `walmart_etl_dag`

## 4. Estructura de Datos
- **Bronze:** `bronze/walmart_sales/` y `bronze/holidays_api/` (datos raw en Parquet).
- **Silver:** `silver/walmart_sales_curated/` (datos limpios, tipados y cruzados).
- **Gold:** `gold/bsg_walmart/` y Tabla BigQuery `holiday_sales_impact` (métricas agregadas por tienda, año y festividad).

## 5. Decisiones Clave
- **Formato Parquet:** La compresión de estos archivos es eficiente y de bajo peso comparado con csv y, además, cuenta con tipado nativo columnar.
- **Contratos de Datos:** Esquemas JSON formales para garantizar la estructura de las tablas entre capas.
- **Apache Airflow:** Plataforma de orquestación que permite el monitoreo y ejecución de un pipeline de datos.
- **Makefile:** Estandarización de comandos para una re-ejecución sencilla (`install`, `test`, `run`).

## 6. Costos y Seguridad
- Acceso restringido por roles mínimos necesarios en Service Account IAM.
- Variables sensibles y credenciales protegidas vía `.env` y excluidas del control de versiones (`.gitignore`).