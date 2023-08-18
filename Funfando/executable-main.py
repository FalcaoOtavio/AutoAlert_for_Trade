import subprocess
import time

def executar_coleta_de_dados():
    subprocess.Popen(['gnome-terminal', '--', 'python3', '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Dados.py'])

def executar_treinamento_da_IA():
    subprocess.Popen(['gnome-terminal', '--', 'python3', '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Brain.py'])

def executar_TeleBot():
    subprocess.Popen(['gnome-terminal', '--', 'python3', '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/TeleBot.py'])

def executar_Calculadore_Fibonacci():
    subprocess.Popen(['gnome-terminal', '--', 'python3', '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/calc_fibo.py'])

intervalo_de_tempo = 45  # Tempo mínimo para conseguir a primeira requisição de dados

executar_coleta_de_dados()

executar_TeleBot()

for i in range(1, 91):
    print(i)
    time.sleep(1)

executar_Calculadore_Fibonacci()

for i in range(1, 16):
    print(i)
    time.sleep(1)

#time.sleep(intervalo_de_tempo)

executar_treinamento_da_IA()