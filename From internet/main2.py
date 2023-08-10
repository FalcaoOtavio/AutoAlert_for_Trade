from binance.client import Client
from binance.enums import *
import numpy as np
import config 
import json, talib, websocket
from datetime import datetime
import telegramMSG as tlg
import sys

import pandas as pd
from itertools import compress
from candle_rankings import candle_rankings

TRADE_SYMBOL = 'ETHUSDT'
TIME_INTERVAL = Client.KLINE_INTERVAL_15MINUTE

# armazena os valore de fechamento
closes = []

# https://medium.com/analytics-vidhya/recognizing-over-50-candlestick-patterns-with-python-4f02a1822cb5
def recognize_candlestick(df):
    """
    Recognizes candlestick patterns and appends 2 additional columns to df;
    1st - Best Performance candlestick pattern matched by www.thepatternsite.com
    2nd - # of matched patterns
    """

    op = df['open'].astype(float)
    hi = df['high'].astype(float)
    lo = df['low'].astype(float)
    cl = df['close'].astype(float)

    candle_names = talib.get_function_groups()['Pattern Recognition']

    # # patterns not found in the patternsite.com
    # exclude_items = ('CDLCOUNTERATTACK',
    #                  'CDLLONGLINE',
    #                  'CDLSHORTLINE',
    #                  'CDLSTALLEDPATTERN',
    #                  'CDLKICKINGBYLENGTH')

    exclude_items = ('CDLLONGLINE',
                     'CDLSHORTLINE',
                     'CDLSTALLEDPATTERN')
    candle_names = [candle for candle in candle_names if candle not in exclude_items]


    # create columns for each candle
    for candle in candle_names:
        # below is same as;
        # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)


    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    for index, row in df.iterrows():

        # no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                else:
                    container.append(pattern + '_Bear')
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    # cols_to_drop = candle_names + list(exclude_items)
    cols_to_drop = candle_names
    df.drop(cols_to_drop, axis = 1, inplace = True)

    return df

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, klines_df

    json_message = json.loads(message)
    
    candle = json_message['k']

    is_candle_closed = candle['x']

    if is_candle_closed:
        print(json_message,datetime.fromtimestamp(int(candle['T'])/1000))

    # armazena o valor de fechamento do candle
    close = candle['c']

    # verifica se o candle atual é fechamento
    if is_candle_closed:
    #if True:
        #criar um dataframe do ultimo clande fechado
        df2 = pd.DataFrame({"T": [datetime.fromtimestamp(int(candle['T'])/1000)],
                "open":[float(candle['o'])],
                "high":[float(candle['h'])],
                "low": [float(candle['l'])],
                "close":[float(candle['c'])],
                "V": [float(candle['v'])    ],
                "CT": [0],
                "QV":[float(candle['q'])],
                "N": [0],
                "TB":[ 0],
                "TQ": [0],
                "I":[0]}
                )
        # print("APPEND")
        klines_df = klines_df.append(df2, ignore_index = True)

        klines_df = removeExcedent(klines_df,30)

        # klines_df = setCandlestick(klines_df)
        klines_df2 = recognize_candlestick(klines_df)

        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
        
        closes.append(float(close))

        np_closes = np.array(closes)

        if len(closes) > 19 :
            upper, middle, lower = talib.BBANDS(np_closes, 21, 2, 2)
            last_BBupper = upper[-1]
            last_BBlower = lower[-1]
        
        if len(closes) > 26:
            macd, macdsignal, macdhist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
            last_macd = macd[-1]
            last_macdsignal = macdsignal[-1]
            last_macdhist = macdhist[-1]
        
        if len(closes) > 21:
            fastk, fastd  = talib.STOCHRSI(np_closes,timeperiod=21, fastk_period=21, fastd_period=3, fastd_matype=3)
            last_SRSIk = fastk[-1]
            last_SRSId = fastd[-1]
        
        if len(closes) > 7:
            rsi = talib.RSI(np_closes, 7)
            last_RSI = rsi[-1]

        #if True  Alterado#####:
        if (last_RSI > 70 and last_SRSIk > 20 and last_SRSId > 80):
            telegrambot.send_msg("SOBREVENDIDO:"+TRADE_SYMBOL)
            print("SOBREVENDIDO")
            print("Date time      :\t",data_e_hora_em_texto)
            print("TRADE SYMBOL   :\t",TRADE_SYMBOL)
            print("Closed value   :\t",format(float(close),'.6f'))
            print("RSI            :\t",format(float(last_RSI),'.4f'))
            print("RSI STOCK      :\t",format(last_SRSIk,'.2f'),format(last_SRSId,'.2f'))
            print("macdhist       :\t",format(last_macd,'.5f'),format(last_macdhist,'.5f'),format(last_macdhist,'.5f'))
            if float(close) >= last_BBupper:
                    print("*ROMPEU BOLLING PARA ACIMA*")
            
            print("CANDLE PATTERN :\t",klines_df2.candlestick_pattern.iloc[-1])
            print("CANDLE MATCH COUNT :\t",klines_df2.candlestick_match_count.iloc[-1])   
        elif (last_RSI < 30 and last_SRSIk < 20 and last_SRSId < 20):
            telegrambot.send_msg("SOBRECOMPRADO:"+TRADE_SYMBOL)
            print("SOBRECOMPRADO")
            print("Date time      :\t",data_e_hora_em_texto)
            print("TRADE SYMBOL   :\t",TRADE_SYMBOL)
            print("Closed value   :\t",format(float(close),'.6f'))
            print("RSI            :\t",format(float(last_RSI),'.4f'))
            print("RSI STOCK      :\t",format(last_SRSIk,'.2f'),format(last_SRSId,'.2f'))
            print("macdhist       :\t",format(last_macd,'.5f'),format(last_macdhist,'.5f'),format(last_macdhist,'.5f'))
            if float(close) <= last_BBlower:
                    print("*ROMPEU BOLLING PARA BAIXO*")
            if str(klines_df2.candlestick_pattern.iloc[-1]) != 'NO_PATTERN':
                print("CANDLE PATTERN :\t",klines_df2.candlestick_pattern.iloc[-1])
                print("CANDLE MATCH COUNT :\t",klines_df2.candlestick_match_count.iloc[-1])

def binanceDataFrame( klines):
    # df = pd.DataFrame(klines.reshape(-1,12),dtype=float, columns = ('Open Time',
    #                                                                 'Open',
    #                                                                 'High',
    #                                                                 'Low',
    #                                                                 'Close',
    #                                                                 'Volume',
    #                                                                 'Close time',
    #                                                                 'Quote asset volume',
    #                                                                 'Number of trades',
    #                                                                 'Taker buy base asset volume',
    #                                                                 'Taker buy quote asset volume',
    #                                                                 'Ignore'))
    # df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df = pd.DataFrame(klines.reshape(-1,12),dtype=float, columns=['T',
        'open',
        'high',
        'low',
        'close',
        'V',
        'CT',
        'QV',
        'N',
        'TB',
        'TQ',
        'I'])
    df['T'] = pd.to_datetime(df['T'], unit='ms')
    return df

def removeExcedent(df,qtmanter):
    if len(df) > qtmanter:
        qt2remove = len(df) - qtmanter
        df.drop(index=df.index[:qt2remove],
        axis=0,
        inplace=True)
    return df

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        
        # last_position_value = float(sys.argv[1])
        if sys.argv[1] is not None:
            
            TRADE_SYMBOL = sys.argv[1]

    client = Client(config.API_KEY,config.API_SECRET)
    print("Get historial klines")
    telegrambot = tlg.BotTelegram(config.TOKEN,config.BOTCHATID)
        
    klines = client.get_historical_klines(TRADE_SYMBOL,TIME_INTERVAL,"1 day ago UTC",limit=30)
    
    print("Get only close values")
    for candles  in range (len(klines) -1 ):
        closes.append(float(klines[candles][4]))
    
    klines_np = np.array(klines)
    print("Convert do Binance Data Frame")
    klines_df = binanceDataFrame(klines_np)

    # Remove o último
    klines_df = klines_df[:-1]
    print("Remove excedent")
    klines_df = removeExcedent(klines_df,30)
    print(klines_df)

    SOCKET = "wss://stream.binance.com:9443/ws/"+TRADE_SYMBOL.lower()+"@kline_"+TIME_INTERVAL
    
    ws = websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message)
    ws.run_forever()