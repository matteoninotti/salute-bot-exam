'''
Autore: Matteo Ninotti
Data: 15/04/2026
Terzo Esercizio - Liste: Scrivi un programma per trovare il secondo numero più piccolo in una lista.
'''
import numbers

##
## Funzioni:
##
def is_list_of_numbers(lista: list) -> bool:
  '''
  Funzione: is_list_of_numbers
  Parametri formali:
  list lista -> lista da validare come lista di soli numeri 
  Valore di ritorno:
  bool -> se lista di soli num: True | False 
  '''
  ret = True    
  for i in lista:
    if not isinstance(i, numbers.Number):
      ret = False
  return ret

def bubble_sort_two_items(lista: list) -> list:
  '''
  Funzione: bubble_sort_two_items
  Parametri formali:
  list lista -> lista da ordinare asc 
  Valore di ritorno:
  list ordinata -> lista ordinata asc
  '''
  # Copia per non modificare la lista originale
  ordinata = lista[:]
  n = len(ordinata)
  # Bubble "da destra a sinistra":
  # passata 0 -> porta il minimo in posizione 0
  # passata 1 -> porta il secondo minimo in posizione 1
  passate = min(2, n - 1)
  for i in range(passate):
    scambio = False
    for j in range(n - 1, i, -1):
      if ordinata[j] < ordinata[j - 1]:
        ordinata[j], ordinata[j - 1] = ordinata[j - 1], ordinata[j]
        scambio = True
      # se non ci sono scambi, la lista è già ordinata
    if not scambio:
      break
  return ordinata[:2]

def second_smallest(lista: list) -> tuple:
  '''
  Funzione: second_smallest 
  Parametri formali:
  list lista -> lista su cui trovare il secondo num più piccolo. dev'essere lista di numeri
  Valore di ritorno:
  tuple ret -> secondo num più piccolo, codice errore 
  ''' 
  if len(lista) < 2:
    ret = None, 1
  elif not is_list_of_numbers(lista):
    ret = None, 2
  else:
    ordinata = bubble_sort_two_items(lista)
    ret = ordinata[1], 0
  
  return ret
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

lista = [21, 6, 67, 4, 2, 43, 643, 2.5, 653, 3, 6543]

print(second_smallest(lista))

