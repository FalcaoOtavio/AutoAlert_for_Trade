import pandas as pd
from sklearn.linear_model import LinearRegression
import time
import ccxt
import yfinance as yf

# Carregar os dados do arquivo CSV
data = pd.read_csv('Dados.csv')

# preço de fechamento
data = data[['close']]

# target
num_steps = 5
data['target'] = data['close'].shift(-num_steps)

# Remover valores ausentes
data.dropna(inplace=True)

# Recursos (X) e alvo (y)
X = data.drop('target', axis=1)
y = data['target']

# Regressão Linear
model = LinearRegression()
model.fit(X, y)

csv_filename = "previsoes.csv"

# Inicializar a API
exchange = ccxt.binance()

# Tolerância para comparação entre previsão e valor real
tolerancia = 1

# Ajustes com base nas oscilações
max_ajustes = 10

num_ajustes = 0

# Lista de fontes de dados para comparação
fontes_de_dados = ['coinmarketcap', 'coinbase', 'kraken']

while True:
    try:
        # Atualizar o DataFrame com os dados mais recentes
        data = pd.read_csv('Dados.csv')
        data = data[['close']]

        # Target
        data['target'] = data['close'].shift(-num_steps)

        data.dropna(inplace=True)

        X = data.drop('target', axis=1)
        y = data['target']

        # Treinar
        model.fit(X, y)

        last_known_price = X.iloc[-1]['close']

        # Especulação do Ticker
        max_attempts = 5
        attempts = 0
        latest_price = None
        while attempts < max_attempts:
            try:
                ticker = exchange.fetch_ticker('BTC/USDT')
                latest_price = ticker['last']
                break
            except Exception as e:
                print("Erro de conexão:", e)
                attempts += 1
                time.sleep(5)  # Aguardar um pouco antes de tentar novamente

        if latest_price is None:
            print("Não foi possível obter o valor do ticker após várias tentativas. Continuando...")
            continue

        # Prever
        future_predictions = model.predict([[last_known_price]])

        # Comparar a previsão com o valor real, com tolerância
        error = latest_price - future_predictions[0]
        if abs(error) <= tolerancia and num_ajustes < max_ajustes:
            y[-num_steps:] = y[-num_steps:] - error
            model.fit(X, y)
            num_ajustes += 1

        print("Previsões das próximas cotações do BTC:")
        print(future_predictions)
        print("Valor real mais recente do BTC:", latest_price)
        print("Erro:", error)

        # Coletar valores de diferentes fontes para comparação
        comparacoes = {}
        for fonte in fontes_de_dados:
            try:
                if fonte == 'coinbase':
                    # Obter o valor de BTC da Coinbase usando ccxt
                    ticker = exchange.fetch_ticker('BTC/USD', {'source': fonte})
                    valor_fonte = ticker['last']
                elif fonte == 'coinmarketcap':
                    # Obter o valor de BTC do CoinMarketCap usando yfinance
                    ticker = yf.Ticker('BTC-USD')
                    valor_fonte = ticker.history(period="1d")["Close"].iloc[-1]
                elif fonte == 'kraken':
                    # Obter o valor de BTC da Kraken usando ccxt
                    ticker = exchange.fetch_ticker('BTC/USD', {'source': fonte})
                    valor_fonte = ticker['last']
                else:
                    valor_fonte = None
                
                if valor_fonte is not None:
                    comparacoes[fonte] = abs(latest_price - valor_fonte)
            except Exception as e:
                print(f"Erro ao obter valor da fonte {fonte}:", e)
         
        # Ordenar as fontes por menor diferença em relação ao valor real
        fonte_mais_acurada = min(comparacoes, key=comparacoes.get)
        print("Fonte mais acurada:", fonte_mais_acurada)
        
        # Ajustar previsões com base nos erros passados
        if num_ajustes > 0:
            y[-num_steps:] = y[-num_steps:] - error
        
        # DataFrame previsões
        future_df = pd.DataFrame({'predicted_price': future_predictions, 'fonte_mais_acurada': [fonte_mais_acurada]})

        # Salvar previsões CSV
        future_df.to_csv(csv_filename, mode='a', header=False, index=False)

        # Atualização
        time.sleep(900)

    except Exception as e:
        print("Erro no loop principal:", e)
        continue
