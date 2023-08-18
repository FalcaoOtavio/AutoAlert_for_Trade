import telebot
import time

# Substitua pelo seu token do bot
BOT_TOKEN = ''

# Substitua pelo chat ID do grupo para onde deseja enviar as mensagens
CHAT_ID = ''

print("BOT INICIADO!!")

# Inicialize o bot do Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Variável para armazenar a última linha do arquivo
ultima_linha = None

text0 = 'Welcome back, BOT Binance is started!'
if text0:    
    bot.send_message(CHAT_ID, text0)

# Armazena o último número de linhas do arquivo lido
ultima_quantidade_de_linhas = 0
ultima_linha_enviada = 0

# Inicializa a variável para verificar se é a primeira execução
primeira_execucao = True

while True:
    try:
        # Lê o conteúdo do arquivo previsoes.csv
        with open('/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/previsoes.csv', 'r') as arquivo:
            linhas = arquivo.readlines()
            quantidade_de_linhas = len(linhas)
            
            # Verifica se há novas linhas a serem processadas
            if quantidade_de_linhas > ultima_quantidade_de_linhas:
                # Envia a última linha para o grupo no Telegram
                linha = linhas[-1].strip()
                bot.send_message(CHAT_ID, linha)
                ultima_quantidade_de_linhas = quantidade_de_linhas

        # Aguarda antes da próxima iteração
        time.sleep(10)  # Aguarda 30 minutos

    except Exception as e:
        print("Erro no loop principal:", e)
        # Aguarda antes da próxima iteração em caso de erro
        time.sleep(1800)  # Aguarda 30 minutos
