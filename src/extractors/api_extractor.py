import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from typing import List
from dotenv import load_dotenv

load_dotenv()

class HolidayAPIExtractor:

    def __init__(
            self, 
            country_code: str = "US",
            timeout: int = 30,
            max_retries: int = 3
        ):
        self.country_code = country_code

        # Se utiliza la api de date.nager para obtener las fechas dee las festividades de USA de 2010 a 2012
        self.api_url = os.getenv("API_URL", "https://date.nager.at/api/v3/publicholidays")
        self.timeout = timeout
        self.session = self._build_session(max_retries)

    # Se tomó el ejemplo de reintentos incrementales del ejercicio en clase
    def _build_session(
            self, 
            max_retries: int
        ) -> requests.Session:
            """Configura la sesión HTTP con reintentos y backoff exponencial."""
            session = requests.Session()
            session.headers.update(
                {"Content-Type": "application/json", "Accept": "application/json"}
            )
            retry = Retry(
                total=max_retries,
                backoff_factor=0.5,              # 0s → 1s → 2s → falla
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            return session

    def extract_holidays(
              self, 
              years: List[int] = [2010, 2011, 2012]
        ) -> pd.DataFrame:
        all_holidays = []
        for year in years:
            url = f"{self.api_url}/{year}/{self.country_code}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            holidays = response.json()
            all_holidays.extend(holidays)

        df = pd.DataFrame(all_holidays)
        
        # Solo se tomarán los campos relevantes de la API
        cols_to_keep = ["date", "localName", "name", "fixed", "global", "types"]
        df = df[[c for c in cols_to_keep if c in df.columns]]
        return df

if __name__ == "__main__":
    extractor = HolidayAPIExtractor()
    df = extractor.extract_holidays()
    print(f"Festividades extraídas: {len(df)}")
    # Se imprime una pequeña muestra del df para pruebas
    print(df.head())