'''
Autore: Matteo Ninotti
Data: 10/06/2026
Titolo: 'Scrivere un programma Python per eseguire un comando del sistema operativo usando il
modulo os.'
'''
import os



##
## Funzioni:
##
def esegui_comando(comando: str) -> str:
    '''
    Funzione: esegui_comando
    Scopo: esegue un comando del sistema operativo tramite il modulo os
    Parametri formali:
    str comando -> comando del sistema operativo da eseguire
    Valore di ritorno:
    str -> output restituito dal comando
    '''
    output = os.popen(comando).read()
    return output



'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
comando = 'ls -la'  # comando del sistema operativo da eseguire
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(comando)
print(esegui_comando(comando))
