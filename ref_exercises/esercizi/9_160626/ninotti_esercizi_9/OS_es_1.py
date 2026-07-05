'''
Autore: Matteo Ninotti
Data: 10/06/2026
Titolo: 'Scrivere una procedura che dato un percorso elenchi tutte le directories presenti.'
'''
import os



##
## Funzioni:
##
def elenca_directories(percorso: str) -> None:
    '''
  Funzione: elenca_directories
  Scopo: dato un percorso, stampa tutte le directory in esso presenti
  Parametri formali:
  str percorso -> percorso di cui elencare le sottodirectory
  Valore di ritorno:
  None -> procedura, stampa a video le directory e non restituisce nulla
  '''
    for elemento in os.listdir(percorso):
        if os.path.isdir(os.path.join(percorso, elemento)):
            print(elemento)
    return None



'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
percorso = '.'  # percorso di cui elencare le directory
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
elenca_directories(percorso)
