'''
Autore: Matteo Ninotti
Data: 06/03/2026
Titolo: Scrivere un programma che legga i coefficienti a e b di un'equazione di primo grado ax=b e
ne scriva la soluzione (attenzione al dominio del coefficiente a)
'''

a = input("coefficiente a: ")
b = input("coefficiente b: ")

try:
    a = float(a)
    b = float(b)
    if a != 0:
        x = round(b/a, 4)
        print(f"il risultato dell'equazione {a}x = {b} è: x = {x}")
    else: print(f"il risultato dell'equazione {a}x = {b} è: impossibile (divisione per zero)")

except: print("coefficienti non inseriti correttamente")



