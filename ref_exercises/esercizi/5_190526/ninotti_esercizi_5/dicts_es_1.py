'''
Autore: Matteo Ninotti
Data: 15/05/2026
Titolo: 'Progettare una funzione che accetti un numero indefinito di dizionari e restituisca un
dizionario che è la concatenazione di tutti i dizionari indicati come parametro formale alla
funzione. Scrivete uno script che utilizzi tale funzione.
Esempio:
diz1 = {'v1':1,'v2':2,'v3':3}
diz2 = {'v4':4,'v5':5,'v6':6}
diz3 = {'v7':7,'v8':8}
Dizionario restituito: {'v1': 1, 'v2': 2, 'v3': 3, 'v4': 4,
'v5': 5, 'v6': 6, 'v7': 7, 'v8': 8}'
'''
##
## Funzioni:
##
def concat_dicts(*dicts: dict) -> dict:
  '''
  Funzione: concat_dicts
  Template per costruire le funzioni
  Parametri formali:
  dict *dicts -> dicts passati con *args (numero indef di dicts)
  float Param2 -> descrizione Param2
  Valore di ritorno:
  int -> descrizione valore di ritorno
  '''
  diz_concatenato = {}
  for diz in dicts:
    diz_concatenato.update(diz)
  return diz_concatenato

'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
diz_1 = {'v1':1,'v2':2,'v3':3}
diz_2 = {'v4':4,'v5':5,'v6':6}
diz_3 = {'v7':7,'v8':8}
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(concat_dicts(diz_1, diz_2, diz_3))
