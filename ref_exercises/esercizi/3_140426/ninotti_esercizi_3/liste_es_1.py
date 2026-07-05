'''
Autore: Matteo Ninotti
Data: 15/04/2026
Primo Esercizio - Liste: Scrivere un programma python che rimuova gli elementi duplicati da una lista.
Esempio:
listaIN = [2, -4, 5, 6, 5, 5, 2]
listaOUT=[2, -4, 5, 6]
'''
##
## Funzioni:
##
def rimuovi_duplicati(lista_in: list) -> list:

    '''
    Funzione: rimuovi_duplicati
    Parametri formali:
    list lista_in -> lista da cui rimuovere i duplicati
    Valore di ritorno:
    list lista_out -> lista modificata
    '''
    lista_out = lista_in

    for i in lista_in:
        if lista_in.count(i) > 1:
            lista_out.remove(i)

    return lista_out

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

lista1 = ["2", 2, "q", {4,5,6}, {5,6,7}, "matteo", ("ci", "ao"), ["ci","ao"], 89, {4,5,6}, "matteo", "matteo"]
lista2 = [2, -4 ,5,6,5,5,2]
print(rimuovi_duplicati(lista1))
print(rimuovi_duplicati(lista2))
