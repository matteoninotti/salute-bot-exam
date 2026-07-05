'''
Autore: Matteo Ninotti
Data: 10/06/2026
Titolo: 'Scrivere un programma che elimini tutti i files che contengono nel nome una sequenza di
caratteri dati in input.'
'''
import os



##
## Funzioni:
##
def elimina_files(percorso: str, sequenza: str) -> list:
    '''
    Funzione: elimina_files
    Scopo: elimina i files il cui nome contiene una data sequenza di caratteri
    Parametri formali:
    str percorso -> percorso in cui cercare ed eliminare i files
    str sequenza -> sequenza di caratteri che il nome del file deve contenere per essere eliminato
    Valore di ritorno:
    list -> lista dei nomi dei files che sono stati eliminati
    '''
    eliminati = []
    for elemento in os.listdir(percorso):
        percorso_completo = os.path.join(percorso, elemento)
        if os.path.isfile(percorso_completo) and sequenza in elemento:
            os.remove(percorso_completo)
            eliminati.append(elemento)
    return eliminati



'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
percorso = input(
    'Percorso in cui eliminare i files: ')  # cartella in cui cercare i files
sequenza = input('Sequenza di caratteri nel nome: '
                 )  # sequenza da cercare nei nomi dei files
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print('Files eliminati:', elimina_files(percorso, sequenza))
