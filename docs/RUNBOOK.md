# Cómo Re-ejecutar el Pipeline

## Modo Local:
1. Clonar repositorio y configurar variables en `.env`.
2. Iniciar contenedor de base de datos: `docker start mongodb-walmart`
3. Instalar dependencias: `make install`
4. Ejecutar tests: `make test`
5. Correr pipeline: `make run-local`

## Modo Cloud (GCP):
1. Clonar repositorio y configurar variables en `.env`.
2. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
3. Instalar dependencias: `make install`
4. Ejecutar tests: `make test`
5. Correr pipeline: `make run-cloud`

## Modo Hybrid (Local y GCP):
1. Clonar repositorio y configurar variables en `.env`.
2. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
3. Instalar dependencias: `make install`
4. Cargar csv a Mongodb: `make ingest-mongodb`
5. Ejecutar tests: `make test`
6. Correr pipeline: `make run-hybrid`

## En Airflow (Nube):
1. Clonar repositorio y configurar variables en `.env`.
2. Crear carpeta `landing` en bucket y subir el archivo: `Walmart.csv`
3. Instalar dependencias: `make install`
4. Cargar csv a Mongodb: `make ingest-mongodb`
5. Ejecutar tests: `make test`
6. Instalar airflow: `make airflow-install`
7. Inicializar BD: `make airflow-init`
8. Crear usuario: airflow users create --username admin --firstname Nombre(s) --lastname Apellido(s) --role Admin --email email@ejemplo.com --password admin123
9. Iniciar Airflow: `make airflow-run`
10. Acceder a: `http://localhost:8081/`
11. Buscar y ejecutar DAG: `walmart_etl_dag`

# Cómo hacer backfill
Para realizar una ejecución backfill se puede llevar a cabo activando el parámetro `catchup` del DAG, esto hará que se recuperen todas las ejecuciones posteriores a "start_date"


# Qué revisar si falla

## Fallo en conexión a MongoDB
 - **Error:** `ServerSelectionTimeoutError` o `Connection refused`.
 - **Acción:** 
1. Verificar si el contenedor Docker está activo: `docker ps`.
2. Si está detenido, levantarlo: `docker start mongodb-walmart`.
3. Comprobar la URI en el archivo .env: `MONGO_URI=mongodb://localhost:27017/`.

## Fallo en la API de Festividades
 - **Error:** `HTTPError` (códigos 429, 500, o timeout).
 - **Acción:**
1. Validar que funcione la API colocando lo siguiente en el buscador: `https://date.nager.at/api/v3/publicholidays/2012/US`.
2. Verificar conectividad a internet en WSL: `curl -I https://date.nager.at`.

## Error de Permisos en GCP / BigQuery
 - **Error:** User does not have bigquery.jobs.create permission o error de escritura en bucket GCS.
 - **Acción:**
1. Verificar que el archivo credentials.json exista y la ruta esté correctamente definida en GOOGLE_APPLICATION_CREDENTIALS.
2. En IAM de GCP, confirmar que la Service Account tenga los roles:
- roles/bigquery.jobUser
- roles/bigquery.dataEditor
- roles/storage.objectAdmin
- roles/storage.bucketViewer
3. Confirmar que el dataset (bsg_walmart) exista en BigQuery.

# Qué Logs Mirar
1. **Salida estándar / WSL:**
 - Al ejecutar `make run-(modo)`, observar las salidas por consola que indican el avance de cada etapa (Extracción, Transformación, Carga).
2. **Logs de Apache Airflow:**
 - UI de Airflow > Seleccionar DAG Run > Clic en la tarea > Pestaña Log.