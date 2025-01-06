import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import FuncFormatter

# Caminho do arquivo Excel
caminho_arquivo = 'arquivos/lista-de-orgaos.xlsx'
# Obter o ano atual
ano_atual = datetime.now().year
# Função para ler os dados do Excel e criar o dicionário
def carregar_dados_excel(caminho_arquivo):
    # Carregar a planilha Excel
    df = pd.read_excel(caminho_arquivo, engine='openpyxl')

    # Criar um dicionário com o nome do órgão como chave e o código como valor
    orgaos = dict(zip(df['Órgão UGE Nome'], df['Órgão UGE Código']))
    # Ordenar os órgãos por nome (chave do dicionário)
    orgaos = dict(sorted(orgaos.items()))
  
    return orgaos

# Acessar a variável de ambiente para a chave da API
api_key = st.secrets["general"].get("CHAVE_API_PORTAL")

if api_key:
    st.success('Chave da API carregada com sucesso.')
else:
    st.error('Erro: Chave da API não encontrada na variável de ambiente.')

# Carregar os dados dos órgãos
orgaos = carregar_dados_excel(caminho_arquivo)

# Função para obter o código do órgão com base no nome
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

    for y in range(year - 8, year + 1):
        page = 1  # Apenas a página 1 será requisitada
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
            else:
                break  # Não há mais dados, sai do loop para esse ano
        else:
            st.write(f"Erro na requisição: {response.text}")
            break  # Em caso de erro, sai do loop

    return all_data

# Função para limpar e converter colunas para numérico
def clean_and_convert(df):
    # Substituir vírgulas por pontos e remover pontos de milhares
    for col in ['empenhado', 'liquidado', 'pago']:
        df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df
 # Função de formatação
def formatar_eixo_y(x, pos):
    if x >= 1e12:
        return f'{x/1e12:.1f} Tri'
    elif x >= 1e9:
        return f'{x/1e9:.1f} Bi'
    elif x >= 1e6:
        return f'{x/1e6:.1f} Mi'
    else:
        return f'{x:.1f}'
# Função principal do Streamlit
def main():
    # Título da aplicação
    st.title("Consulta de Despesas por Órgão")

    # Verificar se a chave foi carregada corretamente
    if not api_key:
        st.error("Erro: Chave da API não encontrada na variável de ambiente.")
        return

    # Criar um seletor para o ano
    year = st.selectbox("Escolha o ano", [ano_atual, ano_atual-1, ano_atual-2, ano_atual-3, ano_atual-4])

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
        filtered_data = [item for item in data if str(item.get('codigoOrgao')) == str(orgao_code)]

        if filtered_data:
            # Organizar os dados por ano
            df = pd.DataFrame(filtered_data)
            df_grouped = df.groupby('ano')[['empenhado', 'liquidado', 'pago']].sum().reset_index()

            # Limpar e converter as colunas para numérico
            df_grouped = clean_and_convert(df_grouped)

            # Exibir o DataFrame para diagnóstico
            st.subheader("Dados Agrupados por Ano")
            st.dataframe(df_grouped)

           # Criar subplots (1 coluna, 2 linhas)
            fig, (ax1, ax2) = plt.subplots(figsize=(10, 12), nrows=2)

            # Gráfico de barras (na parte superior)
            df_grouped.set_index('ano').plot(kind='bar', stacked=False, ax=ax1)
            ax1.set_title(f"Comparativo de Despesas: {orgao_selecionado} ({year - 8} a {year})")
            ax1.set_xlabel("Ano")
            ax1.set_ylabel("Valor (R$)")
            ax1.legend(title='Categorias de Despesa')

            # Aplicar formatação ao eixo Y para o gráfico de barras
            ax1.yaxis.set_major_formatter(FuncFormatter(formatar_eixo_y))

            # Calcular o total acumulado
            df_grouped['total'] = df_grouped[['empenhado', 'liquidado', 'pago']].sum(axis=1)

            # Gráfico de linha (na parte inferior)
            ax2.plot(df_grouped['ano'], df_grouped['total'], marker='o', color='black', linestyle='-', linewidth=2, label='Total Acumulado')
            ax2.set_title(f"Total Acumulado de Despesas: {orgao_selecionado} ({year - 8} a {year})")
            ax2.set_xlabel("Ano")
            ax2.set_ylabel("Valor (R$)")
            ax2.legend()

            # Aplicar formatação ao eixo Y para o gráfico de linha
            ax2.yaxis.set_major_formatter(FuncFormatter(formatar_eixo_y))

            # Ajustar layout para evitar sobreposição
            plt.tight_layout()

            # Exibir os gráficos
            st.pyplot(fig)
        else:
            st.warning(f"Nenhum dado encontrado para o código do órgão {orgao_code} e orgao superior {orgao_superior_code}.")
    else:
        st.warning("Nenhum dado encontrado ou erro na requisição.")

# Rodar a aplicação Streamlit
if __name__ == "__main__":
    main()

