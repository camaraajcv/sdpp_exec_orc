import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path="chave.env")

# Função para buscar dados da API
def fetch_data(year, orgao_code, page=1, api_key=None):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
    
    # Verificar se a chave da API está presente
    if not api_key:
        print("Erro: A chave da API não foi fornecida.")
        return None
    
    # Construir a URL com os parâmetros
    url = f"{url_base}?ano={year}&pagina={page}&codigoOrgao={orgao_code}"
    
    # Cabeçalhos da requisição, incluindo a chave da API
    headers = {
        "accept": "*/*",
        "chave-api-dados": api_key  # Passando a chave da API no cabeçalho
    }

    # Realiza a requisição
    response = requests.get(url, headers=headers)
    
    # Exibe a URL da requisição e a resposta para diagnóstico
    print(f"URL da requisição: {url}")
    print(f"Resposta da API: {response.status_code}")
    
    # Verificar o status da resposta
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Erro na requisição: {response.text}")
        return None

# Configurações e parâmetros
year = 2024
orgao_code = "52111"  # Exemplo de código do órgão
page = 1

# Carregar a chave da API do arquivo .env
api_key = os.getenv("CHAVE_API_PORTAL")

# Verificar se a chave foi carregada corretamente
if not api_key:
    print("Erro: Chave da API não encontrada no arquivo .env.")
else:
    # Buscar dados usando a função fetch_data
    data = fetch_data(year, orgao_code, page, api_key)

    # Exibir os dados se a resposta for válida
    if data:
        df = pd.DataFrame(data)
        print("Dados Recuperados:")
        print(df)
    else:
        print("Nenhum dado encontrado ou erro na requisição.")