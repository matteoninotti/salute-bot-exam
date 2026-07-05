'''
Autore: Matteo Ninotti
Data: 10/04/2026
Primo Esercizio - Stringhe: Scrivere un programma per rimuovere l'n- esimo carattere da una stringa non vuota. Progettare una funzione che accetti la stringa, la posizione del carattere e restituisca la stringa modificata: 
'''
##
## Funzioni:
##
def rimuovi_char(stringa: str, indice: int) -> str:
    '''
    Funzione: rimuovi_char
    Parametri formali:
    str stringa -> stringa da cui rimuovere l'elemento n-esimo
    int indice  -> indice dell'elemento da rimuovere (positivo o negativo, con wrap-around automatico oltre la lunghezza della stringa)
    Valore di ritorno:
    str -> stringa modificata
    '''
    
    l_str = len(stringa)

    # il modulo gestisce wrap-around per qualsiasi indice, positivo o negativo, anche oltre l_str
    if l_str > 0:
        ind_norm = indice % l_str
        
        new_stringa = stringa[:ind_norm] + stringa[ind_norm + 1:]
        return new_stringa
    else: return "stringa vuota"

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
print(rimuovi_char("matteoninotti", -15))
print(rimuovi_char("ot", -15))
print(rimuovi_char("aca", -1))
print(rimuovi_char("matteoninotti", -1500))
print(rimuovi_char("matteoninotti", -1))
print(rimuovi_char("", 1))
