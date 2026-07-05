'''
Autore: Matteo Ninotti
Data: 15/04/2026
Quarto Esercizio - Liste: Scrivere un programma Python per dividere una data lista in due parti in cui viene data la lunghezza della prima parte della lista.
Esempio:
Lista originale: [1, 1, 2, 3, 4, 4, 5, 1]
Lunghezza della prima parte della lista: 3
Output : Prima parte: [1, 1, 2] ,
Seconda parte: [3, 4, 4, 5, 1]
'''

##
## Funzioni:
##
def split_lista(lista: list, l: int) -> tuple | str:
    '''
    Funzione: split_lista
    Parametri formali:
    list lista -> lista da splittare
    int l -> lunghezza della prima parte della lista
    Valore di ritorno:
    tuple | str ret -> tupla contenente le due parti della lista | stringa di errore
    '''
    if len(lista) < l:
        ret = "posizione in cui splittare va oltre la lista"
    else:
        parte1 = []
        counter = 0
        for i in lista:
            if counter < l:
                parte1.append(i)
                counter += 1
            else: break
        
        # copia della lista per non sovrascriverla
        parte2 = lista[:]
        counter = 0
        for j in lista:
            if counter < l:
                parte2.remove(j)
                counter += 1
            else: break
        
        ret = parte1, parte2
    
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

lista = [1, "2", "3", 4]

print(split_lista(lista, 3))
print(lista) # la lista non viene sovrascritta perché l'abbiamo copiata
