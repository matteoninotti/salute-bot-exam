'''
Autore: Matteo Ninotti
Data: 10/04/2026
Secondo Esercizio - Stringhe: Scrivere un programma che dica se una stringa è palindroma.
Esempio:
str="ABBA" PALINDROMA
str="PIPPO" NON PALINDROMA: 
'''

##
## Funzioni:
##
def is_palindromo(my_string: str) -> bool:
    '''
    Funzione: is_palindromo
    str my_string -> stringa su cui eseguire la funzione
    Valore di ritorno:
    bool -> True se la stringa è palindroma, False se la stringa non è palindroma
    '''
    if isinstance(my_string, str):
        if my_string[-1:0:-1] == my_string[0:-1:1]:
            return True
        else: return False
        # return stringa == stringa[::-1]
    else: return "inserisci solo stringhe"


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

print(is_palindromo(1991))              # int --> inserisci solo stringhe
print(is_palindromo("!@1991@!"))        # True
print(is_palindromo("Matteo Ninotti"))  # False
print(is_palindromo("Arianna Annaira"))  # False
print(is_palindromo("arianna annaira"))  # True
