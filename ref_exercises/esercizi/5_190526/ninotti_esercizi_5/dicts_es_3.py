'''
Autore: Matteo Ninotti
Data: 15/05/2026
Titolo: 'Scrivete un programma Python per ottenere il valore massimo e minimo in un dizionario.'
'''



##
## Funzioni:
##
def maxmin_dict(diz: dict) -> tuple:
    '''
  Funzione: maxmin_dict
  Template per costruire le funzioni
  Parametri formali:
  dict diz -> dizionario da cui trarre massimo e minimo
  Valore di ritorno:
  tuple -> tupla comoposta da due diz di un elemento ciascuno,
    tipo ({massimo: diz[massimo]}, {minimo, diz[minimo]})
  '''
    massimo = max(diz.keys(), key=lambda k: diz[k])
    minimo = min(diz.keys(), key=lambda k: diz[k])
    return {massimo: diz[massimo]}, {minimo: diz[minimo]}



'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
diz = {"a": 3, "b": 43, "c": -1, "d": 2, "e": 0}
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(maxmin_dict(diz))
