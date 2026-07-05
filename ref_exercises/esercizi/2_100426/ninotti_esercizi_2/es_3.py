'''
Autore: Matteo Ninotti
Data: 10/04/2026
Terzo Esercizio: Implementare una funzione convertiCF che converta una temperatura
espressa in gradi Fahrenheit in una temperatura espressa in gradi Celsius usando la
formula C = (F - 32) * 5 / 9. Creare un programma principale che richiami la funzione
e ne stampi il risultato visualizzando solo 3 cifre decimali.
'''
##
## Funzioni:
##

def convertiCF(f: float = 32.0) -> float:
    '''
    Funzione che converte una temperatura da gradi Fahrenheit a gradi Celsius.
    Formula: C = (F - 32) * 5 / 9
    Parametri formali:
    float f -> temperatura in gradi Fahrenheit (default: 32.0)
    Valore di ritorno:
    float -> temperatura convertita in gradi Celsius
    '''
    c = (f - 32) * 5 / 9   # Risultato della conversione in Celsius
    return c


'''
Programma principale
Chiede in input una temperatura in Fahrenheit, richiama convertiCF
e stampa il risultato con 3 cifre decimali.
'''

# Sezione di input Dati
try:
    fahrenheit = float(input("Inserisci la temperatura in gradi Fahrenheit: "))
except:
    print("Valore non valido. Inserire un numero.")
    exit()

# Inizializzazioni variabili
# celsius -> temperatura convertita in gradi Celsius

# Elaborazione
celsius = convertiCF(fahrenheit)

# Sezione di output
print(f"{fahrenheit}°F corrisponde a {celsius:.3f}°C")
