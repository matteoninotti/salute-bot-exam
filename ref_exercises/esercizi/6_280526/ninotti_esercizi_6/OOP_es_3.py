'''
Autore: Matteo Ninotti
Data: 25/05/2026
Titolo: '1 - Creare una classe Calcolo con un costruttore di default (senza parametri) che consenta
di eseguire vari calcoli su numeri interi.
2 - Creare un metodo chiamato Factorial() che permetta di calcolare il fattoriale di un
intero. Testare il metodo istanziando la classe.
3 - Creare un metodo chiamato Sum() che consenta di calcolare la somma dei primi n
interi 1 + 2 + 3 + .. + n. Prova questo metodo.
4 - Creare un metodo tableMult() che crea e visualizza la tabellina di un dato intero. Quindi
creare un metodo allTablesMult() per visualizzare tutte le tabelline di numeri interi 1, 2, 3, ..., 9.'
'''
import json

##
## Classi:
##
class Calcolo:
  '''
  Classe: Calcolo
  Template per costruire le classi
  Attributi:
  Nessuno
  '''
  
  def __init__(self):
    '''
    Metodo: __init__
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    None -> il metodo inizializza l'oggetto
    '''
    pass
  
  def factorial(self, n: int) -> int:
    '''
    Metodo: factorial
    Template per costruire i metodi
    Parametri formali:
    int n -> numero intero di cui calcolare il fattoriale
    Valore di ritorno:
    int -> fattoriale del numero intero indicato
    '''
    # Controllo che il numero non sia negativo.
    if n < 0:
      raise ValueError("n must be non-negative")
    # Caso base della funzione ricorsiva.
    if n <= 1:
      return 1
    return n * self.factorial(n - 1)
  
  def sum(self, n: int) -> int:
    '''
    Metodo: sum
    Template per costruire i metodi
    Parametri formali:
    int n -> numero finale della somma dei primi n interi
    Valore di ritorno:
    int -> somma dei primi n numeri interi
    '''
    # Controllo che il numero non sia negativo.
    if n < 0:
      raise ValueError("n must be non-negative")
    # Caso base della funzione ricorsiva.
    if n <= 1:
      return 1
    return n + self.sum(n - 1)
  
  def tableMult(self, n: int) -> dict:
    '''
    Metodo: tableMult
    Template per costruire i metodi
    Parametri formali:
    int n -> numero intero di cui generare la tabellina
    Valore di ritorno:
    dict -> dizionario con la tabellina del numero indicato
    '''
    # Generazione della tabellina da 1 a 10.
    return {str(n) + " * " + str(i): n*i for i in range(1,11)} # {"n*1": x, "n*2": y, "n*3": z}
  
  def allTableMult(self) -> object:
    '''
    Metodo: allTableMult
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    object -> stringa json con tutte le tabelline da 1 a 9
    '''
    # Generazione delle tabelline da 1 a 9 in formato json.
    return json.dumps([self.tableMult(i) for i in range(1,10)], indent=2)

'''
Programma principale
Descrizione sintetica funzionalitàl
del programma principale.
'''
# Sezione di input Dati
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
calc = Calcolo()
try:
  print(calc.factorial(4))
except ValueError as e:
  print(e)
  
try:
  print(calc.sum(4))
except ValueError as e:
  print(e)

print(calc.tableMult(5))

print(calc.allTableMult())
