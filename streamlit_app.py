import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="chave.env")

# Função para buscar dados da API
def fetch_data(year, headers):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-funcional-programatica/movimentacao-liquida"
    page = 1
    data = []

    while True:
        url = f"{url_base}?ano={year}&pagina={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Erro ao buscar dados: {response.status_code}")
            st.write(response.text)  # Diagnóstico do erro
            break
        
        page_data = response.json()
        if not page_data:  # Se não houver mais dados, interrompa
            break

        data.extend(page_data)
        page += 1  # Avance para a próxima página

    return data

# Configuração do Streamlit
st.title("Consulta ao Portal da Transparência")
st.write("Consulte as despesas por funcional programática do Portal da Transparência.")

# Entradas do usuário
year = st.number_input("Ano", min_value=2000, max_value=2025, value=2024, step=1)

# Recuperar a chave da API do arquivo .env
api_key = os.getenv("CHAVE_API_PORTAL")

if not api_key:
    st.error("Chave da API não encontrada! Configure o arquivo chave.env.")
else:
    headers = {
        "accept": "*/*",
        "chave-api-dados": api_key
    }

# Executar a consulta
if st.button("Buscar Dados"):
    with st.spinner("Buscando dados..."):
        data = fetch_data(year, headers)
    
    if data:
        st.success(f"Dados recuperados com sucesso! Total de registros: {len(data)}")
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        # Opção de baixar os dados como CSV
        csv = df.to_csv(index=False)
        st.download_button("Baixar Dados em CSV", csv, "dados.csv")
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")