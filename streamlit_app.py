import requests
import pandas as pd
import os
import streamlit as st
import matplotlib.pyplot as plt

# Acessar a variável de ambiente
api_key = os.getenv('CHAVE_API_PORTAL')

if api_key:
    print('Chave da API carregada com sucesso.')
else:
    print('Erro: Chave da API não encontrada na variável de ambiente.')

# Função para buscar dados da API
def fetch_data(year, orgao_code, orgao_superior_code, api_key=None):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
    all_data = []

    # Verificar se a chave da API está presente
    if not api_key:
        st.error("Erro: A chave da API não foi fornecida.")
        return None

    for y in range(year - 4, year + 1):
        page = 1
        while True:
            # Construir a URL com os parâmetros
            url = f"{url_base}?ano={y}&pagina={page}&codigoOrgao={orgao_code}&orgaoSuperior={orgao_superior_code}"

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

    # Verificar se a chave foi carregada corretamente
    if not api_key:
        st.error("Erro: Chave da API não encontrada na variável de ambiente.")
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
        # Filtrar os dados para incluir apenas os registros com o código do órgão 52111
        filtered_data = [item for item in data if item.get('codigoOrgao') == orgao_code]
        if filtered_data:
            # Organizar os dados por ano
            df = pd.DataFrame(filtered_data)
            df_grouped = df.groupby('ano')[['empenhado', 'liquidado', 'pago']].sum().reset_index()

            # Plotar o gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            df_grouped.set_index('ano').plot(kind='bar', stacked=True, ax=ax)
            ax.set_title(f"Comparativo de Despesas: {orgao_code} ({year - 4} a {year})")
            ax.set_xlabel("Ano")
            ax.set_ylabel("Valor (R$)")
            st.pyplot(fig)
        else:
            st.warning(f"Nenhum dado encontrado para o código do órgão {orgao_code}.")
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")

# Rodar a aplicação Streamlit
if __name__ == "__main__":
    main()
