import requests
import pandas as pd
import os
from dotenv import load_dotenv
import streamlit as st

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path="chave.env")

# Função para buscar dados da API
def fetch_data(year, orgao_code, orgao_superior_code, api_key=None):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
    page = 1
    all_data = []

    # Verificar se a chave da API está presente
    if not api_key:
        st.error("Erro: A chave da API não foi fornecida.")
        return None

    while True:
        # Construir a URL com os parâmetros
        url = f"{url_base}?ano={year}&pagina={page}&codigoOrgao={orgao_code}&orgaoSuperior={orgao_superior_code}"

        # Cabeçalhos da requisição, incluindo a chave da API
        headers = {
            "accept": "*/*",
            "chave-api-dados": api_key  # Passando a chave da API no cabeçalho
        }

        # Realiza a requisição
        response = requests.get(url, headers=headers)

        # Verificar o status da resposta
        if response.status_code == 200:
            data = response.json()
            if data:
                all_data.extend(data)
                page += 1
            else:
                break  # Não há mais dados, sai do loop
        else:
            st.write(f"Erro na requisição: {response.text}")
            break  # Em caso de erro, sai do loop

    return all_data

# Função principal do Streamlit
def main():
    # Título da aplicação
    st.title("Consulta de Despesas por Órgão")

    # Carregar a chave da API do arquivo .env
    api_key = os.getenv("CHAVE_API_PORTAL")

    # Verificar se a chave foi carregada corretamente
    if not api_key:
        st.error("Erro: Chave da API não encontrada no arquivo .env.")
        return

    # Parâmetros fixos
    orgao_code = "52111"  # Código do órgão
    orgao_superior_code = "52000"  # Código do órgão superior

    # Criar um seletor para o ano
    year = st.selectbox("Escolha o ano", [2024, 2023, 2022, 2021])

    # Buscar dados usando a função fetch_data
    data = fetch_data(year, orgao_code, orgao_superior_code, api_key)

    # Exibir os dados se a resposta for válida
    if data:
        df = pd.DataFrame(data)
        st.write("Dados Recuperados:")
        st.dataframe(df)
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")

# Rodar a aplicação Streamlit
if __name__ == "__main__":
    main()