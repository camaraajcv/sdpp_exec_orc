import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

orgaos = {
    "CAMARA DOS DEPUTADOS": 1000,
    "FUNDO ROTATIVO DA CAMARA DOS DEPUTADOS": 1901,
    "SENADO FEDERAL": 2000,
    "FUNDO ESPECIAL DO SENADO FEDERAL": 2001,
    "TRIBUNAL DE CONTAS DA UNIAO": 3000,
    "SUPREMO TRIBUNAL FEDERAL": 10000,
    "SUPERIOR TRIBUNAL DE JUSTICA": 11000,
    "JUSTICA FEDERAL": 12000,
    "JUSTICA MILITAR": 13000,
    "JUSTICA ELEITORAL": 14000,
    "JUSTICA DO TRABALHO": 15000,
    "JUSTICA DO DISTRITO FEDERAL E DOS TERRITORIOS": 16000,
    "CONSELHO NACIONAL DE JUSTICA": 17000,
    "PRESIDENCIA DA REPUBLICA": 20000,
    "PRESIDENCIA DA REPUBLICA": 20101,
    "MINISTERIO ADM.FED.REFORMA ESTADO-EM EXTINCAO": 20103,
    "MINISTERIO DO PLANEJAMENTO E ORCAMENTO": 20113,
    "FUNDO DE IMPRENSA NACIONAL": 20116,
    "SECRETARIA NACIONAL DE POLITICAS P/MULHERES": 20122,
    "CONTROLADORIA-GERAL DA UNIAO": 20125,
    "FUNDACAO ESCOLA NACIONAL DE ADM. PUBLICA": 20202,
    "AGENCIA NACIONAL DO CINEMA": 20203,
    "AGENCIA NACIONAL DE AVIACAO CIVIL": 20214,
    "COMISSAO NACIONAL DE ENERGIA NUCLEAR": 20301,
    "NUCLEBRAS EQUIPAMENTOS PESADOS S/A": 20302,
    "INDUSTRIAS NUCLEARES DO BRASIL S/A": 20303,
    "AGENCIA ESPACIAL BRASILEIRA - AEB": 20402,
    "FUNDACAO CASA DE RUI BARBOSA": 20403,
    "FUNDACAO BIBLIOTECA NACIONAL": 20404,
    "FUNDACAO CULTURAL PALMARES": 20408,
    "INSTITUTO DO PATRIMONIO HIST. E ART. NACIONAL": 20411,
    "FUNDACAO NACIONAL DE ARTES": 20412,
    "EMPRESA BRASIL DE COMUNICACAO S.A.-EBC": 20415,
    "CONSELHO NACIONAL DE DES.CIENT.E TECNOLOGICO": 20501,
    "FINANCIADORA DE ESTUDOS E PROJETOS": 20502,
    "SUPERINTENDENCIA DO DESENVOLV. DO NORDESTE": 20601,
    "SUPERINTENDENCIA DO DESENVOLV. DA AMAZONIA": 20602,
    "SUPERINTENDENCIA DA ZONA FRANCA DE MANAUS": 20603,
    "INSTITUTO BRASILEIRO DE TURISMO": 20604,
    "COMPANHIA DE DESENVOLVIMENTO DE BARCARENA": 20605,
    "INST.BRAS.DO MEIO AMB.E DOS REC.NAT.RENOVAV.": 20701,
    "FUNDO NACIONAL DE DESENVOLVIMENTO": 20924,
    "MINISTERIO DA AGRICULTURA E PECUARIA": 22000,
    "INSTIT. NAC. DE COLONIZACAO E REFORMA AGRARIA": 22201,
    "EMPRESA BRASILEIRA DE PESQUISA AGROPECUARIA": 22202,
    "CIA.DE DES.DOS VALES DO S.FRANC.E DO PARNAIBA": 22203,
    "DEPARTAMENTO NAC.DE OBRAS CONTRA AS SECAS": 22204,
    "COMPANHIA NACIONAL DE ABASTECIMENTO": 22211,
    "CIA.DE ENTREPOSTOS E ARMAZENS GER.DE S.PAULO": 22500,
    "FUNDO DE DEFESA DA ECONOMIA CAFEEIRA": 22905,
    "FUNDACAO DE DEFESA ECONOMICA CAFEEIRA": 23000,
    "MINISTERIO DA CIENCIA, TECNOLOGIA E INOVACAO": 24000,
    "INSTITUTO NAC.DE TECNOLOGIA DA INFORMACAO-ITI": 24208,
    "CENTRO NAC DE TECN ELETRONICA AVANCADA S/A": 24209,
    "TELECOMUNICACOES BRASILEIRAS S/A": 24216,
    "FUNDINCIAMENTO DE DESENVOLVIMENTO CIENTIFICIVO": 25901,
    "MINISTERIO DA FAZENDA": 25000,
    "COMISSAO DE VALORES MOBILIARIOS": 25203,
    "SUPERVISOR CONC.NACIONAL - AGRICULTURA": 25902,
    "SECRETARIA DA SAUDE E EDUCACAO": 25205,
    "FUND.PREVISTO INSTITUTO TENTALP-VIADAGRANCE": 25220
}

# Acessar a variável de ambiente
api_key = st.secrets["general"]["CHAVE_API_PORTAL"]

if api_key:
    st.success('Chave da API carregada com sucesso.')
else:
    st.error('Erro: Chave da API não encontrada na variável de ambiente.')

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
