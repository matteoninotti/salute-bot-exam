'''
Autore: Matteo Ninotti
Data: 08/04/2026
Primo Esercizio: Creare una funzione che riceva una quantità di tempo in formato ore,
minuti e secondi e la restituisca espressa solamente in secondi. Successivamente creare
un programma principale che chieda in input due quantità di tempo e stampi in output
quale quantità di tempo è maggiore. La funzione deve avere i parametri formali con valori
predefiniti.
'''
##
## Funzioni:
##

def convert_to_seconds(h:int, m:int, s:int) -> int:
    '''
    Funzione che converte un lasso temporale (e.g. h=5, m=53, s=16) e lo trasforma in lasso temporale in secondi
    Parametri formali:
    int h -> valore int da 0 a +infinito
    int m -> valore int da 0 a +infinito
    int s -> valore int da 0 a +infinito
    Valore di ritorno:
    int -> valore int da 0 a +infinito
    '''
    if h >= 0 and m >= 0 and s >= 0:
        total_seconds = h*3600+m*60+s
        return total_seconds
    else: return ("orario negativo, ritenta")


'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''

# Sezione di input Dati
try:
    hours,minutes,seconds = map(int, (input("inserisci ore, minuti, secondi separati da spazio: ").split()))
    seconds_1 = convert_to_seconds(hours, minutes, seconds)
    print(seconds_1)
except: 
    print("valori non corretti")
    exit()

try:
    hours,minutes,seconds = map(int, (input("inserisci ore, minuti, secondi separati da spazio: ").split()))
    seconds_2 = convert_to_seconds(hours, minutes, seconds)
    print(seconds_2)
except:
    print("valori non corretti")
    exit()

# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output
if seconds_2 > seconds_1:
    print(f"il tempo più alto è {seconds_2}")
elif seconds_1 > seconds_2:
    print(f"il tempo più alto è {seconds_1}")
else: print("tempi equivalenti")
