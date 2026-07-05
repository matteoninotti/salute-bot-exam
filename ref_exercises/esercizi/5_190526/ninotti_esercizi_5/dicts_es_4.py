'''
Autore: Matteo Ninotti
Data: 15/05/2026
Titolo: 'Scrivete un programma Python per rimuovere i duplicati dal dizionario.'
'''
##
## Funzioni:
##
def rmv_dupl(diz: dict) -> dict:
  '''
  Funzione: rmv_dupl
  Template per costruire le funzioni
  Parametri formali:
  dict diz -> dizionario da cui rimuovere i valori duplicati
  Valore di ritorno:
  dict -> dzionario senza valori duplicati
  '''
  diz_unici = {}
  for k,v in diz.items():
    if v not in diz_unici.values():
      diz_unici[k] = v
  return diz_unici

'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
diz = {"a": 3,"b": 43,"c": -1,"d": 2,"e": 0, "f":43}

# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(rmv_dupl(diz))
