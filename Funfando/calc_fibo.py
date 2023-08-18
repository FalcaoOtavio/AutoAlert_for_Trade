import pandas as pd
import time

print("Calculando...")

# Carregar os dados do arquivo CSV
data = pd.read_csv('/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Dados.csv')

while True:
    try:
        # Obter os preços de fechamento dos últimos 10 dias
        close_prices = data['close'][-10:]

        # Calcular o preço máximo e mínimo
        max_price = close_prices.max()
        min_price = close_prices.min()

        # Calcular os níveis de retração de Fibonacci
        fib_236 = max_price - 0.236 * (max_price - min_price)
        fib_382 = max_price - 0.382 * (max_price - min_price)
        fib_05 = max_price - 0.5 * (max_price - min_price)
        fib_618 = max_price - 0.618 * (max_price - min_price)

        # Criar um novo DataFrame com os níveis de Fibonacci
        fib_data = pd.DataFrame({'23.6': [fib_236], '38.2': [fib_382], '50': [fib_05], '61.8': [fib_618]})

        # Salvar o DataFrame com os níveis de Fibonacci
        fib_data.to_csv('/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Dados_Fibo.csv', index=False)

        # Aguardar antes da próxima iteração
        time.sleep(1800)

        #bot.polling(non_stop=True)

    except Exception as e:
        print("Erro no loop principal:", e)
        continue