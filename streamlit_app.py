import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="chave.env")

# Função para buscar dados da API
def fetch_data(year, headers, filters):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
    page = 1
    data = []

    while True:
        # Construir a URL com os filtros adicionais
        params = f"ano={year}&pagina={page}"
        for key, value in filters.items():
            if value:
                params += f"&{key}={value}"

        url = f"{url_base}?{params}"
        response = requests.get(url, headers=headers)

        # Exibir a URL e resposta para diagnóstico
        st.write(f"URL da requisição: {url}")
        st.write(f"Resposta da API: {response.text}")  # Exibe a resposta completa para depuração

        if response.status_code != 200:
            st.error(f"Erro ao buscar dados: {response.status_code}")
            break

        page_data = response.json()

        # Verificar se a resposta contém dados válidos
        if page_data and 'codigoOrgao' in page_data[0]:
            data.extend(page_data)
        else:
            st.warning("Nenhum dado válido encontrado ou dados com valores padrão.")

        if not page_data:  # Se não houver mais dados, interrompa
            break

        page += 1  # Avance para a próxima página

    return data

# Configuração do Streamlit
st.title("Consulta ao Portal da Transparência")
st.write("Consulte as despesas por órgão do Portal da Transparência.")

# Entradas do usuário
year = st.number_input("Ano", min_value=2000, max_value=2025, value=2024, step=1)

# Seleção de filtros adicionais
codigo_orgao = st.text_input("Código do Órgão (opcional)", "52111")

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
        # Preparar filtros
        # Adicionando o filtro 'empenhado' com valor vazio para passar o filtro mínimo exigido pela API
        filters = {"codigoOrgao": codigo_orgao, "empenhado": ""}

        data = fetch_data(year, headers, filters)

    if data:
        st.success(f"Dados recuperados com sucesso! Total de registros: {len(data)}")
        df = pd.DataFrame(data)
        st.dataframe(df)

        # Opção de baixar os dados como CSV
        csv = df.to_csv(index=False)
        st.download_button("Baixar Dados em CSV", csv, "dados.csv")
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")