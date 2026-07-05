'''
Autore: Matteo Ninotti
Data: 10/04/2026
Secondo Esercizio: Creare una funzione che abbia come parametri formali un numero
arbitrario di valori numerici. Si vuole che restituisca la somma dei soli numeri pari
e il prodotto dei soli numeri dispari. Successivamente creare un programma che
richiami tale funzione e che stampi in output i risultati. No standard input.
'''
##
## Funzioni:
##

def somma_pari_prodotto_dispari(*numeri: int) -> tuple:
    '''
    Funzione che riceve un numero arbitrario di valori interi e restituisce
    la somma dei soli numeri pari e il prodotto dei soli numeri dispari.
    Parametri formali:
    *numeri -> sequenza arbitraria di valori int
    Valore di ritorno:
    tuple -> (int somma_pari, int prodotto_dispari)
    '''
    somma_pari = 0         # Accumulatore per la somma dei numeri pari
    prodotto_dispari = 1   # Accumulatore per il prodotto dei numeri dispari

    for n in numeri:
        if n % 2 == 0:
            somma_pari += n
        else:
            prodotto_dispari *= n

    return somma_pari, prodotto_dispari


'''
Programma principale
Chiama somma_pari_prodotto_dispari con una lista fissa di numeri (no standard input)
e stampa i risultati.
'''

# Sezione di input Dati
numeri_test = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

# Inizializzazioni variabili
# somma_p    -> somma dei numeri pari presenti in numeri_test
# prodotto_d -> prodotto dei numeri dispari presenti in numeri_test

# Elaborazione
somma_p, prodotto_d = somma_pari_prodotto_dispari(*numeri_test)

# Sezione di output
print(f"Numeri: {numeri_test}")
print(f"Somma dei numeri pari: {somma_p}")
print(f"Prodotto dei numeri dispari: {prodotto_d}")
