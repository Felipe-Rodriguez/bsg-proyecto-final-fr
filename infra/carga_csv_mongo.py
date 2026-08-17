import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "walmart_db")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "ventas_raw")
CSV_PATH = os.getenv("INPUT_FILE_PATH_MONGODB", "./data_samples/Walmart.csv")

def carga_csv_db():
    print(f"Leyendo dataset desde {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Conexión a MongoDB
    print("Iniciando conexión a MongoDB")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Limpiar colección si ya existe
    collection.drop()
    
    # Convertir a diccionario e insertar
    records = df.to_dict(orient="records")
    collection.insert_many(records)
    
    print(f" Carga completada: {collection.count_documents({})} registros insertados en MongoDB ({DB_NAME}.{COLLECTION_NAME}).")

if __name__ == "__main__":
    carga_csv_db()