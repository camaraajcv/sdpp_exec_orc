import streamlit as st
import requests
import pandas as pd

# Função para buscar os dados da API
def fetch_data(year, headers):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-funcional-programatica/movimentacao-liquida"
    page = 1
    data = []

    while True:
        url = f"{url_base}?ano={year}&pagina={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Erro ao buscar dados: {response.status_code}")
            break
        
        page_data = response.json()
        if not page_data:
            break

        data.extend(page_data)
        page += 1

    return data

# Configuração do Streamlit
st.title("Consulta ao Portal da Transparência")
st.write("Consulte as despesas por funcional programática do Portal da Transparência.")

# Entradas do usuário
year = st.number_input("Ano", min_value=2000, max_value=2025, value=2024, step=1)
api_key = st.text_input("API Key", type="password")

# Executa a consulta
if st.button("Buscar Dados"):
    if not api_key:
        st.error("Insira uma chave de API válida!")
    else:
        headers = {
            "accept": "*/*",
            "chave-api-dados": api_key
        }
        with st.spinner("Buscando dados..."):
            data = fetch_data(year, headers)

        if data:
            st.success(f"Dados recuperados com sucesso! Total de registros: {len(data)}")
            # Converte os dados para DataFrame
            df = pd.DataFrame(data)
            st.dataframe(df)
            # Opção para download dos dados
            csv = df.to_csv(index=False)
            st.download_button("Baixar Dados em CSV", csv, "dados.csv")
        else:
            st.warning("Nenhum dado encontrado para os parâmetros informados.")