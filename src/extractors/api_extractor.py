import requests
import pandas as pd
from typing import List

class HolidayAPIExtractor:

    # Se utiliza la api de date.nager para obtener las fechas dee las festividades de USA de 2010 a 2012
    BASE_URL = "https://date.nager.at/api/v3/publicholidays"

    def __init__(self, country_code: str = "US"):
        self.country_code = country_code

    def extract_holidays(self, years: List[int] = [2010, 2011, 2012]) -> pd.DataFrame:
        all_holidays = []
        for year in years:
            url = f"{self.BASE_URL}/{year}/{self.country_code}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            holidays = response.json()
            all_holidays.extend(holidays)

        df = pd.DataFrame(all_holidays)
        
        # Seleccionar campos relevantes de la API
        cols_to_keep = ["date", "localName", "name", "fixed", "global", "types"]
        df = df[[c for c in cols_to_keep if c in df.columns]]
        return df

if __name__ == "__main__":
    extractor = HolidayAPIExtractor()
    df = extractor.extract_holidays()
    print(f"Festividades extraídas: {len(df)}")
    # Se imprime una pequeña muestra del df
    print(df.head())