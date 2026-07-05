'''
Autore: Matteo Ninotti
Data: 06/03/2026
Titolo: Scrivere un programma che legga i coeﬃcienti a, b e c di un'equazione di secondo grado
ax^2+bx+c=0 e ne scriva le soluzioni.
'''

import math
coefficients = []

while True:
    coefficients = input("scrivi i tre coefficienti a, b, c separati da spazio (q per uscire): ").split()
    if all(w != "q" for w in coefficients):

        try:
            a, b, c = map(float, coefficients)
            discriminante = b**2 - 4*a*c
            if discriminante > 0:
                result1 = round(((-b + math.sqrt(discriminante))/2*a), 4)
                result2 = round(((-b - math.sqrt(discriminante))/2*a), 4)
                print(f"i risultati dell'equazione {a}x^2+{b}x+{c} sono: {result1}, {result2}")
            else:
                print(f"il risultato dell'equazione {a}x^2+{b}x+{c} è: impossibile (discriminante = {discriminante})")
        except:
            print("coefficienti non inseriti correttamente")

    else:
        print("programma terminato")
        break
