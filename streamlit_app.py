import requests
import pandas as pd
import os
from dotenv import load_dotenv
import streamlit as st

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path="chave.env")

# Função para buscar dados da API
def fetch_data(year, orgao_code, orgao_superior_code, page=1, api_key=None):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
    
    # Verificar se a chave da API está presente
    if not api_key:
        st.error("Erro: A chave da API não foi fornecida.")
        return None
    
    # Construir a URL com os parâmetros
    url = f"{url_base}?ano={year}&pagina={page}&codigoOrgao={orgao_code}&orgaoSuperior={orgao_superior_code}"
    
    # Cabeçalhos da requisição, incluindo a chave da API
    headers = {
        "accept": "*/*",
        "chave-api-dados": api_key  # Passando a chave da API no cabeçalho
    }

    # Realiza a requisição
    st.write(f"Fazendo requisição para a URL: {url}")  # Diagnóstico no Streamlit
    response = requests.get(url, headers=headers)
    
    # Exibe a URL da requisição e a resposta para diagnóstico
    st.write(f"Resposta da API: {response.status_code}")
    
    # Verificar o status da resposta
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.write(f"Erro na requisição: {response.text}")
        return None

# Configurações e parâmetros
year = 2024
orgao_code = "52111"  # Exemplo de código do órgão
orgao_superior_code = "52000"  # Código do órgão superior
page = 1

# Carregar a chave da API do arquivo .env
api_key = os.getenv("CHAVE_API_PORTAL")

# Verificar se a chave foi carregada corretamente
if not api_key:
    st.error("Erro: Chave da API não encontrada no arquivo .env.")
else:
    st.write(f"Chave da API carregada: {api_key}")  # Diagnóstico no Streamlit

    # Buscar dados usando a função fetch_data
    data = fetch_data(year, orgao_code, orgao_superior_code, page, api_key)

    # Exibir os dados se a resposta for válida
    if data:
        df = pd.DataFrame(data)
        st.write("Dados Recuperados:")
        st.dataframe(df)
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")
