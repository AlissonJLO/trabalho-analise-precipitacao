import pandas as pd

# Define o caminho do arquivo CSV
caminho_arquivo = "./cuiaba/cuiaba-2008.CSV"

# Lê o CSV. Se o arquivo usar separador ';' (muito comum em arquivos gerados no Brasil),
# altere o parâmetro sep para ';'
df = pd.read_csv(caminho_arquivo, sep=',')

# Exibe as primeiras linhas do DataFrame
print(df.head())
