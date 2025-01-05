import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Caminho do arquivo Excel
caminho_arquivo = 'arquivos/lista-de-orgaos.xlsx'

# Função para ler os dados do Excel e criar o dicionário
def carregar_dados_excel(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo, engine='openpyxl')
    orgaos = dict(zip(df['Órgão UGE Nome'], df['Órgão UGE Código']))
    orgaos = dict(sorted(orgaos.items()))  # Ordenar por nome
    return orgaos

# Carregar a chave da API
api_key = st.secrets.get("CHAVE_API_PORTAL")

if api_key:
    st.success('Chave da API carregada com sucesso.')
else:
    st.error('Erro: Chave da API não encontrada.')

# Carregar os dados dos órgãos
orgaos = carregar_dados_excel(caminho_arquivo)

# Função para obter o código do órgão com base no nome
def obter_codigo(orgao_nome):
    return orgaos.get(orgao_nome, None)

# Função para buscar dados da API
def fetch_data(year, orgao_code, orgao_superior_code, api_key):
    url_base = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
    all_data = []
    
    if not api_key:
        st.error("Erro: A chave da API não foi fornecida.")
        return None

    st.write(f"Código do órgão: {orgao_code}")
    st.write(f"Código do órgão superior: {orgao_superior_code}")

    for y in range(year - 4, year + 1):
        page = 1
        while True:
            url = f"{url_base}?ano={y}&pagina={page}&codigoOrgao={orgao_code}&orgaoSuperior={orgao_superior_code}"
            headers = {
                "accept": "*/*",
                "chave-api-dados": api_key
            }
            response = requests.get(url, headers=headers)
            st.write(f"Requisição para {url}")
            st.write(f"Resposta da API: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if data:
                    all_data.extend(data)
                    page += 1
                else:
                    break
            else:
                st.write(f"Erro na requisição: {response.text}")
                break

    return all_data

# Função para limpar e converter colunas para numérico
def clean_and_convert(df):
    # Substituir vírgulas por pontos e converter para float
    for col in ['empenhado', 'liquidado', 'pago']:
        df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
    return df

# Função principal do Streamlit
def main():
    st.title("Consulta de Despesas por Órgão")

    if not api_key:
        st.error("Erro: Chave da API não encontrada.")
        return

    year = st.selectbox("Escolha o ano", [2024, 2023, 2022, 2021])

    orgao_selecionado = st.selectbox("Selecione o órgão", list(orgaos.keys()))
    orgao_code = obter_codigo(orgao_selecionado)

    orgao_selecionado2 = st.selectbox("Selecione o órgão superior", list(orgaos.keys()))
    orgao_superior_code = obter_codigo(orgao_selecionado2)

    if not orgao_code or not orgao_superior_code:
        st.error("Erro: Os códigos do órgão e do órgão superior não foram fornecidos.")
        return

    data = fetch_data(year, orgao_code, orgao_superior_code, api_key)

    if data:
        filtered_data = [item for item in data if item.get('codigoOrgao') == orgao_code]
        if filtered_data:
            df = pd.DataFrame(filtered_data)
            df_grouped = df.groupby('ano')[['empenhado', 'liquidado', 'pago']].sum().reset_index()
            df_grouped = clean_and_convert(df_grouped)

            st.subheader("Dados Agrupados por Ano")
            st.dataframe(df_grouped)

            fig, ax = plt.subplots(figsize=(10, 6))
            df_grouped.set_index('ano').plot(kind='bar', stacked=True, ax=ax)
            ax.set_title(f"Comparativo de Despesas: {orgao_selecionado} ({year - 4} a {year})")
            ax.set_xlabel("Ano")
            ax.set_ylabel("Valor (R$)")
            ax.legend(title='Categorias de Despesa')
            st.pyplot(fig)

            df_grouped['total'] = df_grouped[['empenhado', 'liquidado', 'pago']].sum(axis=1)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_grouped['ano'], df_grouped['total'], marker='o', color='black', linestyle='-', linewidth=2, label='Total Acumulado')
            ax.set_title(f"Total Acumulado de Despesas: {orgao_selecionado} ({year - 4} a {year})")
            ax.set_xlabel("Ano")
            ax.set_ylabel("Valor (R$)")
            ax.legend()
            st.pyplot(fig)
        else:
            st.warning(f"Nenhum dado encontrado para o código do órgão {orgao_code} e órgão superior {orgao_superior_code}.")
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")

# Rodar a aplicação Streamlit
if __name__ == "__main__":
    main()
