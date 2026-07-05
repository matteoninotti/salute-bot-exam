'''
Autore: Matteo Ninotti
Data: 03/06/2026
Titolo: 'Progetta una classe che legga un file di testo. Tale classe deve avere un metodo che restituisca la parola con frequenza maggiore. [Suggerimento: si consideri l'esercizio che contava le frequenze delle lettere in una stringa utilizzando i dictionary]
Provare il programma con testi classici come la Divina Commedia di Dante Alighieri
reperibile sul sito del progetto Gutenberg.'
'''
from collections import Counter

from files_es_2 import read_file  # riciclato la funz dell'es 2


##
## Classi:
##
class Words_counter:
    '''
    Classe: Words_counter
    Scopo: leggere un file di testo e trovare la parola con frequenza maggiore.
    Attributi:
    str __filepath_in -> path del file da leggere
    '''

    def __init__(self, filepath_in: str) -> None:
        '''
        Funzione: __init__
        Scopo: inizializzare il path del file di input.
        Parametri formali:
        str filepath_in -> path del file da leggere
        Valore di ritorno:
        None -> nessun valore di ritorno
        '''
        self.__filepath_in = filepath_in

    def word_freq_counter(self) -> str:
        '''
        Funzione: word_freq_counter
        Scopo: trovare la parola con frequenza maggiore nel file di input.
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> parola con frequenza maggiore
        '''
        words = read_file(self.__filepath_in).split()
        return Counter(words).most_common(1)[0][0]
        # se invece non voglio usare Counter():
        # return max({w: words.count(w) for w in set(words)})



'''
Programma principale
Descrizione sintetica: legge un file di testo e stampa la parola
con frequenza maggiore.
'''
# Inizializzazioni variabili
wc = Words_counter("stringa.txt")

# Sezione di output
print(wc.word_freq_counter())
