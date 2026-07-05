'''
Autore: Matteo Ninotti
Data: 03/06/2026
Titolo: 'Scrivi una classe che legga un file di testo e stampi sul file: “output.txt” la parola più lunga
contenuta. [Facoltativo: stampi sul file: “output.txt” le prime N parole più lunghe, N è dato
in input dall'utente].
Istanziare la classe e provare i metodi implementati.'
'''



##
## Funzioni:
##
def read_file(filepath_in: str) -> str:
    '''
    Funzione: read_file
    Scopo: leggere il contenuto di un file di testo.
    Parametri formali:
    str filepath_in -> path del file da leggere
    Valore di ritorno:
    str -> contenuto del file letto
    '''
    with open(filepath_in) as f:
        return f.read()



##
## Classi:
##



class Longest_word_writer:
    '''
    Classe: Longest_word_writer
    Scopo: trovare la parola più lunga in un file di input e scriverla
    in un file di output.
    Attributi:
    str __filepath_in -> path del file da leggere
    str __filepath_out -> path del file da scrivere
    '''

    def __init__(self, filepath_in: str, filepath_out: str):
        '''
        Funzione: __init__
        Scopo: inizializzare i path dei file di input e output.
        Parametri formali:
        str filepath_in -> path del file su cui si vuole trovare la parola più lunga
        str filepath_out -> path del file su cui si vuole scrivere la parola più lunga
        Valore di ritorno:
        None -> nessun valore di ritorno
        '''
        self.__filepath_in = filepath_in
        self.__filepath_out = filepath_out

    @property
    def filepath_in(self) -> str:
        '''
        Funzione: filepath_in
        Scopo: restituire il path del file di input.
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> path del file di input
        '''
        return self.__filepath_in

    @property
    def filepath_out(self) -> str:
        '''
        Funzione: filepath_out
        Scopo: restituire il path del file di output.
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> path del file di output
        '''
        return self.__filepath_out

    def find_longest_word(self) -> str:
        '''
        Funzione: find_longest_word
        Scopo: trovare la parola più lunga nel file di input.
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> parola più lunga trovata nel file
        '''
        words = read_file(self.filepath_in).split()
        return max(words, key=len)

    def write_word(self, parola: str) -> None:
        '''
        Funzione: write_word
        Scopo: scrivere una parola nel file di output.
        Parametri formali:
        str parola -> parola da scrivere su file
        Valore di ritorno:
        None -> nessun valore di ritorno
        '''
        with open(self.filepath_out, "w") as f:
            f.write(parola)



'''
Programma principale
Descrizione sintetica: legge un file di testo, trova la parola più lunga
e la scrive nel file "output.txt".
'''
# Inizializzazioni variabili
lw = Longest_word_writer("stringa.txt", "output.txt")

# Elaborazione
longest_word = lw.find_longest_word()

# Sezione di output
lw.write_word(longest_word)
