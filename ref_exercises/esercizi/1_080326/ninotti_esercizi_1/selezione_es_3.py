'''
Autore: Matteo Ninotti
Data: 08/03/2026
Titolo: Scrivere un programma che legga il raggio r di una circonferenza e ne calcoli l'area e la lunghezza.
'''

PI = 3.14

while True:

    r = input("inserisci il raggio (q per uscire): ")

    if r != "q":

        try:
            r = float(r)
            if r > 0:
                circ = round(2*PI*r, 4)
                area = round(PI*r**2, 4)
                print(f"l'area del cerchio di raggio = {r} è: {area}")
                print(f"l'area del cerchio di raggio = {r} è: {area}")
            else: print("raggio negativo")
        except: print("raggio non inserito correttamente")

    else:
        print("alla prossima!")
        break

