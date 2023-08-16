import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import pandas as pd
import mplfinance 
from matplotlib.dates import DateFormatter

plt.style.use('ggplot')

# Carregar os dados do arquivo CSV de previsões
previsoes_df = pd.read_csv('previsoes.csv')

# Converter a coluna 'Date' para datetime
previsoes_df['Date'] = pd.to_datetime(previsoes_df['Date'])

# Criar uma coluna numérica para representar o horário do dia
previsoes_df['Time'] = previsoes_df['Date'].apply(lambda x: mpl_dates.date2num(x))

# Selecionar as colunas necessárias para o gráfico de velas
ohlc = previsoes_df.loc[:, ['Time', 'Open', 'High', 'Low', 'Close']]

# Criar subplots
fig, ax = plt.subplots()
plt.axis('off')
fig.patch.set_facecolor('black')

# Plotar o gráfico de velas
candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)

# Formatar as datas no eixo x
date_format = mpl_dates.DateFormatter('%Y-%m-%d %H:%M:%S')
ax.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

plt.show()
