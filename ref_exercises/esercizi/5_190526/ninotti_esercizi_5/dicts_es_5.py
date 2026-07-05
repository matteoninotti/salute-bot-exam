'''
Autore: Matteo Ninotti
Data: 15/05/2026
Titolo: 'Scrivete un programma Python per creare un dizionario da una stringa. Le lettere della
stringa rappresentano le chiavi, i valori rappresentano le occorrenze della chiave nella
stringa
Esempio
stringa = 'ciao mamma'
Dizionario: {'c': 1, 'i': 1, 'a': 3, 'o': 1, ' ':1,'m': 3}'
'''
##
## Funzioni:
##
def conta_lettere(stringa: str) -> dict:
  '''
  Funzione: conta_lettere
  Template per costruire le funzioni
  Parametri formali:
  str stringa -> stringa di cui contare le lettere
  Valore di ritorno:
  dict -> dizionario che conta le lettere tipo {lettera: numero_occorrenze}
  '''
  return {l: stringa.count(l) for l in set(stringa)}
  # se voglio ordinare le occorrenze dalla più freq alla meno freq:
  #   return {l: stringa.count(l) for l in sorted(set(stringa), key=stringa.count, reverse=True)}
  # oppure
  # from collections import Counter
  #   return dict(Counter(stringa).most_common())



'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
stringa1 = 'ciao mamma, guarda come mi diverto!'
stringa2 = 'Apelle, figlio di apollo, fece una palla di pelle di pollo. Tutti i pesci vennero a galla per vedere la palla di pelle di pollo fatta da apelle figlio di apollo'

# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
print(conta_lettere(stringa1))
print(conta_lettere(stringa2))
