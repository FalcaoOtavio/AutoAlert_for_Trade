from binance.client import Client
from API_Key import API_Key, API_Secrect, API_Telegram
import websocket
import json
import talib
import numpy as np
import queue
import threading
import pandas as pd
from itertools import compress
from candle_rankings import candle_rankings
from datetime import datetime

client = Client(API_Key, API_Secrect)

# Symbol
trade_symbol1 = 'ETHUSDT'

# Interval
time_interval = Client.KLINE_INTERVAL_15MINUTE
closes = []

def on_open(ws):
    print("opened_connection")

def on_close(ws):
    print("closed_connection")

# Função chamada quando uma mensagem é recebida pela conexão WebSocket
def on_message(ws, message):
    global closes

    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        closes.append(float(close))
        np_closes = np.array(closes)

        if len(closes) > 21:
            upper, middle, lower = talib.BBANS(np_closes, 21, 2, 2)
            last_BBupper = upper[-1]
            last_BBlower = lower[-1]

        if len(closes) > 26:
            macd, macdsignal, macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
            last_macd = macd[-1]
            last_macdsignal = macdsignal[-1]
            last_macdhist = macdhist[-1]

        if len(closes) > 21:
            fastk, fastd = talib.STOCHRSI(np_closes, timeperiod=21, fastk_period=21, fastd_period=3, fastd_matype=3)
            last_SRSIk = fastk[-1]
            last_SRSId = fastd[-1]

        if last_SRSIk < 20:  # Sobrevendido (original: < 20)
            print("Atenção! O ativo está sobrevendido. Possível oportunidade de compra.")
            send_notification("Atenção! O ativo está sobrevendido. Possível oportunidade de compra.")
        elif last_SRSIk > 80:  # Sobrecomprado (original: > 80)
            print("Atenção! O ativo está sobrecomprado. Possível oportunidade de venda.")
            send_notification("Atenção! O ativo está sobrecomprado. Possível oportunidade de venda.")

        if len(closes) > 7:
            rsi = talib.RSI(np_closes, 7)
            last_RSI = rsi[-1]

            # Verificando se o RSI está sobrevendido ou sobrecomprado
            if last_RSI < 30:  # Sobrevendido
                send_alert("Atenção! O ativo está sobrevendido. Possível oportunidade de compra.")
            elif last_RSI > 70:  # Sobrecomprado
                send_alert("Atenção! O ativo está sobrecomprado. Possível oportunidade de venda.")

            def recognize_candlestick(df):
                last_candle = df[-1]
                if last_candle['open'] < last_candle['close']:
                    print("Candle de alta")
                elif last_candle['open'] > last_candle['close']:
                    print("Candle de baixa")
                else:
                    print("Candle neutro")


            # Reconhecer padrões de candlestick
            recognize_candlestick(np_closes)

# Função para enviar movimentações importantes para o Telegram
def send_alert(message):
    # Use alguma forma de comunicação IPC para enviar a mensagem para o Telegram_BOT.py
    pass

# Função para enviar movimentações importantes para a fila de mensagens
def send_notification(message):
    message_queue.put(message)

# Função para verificar e processar mensagens da fila
def process_message_queue():
    while True:
        message = message_queue.get()
        if message is None:
            break
        print(f"Received message: {message}")

# Inicie a thread para processar a fila
message_queue = queue.Queue()
message_thread = threading.Thread(target=process_message_queue)
message_thread.start()

# fetch 5-minute klines for the last day up until now
klines = client.get_historical_klines(trade_symbol1, Client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")

for candles in range(len(klines) - 1):
    closes.append(float(klines[candles][4]))

SOCKET = "wss://stream.binance.com:9443/ws/" + trade_symbol1.lower() + "@kline_" + time_interval
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

# Inicie a thread para o WebSocket
websocket_thread = threading.Thread(target=ws.run_forever)
websocket_thread.start()
