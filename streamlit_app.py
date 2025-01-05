import os
import requests
import zipfile
import pandas as pd

BASE_URL = "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/"

def download_data(year, month):
    url = f"{BASE_URL}{year}{month:02d}"
    local_zip = f"data/{year}_{month:02d}.zip"
    os.makedirs("data", exist_ok=True)

    response = requests.get(url)
    with open(local_zip, "wb") as f:
        f.write(response.content)
    
    with zipfile.ZipFile(local_zip, 'r') as zip_ref:
        zip_ref.extractall("data/extracted")
    
    print(f"Dados de {year}-{month:02d} baixados e extraídos.")
    
def consolidate_data(start_year, end_year):
    files = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            file_path = f"data/extracted/{year}_{month:02d}.csv"
            if os.path.exists(file_path):
                files.append(file_path)
    
    df_list = [pd.read_csv(file, delimiter=";") for file in files]
    full_data = pd.concat(df_list, ignore_index=True)
    full_data.to_parquet("data/full_data.parquet", index=False)
    print("Dados consolidados em data/full_data.parquet")

# Exemplo: baixar e consolidar dados de 2022 a 2025
for year in range(2022, 2025 + 1):
    for month in range(1, 13):
        download_data(year, month)

consolidate_data(2022, 2025)
