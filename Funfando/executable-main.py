import subprocess
import time

def executar_coleta_de_dados():
    subprocess.Popen(['gnome-terminal', '--', 'python3', '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Dados.py'])

def executar_treinamento_da_IA():
    subprocess.Popen(['gnome-terminal', '--', 'python3', '/home/otavio/Documentos/Programas/Pessoais/AutoAlert_for_Trade/Funfando/Brain.py'])

intervalo_de_tempo = 45  # Tempo mínimo para conseguir a primeira requisição de dados

executar_coleta_de_dados()

time.sleep(intervalo_de_tempo)

executar_treinamento_da_IA()