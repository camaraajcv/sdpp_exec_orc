import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

caminho_arquivo='arquivos/lista-de-orgaos.xls'

# Função para ler os dados do Excel e criar o dicionário
def carregar_dados_excel(caminho_arquivo):
    # Carregar a planilha Excel
    df = pd.read_excel(caminho_arquivo)

    # Criar um dicionário com o nome do órgão como chave e o código como valor
    orgaos = dict(zip(df['nome_do_orgao'], df['orgao_codigo']))
    return orgaos
# Acessar a variável de ambiente
api_key = st.secrets["general"]["CHAVE_API_PORTAL"]

if api_key:
    st.success('Chave da API carregada com sucesso.')
else:
    st.error('Erro: Chave da API não encontrada na variável de ambiente.')

# Função para obter o código do órgão com base no nome
orgaos = carregar_dados_excel(caminho_arquivo)


def obter_codigo(orgao_nome):
    return orgaos.get(orgao_nome, "Órgão não encontrado")

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

# Função para limpar e converter colunas para numérico
def clean_and_convert(df):
    # Substituir vírgulas por pontos e converter para float
    for col in ['empenhado', 'liquidado', 'pago']:
        df[col] = df[col].str.replace('.', '').str.replace(',', '.').astype(float)
    return df

# Função principal do Streamlit
def main():
    # Título da aplicação
    st.title("Consulta de Despesas por Órgão")

    # Verificar se a chave foi carregada corretamente
    if not api_key:
        st.error("Erro: Chave da API não encontrada na variável de ambiente.")
        return

    # Criar um seletor para o ano
    year = st.selectbox("Escolha o ano", [2024, 2023, 2022, 2021])

    # Seleção do órgão
    orgao_selecionado = st.selectbox("Selecione o órgão", list(orgaos.keys()))
    orgao_code = obter_codigo(orgao_selecionado)

    # Seleção do órgão superior
    orgao_selecionado2 = st.selectbox("Selecione o órgão superior", list(orgaos.keys()))
    orgao_superior_code = obter_codigo(orgao_selecionado2)

    # Verificar se os códigos foram fornecidos
    if not orgao_code or not orgao_superior_code:
        st.error("Erro: Os códigos do órgão e do órgão superior não foram fornecidos.")
        return

    # Buscar dados usando a função fetch_data
    data = fetch_data(year, orgao_code, orgao_superior_code, api_key)

    # Exibir os dados se a resposta for válida
    if data:
        # Filtrar os dados para incluir apenas os registros com o código do órgão fornecido
        filtered_data = [item for item in data if item.get('codigoOrgao') == orgao_code]
        if filtered_data:
            # Organizar os dados por ano
            df = pd.DataFrame(filtered_data)
            df_grouped = df.groupby('ano')[['empenhado', 'liquidado', 'pago']].sum().reset_index()

            # Limpar e converter as colunas para numérico
            df_grouped = clean_and_convert(df_grouped)

            # Exibir o DataFrame para diagnóstico
            st.subheader("Dados Agrupados por Ano")
            st.dataframe(df_grouped)

            # Plotar o gráfico de barras empilhadas
            fig, ax = plt.subplots(figsize=(10, 6))
            df_grouped.set_index('ano').plot(kind='bar', stacked=True, ax=ax)
            ax.set_title(f"Comparativo de Despesas: {orgao_selecionado} ({year - 4} a {year})")
            ax.set_xlabel("Ano")
            ax.set_ylabel("Valor (R$)")
            ax.legend(title='Categorias de Despesa')
            st.pyplot(fig)

            # Calcular o total acumulado
            df_grouped['total'] = df_grouped[['empenhado', 'liquidado', 'pago']].sum(axis=1)

            # Plotar o gráfico de linha para o total acumulado
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df_grouped['ano'], df_grouped['total'], marker='o', color='black', linestyle='-', linewidth=2, label='Total Acumulado')
            ax.set_title(f"Total Acumulado de Despesas: {orgao_selecionado} ({year - 4} a {year})")
            ax.set_xlabel("Ano")
            ax.set_ylabel("Valor (R$)")
            ax.legend()
            st.pyplot(fig)
        else:
            st.warning(f"Nenhum dado encontrado para o código do órgão {orgao_code}.")
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")

# Rodar a aplicação Streamlit
if __name__ == "__main__":
    main()
