'''
Autore: Matteo Ninotti
Data: 15/04/2026
Secondo Esercizio - Liste: Scrivere un programma che date due liste stampi "OK" se hanno almeno un membro
comune altrimenti stampi "KO".
Esempio:
lista1=[1,5,8] lista2=[3,1,10] -> output: "OK"
lista1=[1,5,8] lista2=[3,11,10] -> output: "KO"
'''

##
## Funzioni:
##
def is_item_common(lista1: list, lista2: list) -> str:
    '''
    Funzione: is_item_common 
    Parametri formali:
    list lista1 -> lista da confrontare
    list lista2 -> lista da confrontare
    Valore di ritorno:
    str ret -> almeno un item comune -> "OK", altrimenti "KO"
    '''
    ret = "KO"
    for item in lista2:
        if item in lista1:
            ret = "OK"
    
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

lista1 = lista1=[1, 5, 8] 
lista2 = lista2=[3, 1, 10]  

print(is_item_common(lista1, lista2))

lista1 = lista1=["2"] 
lista2 = lista2=[2]

print(is_item_common(lista1, lista2))

