import telebot
from API_Key import API_Telegram
import queue
import threading

# Inicialize o bot e a fila de mensagens
telegram = API_Telegram
bot = telebot.TeleBot(telegram)
message_queue = queue.Queue()
#Usuários que devem receber as atualizações
chat_ids = [936629591]
print('Bot Telegram INICIADO')

@bot.message_handler(commands=['start'])
def start(mensagem):
    text = 'Welcome back, BOT Binance is started!'
    bot.send_message(mensagem.chat.id, text)

# Função para enviar movimentações importantes para a fila de mensagens
def send_notification(message):
    message_queue.put(message)

# Função para verificar e processar mensagens da fila (opcional, dependendo do uso)
def process_message_queue():
    while True:
        message = message_queue.get()
        if message is None:
            break
        print(f"Received message: {message}")

# Função para receber e processar notificações do AutoTrade.py
@bot.message_handler(commands=['notify'])
def notify(message):
    # Processa a mensagem de notificação recebida
    notification = message.text.split(" ", 1)[1]
    # Envia a mensagem para a fila de mensagens do AutoTrade.py
    send_notification(notification)


bot.polling(non_stop=True)