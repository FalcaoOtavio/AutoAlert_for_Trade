import pandas as pd
from sklearn.linear_model import LinearRegression
import time
import ccxt
import yfinance as yf
import telebot
import sys

#API_Key = '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/API_Key.py'

# Carregar as variáveis do TeleBot a partir do arquivo API_Key.py
#sys.path.insert(0, API_Key)
#from API_Key import API_Telegram

#CHAT_ID = '1365368606'

# Inicialize o bot do Telegram
#bot = telebot.TeleBot(API_Telegram)

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

csv_filename = '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/previsoes.csv'

# Inicializar a API da Binance
binance = ccxt.binance()

# Tolerância para comparação entre previsão e valor real
tolerancia = 1

# Ajustes com base nas oscilações
max_ajustes = 10
num_ajustes = 0

# Obter o horário da captura uma única vez fora do loop
horario_captura = time.strftime('%Y-%m-%d %H:%M:%S')

while True:
    try:

        # Atualizar o DataFrame com os dados mais recentes
        data = pd.read_csv('/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Dados.csv')

        # Obter o horário da captura uma única vez fora do loop
        horario_captura = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # preço de fechamento
        data = data[['close']]

        # Target
        data['target'] = data['close'].shift(-num_steps)

        data.dropna(inplace=True)

        # Recursos (X) e alvo (y)
        X = data.drop('target', axis=1)
        y = data['target']

        # Treinar
        model.fit(X, y)

        last_known_price = X.iloc[-1]['close']

        # Obter o valor do ticker da Binance
        ticker = binance.fetch_ticker('BTC/USDT')
        latest_price = ticker['last']

        # Prever
        future_predictions = model.predict([[last_known_price]])

        # Criar a mensagem
        prediction_message = f"Valor do BTC atual: {latest_price:.2f} | Horário da Captura: {horario_captura} | Previsão: {future_predictions[0]:.2f}"
        
        #Criar variavel
        last_future_prediction = future_predictions

        # Salvar mensagem no arquivo CSV
        with open(csv_filename, 'a') as csv_file:
            csv_file.write(prediction_message + '\n')

        # Enviar mensagem para o Telegram
        #if last_future_prediction is None or last_future_prediction != future_predictions:
        #    bot.send_message(CHAT_ID, prediction_message)
            
        # Imprimir mensagem no terminal
        print(prediction_message)
        
        # Aguardar antes da próxima iteração
        time.sleep(1800)

        #bot.polling(non_stop=True)

    except Exception as e:
        print("Erro no loop principal:", e)
        continue