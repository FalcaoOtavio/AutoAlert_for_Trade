import os
import time

# DATA
def executar_coleta_de_dados():
    os.system('python3 /home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Coding/Dados.py')

# AI
def executar_treinamento_da_IA():
    os.system('python3 /home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Coding/Brain.py')

intervalo_de_tempo = 90  # Tempo mínimo para conseguir a primeira requisição de dados

executar_coleta_de_dados()

time.sleep(intervalo_de_tempo)

executar_treinamento_da_IA()