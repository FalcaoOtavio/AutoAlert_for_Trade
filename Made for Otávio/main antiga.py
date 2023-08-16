import os
import time

# DATA
def executar_coleta_de_dados():
    os.system('python Dados.py')

# AI
def executar_treinamento_da_IA():
    os.system('python Brain.py')

intervalo_de_tempo = 30 #Tempo minimo para conseguir a primeira requisiçao de dados  

executar_coleta_de_dados()
    
time.sleep(intervalo_de_tempo)
    
executar_treinamento_da_IA()
    
