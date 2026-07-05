'''
Autore: Matteo Ninotti
Data: 10/04/2026
Quarto Esercizio: Calcolo approssimato del numero di Nepero e mediante la serie
e = sum(1/n!) per n da 0 a N-1. La funzione calcola_e richiama la funzione fattoriale
e restituisce sia il valore approssimato di e sia l'errore rispetto al valore reale.
'''
##
## Funzioni:
##

NEPERO = 2.718281828459045   # Valore reale del numero di Nepero (variabile globale)


def fattoriale(n: int = 0) -> int:
    '''
    Funzione che calcola il fattoriale di un numero intero non negativo.
    Parametri formali:
    int n -> numero intero non negativo (default: 0)
    Valore di ritorno:
    int -> valore del fattoriale di n (n!)
    '''
    if n < 0:
        return None   # Fattoriale non definito per numeri negativi

    risultato = 1   # Accumulatore del prodotto
    for i in range(2, n + 1):
        risultato *= i

    return risultato


def calcola_e(n: int = 1) -> tuple:
    '''
    Funzione che restituisce un valore approssimato del numero di Nepero e
    calcolato con i primi N termini della serie e = sum(1/k!) per k da 0 a N-1.
    Richiama internamente la funzione fattoriale.
    Parametri formali:
    int n -> numero di termini della serie da sommare (default: 1)
    Valore di ritorno:
    tuple -> (float valore_approssimato, float errore)
             errore = NEPERO - valore_approssimato
    '''
    if n <= 0:
        return None, None   # Numero di termini non valido

    somma = 0.0   # Accumulatore della serie

    for k in range(n):
        somma += 1 / fattoriale(k)

    errore = NEPERO - somma   # Differenza tra il valore reale e quello approssimato

    return somma, errore


'''
Programma principale
Chiede in input il numero N di termini, calcola l'approssimazione di e
tramite calcola_e e stampa il valore ottenuto e l'errore commesso.
'''

# Sezione di input Dati
try:
    N = int(input("Inserisci il numero di termini N per il calcolo di e: "))
    if N <= 0:
        print("Il numero di termini deve essere un intero positivo.")
        exit()
except ValueError:
    print("Valore non valido. Inserire un numero intero.")
    exit()

# Inizializzazioni variabili
# valore_e -> approssimazione di e con N termini
# errore_e -> differenza tra NEPERO e valore_e

# Elaborazione
valore_e, errore_e = calcola_e(N)

# Sezione di output
print(f"Valore approssimato di e con {N} termini: {valore_e}")
print(f"Valore reale di e:                        {NEPERO}")
print(f"Errore commesso:                          {errore_e}")
