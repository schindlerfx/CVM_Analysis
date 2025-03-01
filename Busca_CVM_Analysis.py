import pandas as pd
import requests
import os
import zipfile

# Configuração do diretório de trabalho
diretorio_atual = os.getcwd()
dados_cvm_dir = os.path.join(diretorio_atual, "dados_cvm")

# Cria a pasta 'dados_cvm' se não existir
if not os.path.exists(dados_cvm_dir):
    os.makedirs(dados_cvm_dir)

os.chdir(dados_cvm_dir)

# Download dos arquivos da CVM
anos = range(2010, 2023)
url_base = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"

for ano in anos:
    try:
        print(f"Baixando arquivo do ano {ano}...")
        download = requests.get(url_base + f"dfp_cia_aberta_{ano}.zip")
        download.raise_for_status()  # Verifica se o download foi bem-sucedido
        with open(f"dfp_cia_aberta_{ano}.zip", "wb") as f:
            f.write(download.content)
        print(f"Arquivo do ano {ano} baixado com sucesso.")
    except Exception as e:
        print(f"Erro ao baixar o arquivo do ano {ano}: {e}")

# Extração e leitura dos arquivos ZIP
lista_demontracoes_2010_2022 = []

for arquivo in os.listdir(dados_cvm_dir):
    if arquivo.endswith(".zip"):
        try:
            print(f"Processando arquivo: {arquivo}")
            with zipfile.ZipFile(arquivo, 'r') as arquivo_zip:
                for planilha in arquivo_zip.namelist():
                    if planilha.endswith(".csv"):
                        print(f"Lendo planilha: {planilha}")
                        demonstracao = pd.read_csv(arquivo_zip.open(planilha), sep=";", encoding='ISO-8859-1', dtype={"ORDEM_EXERC": "category"})
                        lista_demontracoes_2010_2022.append(demonstracao)
        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

# Concatenando todos os DataFrames
if lista_demontracoes_2010_2022:
    base_dados = pd.concat(lista_demontracoes_2010_2022)
    print("Base de dados criada com sucesso.")
else:
    print("Nenhum dado foi carregado. Verifique os arquivos baixados.")
    exit()

# Processamento dos dados
base_dados[['con_ind', 'tipo_dem']] = base_dados['GRUPO_DFP'].str.split("-", expand=True)
base_dados['con_ind'] = base_dados['con_ind'].str.strip()
base_dados['tipo_dem'] = base_dados['tipo_dem'].str.strip()
base_dados = base_dados[base_dados['ORDEM_EXERC'] != "PENÚLTIMO"]

# Lista de demonstrações e empresas
lista_dem = base_dados['tipo_dem'].unique()
lista_empresas = base_dados['DENOM_CIA'].unique()

print("Tipos de demonstrações:", lista_dem)
print("Empresas encontradas:", lista_empresas)

# Filtragem de dados específicos (WEG S.A.)
weg_dre = base_dados[(base_dados["DENOM_CIA"] == "WEG S.A.") &
                     (base_dados["tipo_dem"] == "Demonstração do Resultado") &
                     (base_dados["DS_CONTA"] == "Receita de Venda de Bens e/ou Serviços") &
                     (base_dados["con_ind"] == "DF Consolidado")]
weg_dre = weg_dre[['DT_REFER', 'VL_CONTA']]

print("Dados da WEG S.A.:")
print(weg_dre)