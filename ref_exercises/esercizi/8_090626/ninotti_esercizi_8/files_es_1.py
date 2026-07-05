'''
Autore: Matteo Ninotti
Data: 03/06/2026
Titolo: 'Scrivere un programma che, leggendo da tastiera una stringa, la salvi su file “stringa.txt”.
Successivamente aprire il file “stringa.txt” e verificare il salvataggio.'
'''



##
## Funzioni:
##
def salva_stringa(stringa: str) -> None:
    '''
    Funzione: salva_stringa
    Scopo: salvare una stringa nel file "stringa.txt".
    Parametri formali:
    str stringa -> stringa da scrivere su file
    Valore di ritorno:
    None -> nessun valore di ritorno
    '''

    with open("stringa.txt", "w") as f:
        f.write(stringa)



def leggi_file() -> str:
    '''
    Funzione: leggi_file
    Scopo: leggere il contenuto del file "stringa.txt".
    Parametri formali:
    Nessuno
    Valore di ritorno:
    str -> contenuto del file letto
    '''
    with open("stringa.txt") as f:
        return f.read()



'''
Programma principale
Descrizione sintetica: legge una stringa da tastiera, la salva su file
e stampa il contenuto del file per verificarne il salvataggio.
'''
# Sezione di input Dati
stringa = input("inserisci stringa da scrivere su file: ")

# Elaborazione
salva_stringa(stringa)

# Sezione di output
print(leggi_file())
