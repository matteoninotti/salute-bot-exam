'''
Autore: Matteo Ninotti
Data: 10/06/2026
Titolo: 'Scrivere un programma che esamini tutte le directories sotto un dato percorso e conti tutti
i files con una determinata estensione data in input. [In prima battuta fermatevi al primo
livello di profondità delle directories]'
'''
import os



##
## Funzioni:
##
def conta_files_estensione(percorso: str, estensione: str) -> int:
    '''
    Funzione: conta_files_estensione
    Scopo: conta i files con una data estensione nelle sottodirectory di primo livello del percorso
    Parametri formali:
    str percorso -> percorso le cui sottodirectory (primo livello) vengono esaminate
    str estensione -> estensione dei files da contare (es. '.txt')
    Valore di ritorno:
    int -> numero di files con la data estensione trovati nelle sottodirectory
    '''
    contatore = 0
    for elemento in os.listdir(percorso):
        percorso_dir = os.path.join(percorso, elemento)
        if os.path.isdir(percorso_dir):
            for file in os.listdir(percorso_dir):
                if file.endswith(estensione):
                    contatore += 1
    return contatore



'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
percorso = input('Percorso da esaminare: '
                 )  # percorso radice di cui esaminare le sottodirectory
estensione = input(
    'Estensione (es. .txt): ')  # estensione dei files da contare
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(conta_files_estensione(percorso, estensione))
