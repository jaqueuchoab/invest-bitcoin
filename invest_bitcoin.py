# Importação das bibliotecas:
# numpy, serve para cáculos númericos
# pandas, serve para a manipulação de dados
# matplotlib, serve para visualização em grafos
# requests, serve para requisões HTTP à API
# datetime, a classe 'datetime' da biblioteca 'datetime' para manipulação de datas
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# Função para obter o preço do Bitcoin em uma data específica
def obter_preco_bitcoin(data_str):
    """
    Obtém o preço do Bitcoin em uma data específica.

    :param data_str: Data no formato 'dd-mm-aaaa'.
    :return: Preço do Bitcoin na data especificada ou None em caso de erro.
    """
    # URL da API CoinGecko
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/history?date={data_str}&localization=false&vs_currency=usd"

    try:
        # Fazer a requisição à API
        response = requests.get(url)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            dados = response.json()
            # Extrair o preço do Bitcoin
            preco = dados['market_data']['current_price']['usd']
            return preco
        else:
            # Se a requisição falhar, exibir uma mensagem de erro
            print(f"Erro na requisição: {response.status_code}")
            print(f"Mensagem de erro: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # Capturar erros de rede ou requisição
        print(f"Erro na requisição: {e}")
        return None

# Função para converter uma data (ano, mês, dia) em um timestamp (em segundos)
def data_para_timestamp(ano, mes, dia):
    # Cria um objeto 'datetime' com a data fornecida
    data = datetime(ano, mes, dia)
    # Converte a data para timestamp (em segundos) e retorna o valor
    return int(data.timestamp())

# Passo 1: Carregar dados históricos do Bitcoin

# Definir as datas de interesse
# Timestamp inicial: 1 de novembro de 2024, 00:00:00 UTC
data_inicial = data_para_timestamp(2024, 11, 1)
# Timestamp final: 5 de novembro de 2024, 23:59:59 UTC
data_final = data_para_timestamp(2024, 11, 10)
data_str = "12-11-2024"  # Data no formato dd-mm-aaaa

# URL da API CoinGecko para obter os dados históricos do Bitcoin
# Parâmetros:
# - 'vs_currency=usd': Preços em dólares americanos (USD)
# - 'from': Timestamp inicial
# - 'to': Timestamp final
url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={data_inicial}&to={data_final}"

# Fazer a requisição à API usando o método GET
response = requests.get(url)

# Verificar se a requisição foi bem-sucedida (código de status 200)
if response.status_code == 200:
    # Converter a resposta da API (em formato JSON) para um dicionário Python
    dados_response = response.json()
else:
    # Se a requisição falhar, exibir uma mensagem de erro e encerrar o programa
    print(f"Erro na requisição: {response.status_code}")
    print(f"Mensagem de erro: {response.text}")
    exit()

# Extrair os preços do Bitcoin do dicionário de dados
# O campo 'prices' contém uma lista de listas, onde cada sublista tem:
# - Posição 0: Timestamp em milissegundos
# - Posição 1: Preço do Bitcoin naquele momento
precos = dados_response['prices']

# Processar os dados para facilitar a visualização
# Converter os timestamps (em milissegundos) para objetos 'datetime'
datas = [datetime.fromtimestamp(preco[0] / 1000) for preco in precos]
# Extrair os preços do Bitcoin
valores = [preco[1] for preco in precos]

# Criar um DataFrame com os dados históricos
dados = {
    'data': datas,
    'preco_fechamento': valores
}
df = pd.DataFrame(dados)

# Calcular a variação percentual diária do preço de fechamento
# A função pct_change() calcula a variação percentual em relação ao valor anterior
# A variação percentual é uma medida que indica o quanto um valor mudou em relação a um valor anterior, expressa em porcentagem.
df['variacao_percentual'] = df['preco_fechamento'].pct_change() * 100

# Remover a primeira linha (onde a variação percentual é NaN)
df = df.dropna()

# Passo 2: Calcular média e desvio padrão das variações
# A média das variações percentuais diárias
media = df['variacao_percentual'].mean()
# O desvio padrão das variações percentuais diárias
desvio_padrao = df['variacao_percentual'].std()

# Exibir a média e o desvio padrão
print(f"Média da variação diária: {media:.2f}%")
print(f"Desvio padrão da variação diária: {desvio_padrao:.2f}%")

# Passo 3: Simulação de Monte Carlo para 3 dias
np.random.seed(42)  # Define uma semente para garantir que os resultados sejam reproduzíveis
num_simulacoes = 10000  # Número de simulações a serem realizadas
preco_atual = obter_preco_bitcoin(data_str)  # Preço atual do Bitcoin (último preço no DataFrame)

# Verificar se o preço atual foi obtido com sucesso
if preco_atual is None:
    print("Não foi possível obter o preço atual. Usando o último preço do DataFrame.")
    preco_atual = df['preco_fechamento'].iloc[-1]

dias = 3  # Número de dias para a simulação
resultados = np.zeros(num_simulacoes)  # Array para armazenar os resultados das simulações

# Loop para realizar as simulações
for i in range(num_simulacoes):
    # Gera variações percentuais aleatórias para os 3 dias, seguindo uma distribuição normal
    variacoes = np.random.normal(media, desvio_padrao, dias)
    # Calcula o preço final após 3 dias, considerando as variações simuladas
    preco_final = preco_atual * (1 + np.sum(variacoes) / 100)
    # Armazena o preço final no array de resultados
    resultados[i] = preco_final

# Passo 4: Análise dos resultados
# Calcula a probabilidade de lucro (preço final maior que o preço atual)
probabilidade_lucro = np.mean(resultados > preco_atual) * 100
# Calcula a probabilidade de prejuízo (preço final menor que o preço atual)
probabilidade_prejuizo = np.mean(resultados < preco_atual) * 100

# Exibe as probabilidades
print(f"Probabilidade de lucro após 3 dias: {probabilidade_lucro:.2f}%")
print(f"Probabilidade de prejuízo após 3 dias: {probabilidade_prejuizo:.2f}%")

# Visualização dos resultados
# Cria um histograma dos preços finais simulados
plt.hist(resultados, bins=50, edgecolor='black')
# Adiciona uma linha vertical para indicar o preço atual
plt.axvline(preco_atual, color='red', linestyle='dashed', linewidth=2, label='Preço Atual')
# Adiciona título e rótulos aos eixos
plt.title('Distribuição de Preços do Bitcoin após 3 Dias')
plt.xlabel('Preço do Bitcoin')
plt.ylabel('Frequência')
# Adiciona uma legenda
plt.legend()
# Exibe o gráfico
plt.show()