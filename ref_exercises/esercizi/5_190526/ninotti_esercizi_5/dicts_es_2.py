'''
Autore: Matteo Ninotti
Data: 15/05/2026
Titolo: 'Scrivete uno script Python per generare e stampare un dizionario che contenga un numero
(compreso tra 1 e n) nella forma (x, x*x).
Esempio:
n = 5
Dizionario: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}'
'''
##
## Funzioni:
##
def diz_parabola(num_finale: int) -> dict:
  '''
  Funzione: diz_parabole
  Template per costruire le funzioni
  Parametri formali:
  int num_finale -> numero (compreso) fino a cui bisogna generare item di diz di tipo x : x*x
  Valore di ritorno:
  dict -> dizionario con item di tipo x : x*x
  '''
  return {num: num**2 for num in range(1, num_finale+1)}

'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(diz_parabola(5))