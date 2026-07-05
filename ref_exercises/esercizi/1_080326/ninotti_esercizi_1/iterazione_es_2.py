'''
Autore: Matteo Ninotti
Data: 08/03/2026
Titolo: Si hanno in input N saldi di conti correnti bancari. Si vuole in output la media aritmetica dei soli conti correnti che hanno un saldo negativo.
'''

conti = [23000, 3400, -50, -47, 324.50, -1450, 0, -2345.76]

somma = 0
counter = 0

for n in conti:
    if n < 0:
        somma += n
        counter += 1

avg = round((somma/counter), 4)

print(f"la media dei conti in negativo è: {avg}")
