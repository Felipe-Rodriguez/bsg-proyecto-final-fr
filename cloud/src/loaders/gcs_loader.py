import os
import io
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

class GCSLoader:
    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET")
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_parquet(self, df: pd.DataFrame, destination_blob_name: str) -> str:

        # Subida de un parquet a GCS
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)

        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_file(buffer, content_type="application/octet-stream")
        
        uri = f"gs://{self.bucket_name}/{destination_blob_name}"
        print(f" [GCS] Archivo subido exitosamente a: {uri}")
        return uri