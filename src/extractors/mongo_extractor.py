import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoVentasExtractor:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("MONGO_DB", "walmart_db")
        self.collection_name = os.getenv("MONGO_COLLECTION", "ventas_raw")

    def extract_ventas(self) -> pd.DataFrame:
        client = MongoClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[self.collection_name]

        # Se obtiene el cursor con la data de la colección
        cursor = collection.find({}, {"_id": 0})
        df = pd.DataFrame(list(cursor))
        return df

if __name__ == "__main__":
    extractor = MongoVentasExtractor()
    df = extractor.extract_ventas()
    print(f"Ventas extraídas de MongoDB: {len(df)}")
    # Se imprime una pequeña muestra del df
    print(df.head())