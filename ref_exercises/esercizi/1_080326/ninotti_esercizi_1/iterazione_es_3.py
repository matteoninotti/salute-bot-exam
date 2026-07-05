'''
Autore: Matteo Ninotti
Data: 08/03/2026
Titolo: Leggere una successione di numeri interi passati dall’utente, fermandosi al primo numero che rende la successione non crescente e restituendo quanti numeri formano la successione inserita.
'''

successione = [-1, 0] 
# necessario inizializzare così la lista
# per soddisfare condiz del while

i = 1 

while successione[i] > successione[i-1]:
    n = input("inserisci un numero: ")
    try:
        n = float(n)
        successione.append(n)
        i += 1
    except:
        print("numero non inserito correttamente, riprova.")
        continue


for _ in range(2):
    successione.pop(0)
# rimuoviamo i due items a cui
# la lista era stata inizializzata

print(f"la successione crescente è: {successione}")
print(f"la successione conta {len(successione)} numero/i")

