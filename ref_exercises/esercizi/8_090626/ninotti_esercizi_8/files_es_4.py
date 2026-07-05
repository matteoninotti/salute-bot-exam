'''
Autore: Matteo Ninotti
Data: 03/06/2026
Titolo: 'Scrivere un programma che permetta di copiare il contenuto di un file in un altro file.'
'''
from files_es_2 import read_file  # riciclato la funz dell'es 2



##
## Funzioni:
##
def copia_file(filepath_in: str) -> None:
    '''
    Funzione: copia_file
    Scopo: copiare il contenuto di un file nel file "output.txt".
    Parametri formali:
    str filepath_in -> path del file da copiare
    Valore di ritorno:
    None -> nessun valore di ritorno
    '''
    input_text = read_file(filepath_in)
    with open("output.txt", "w") as f:
        f.write(input_text)



'''
Programma principale
Descrizione sintetica: copia il contenuto del file "stringa.txt"
nel file "output.txt".
'''
# Elaborazione
copia_file("stringa.txt")
