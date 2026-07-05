'''
Autore: Matteo Ninotti
Data: 30/05/2026
Titolo: 'Si definisca una classe Persona che abbia i seguenti attributi:
● nome
● indirizzo
● età
Tale classe contiene i seguenti metodi: il costruttore, l'overriding del metodo __str__
e tutti i metodi getter e setter degli attributi.
Si vogliono derivare dalla classe Persona le seguenti classi:
● Studente
● Lavoratore
La prima deve avere gli attributi aggiuntivi:
● Scuola
● Media voti
La seconda deve avere gli attributi aggiuntivi:
● Azienda
● Stipendio
Aggiungere tutti i metodi getter e setter relativi agli attributi aggiuntivi.
Inoltre effettuare l'overriding dei costruttori e del metodo str inserendo gli attributi aggiuntivi.
Provare le tre classi instanziando almeno un oggetto per classe e provando qualche metodo.'
'''
##
## Classi:
## 
class Persona:
    '''
    Classe: Persona
    Template per costruire le classi
    Attributi:
    str __nome -> nome privato della persona
    str __indirizzo -> indirizzo privato della persona
    int __eta -> età privata della persona
    '''
    def __init__(self, nome: str, indirizzo: str, eta: int) -> None:
        '''
        Metodo: __init__
        Template per costruire i metodi
        Parametri formali:
        str nome -> nome da assegnare alla persona
        str indirizzo -> indirizzo da assegnare alla persona
        int eta -> età da assegnare alla persona
        Valore di ritorno:
        None -> il metodo inizializza l'oggetto
        '''
        # Inizializzazione degli attributi privati dell'oggetto.
        self.__nome = nome
        self.__indirizzo = indirizzo
        self.__eta = eta

    @property
    def nome(self) -> str:
        '''
        Metodo: nome
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> nome privato della persona
        '''
        return self.__nome

    @property
    def indirizzo(self) -> str:
        '''
        Metodo: indirizzo
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> indirizzo privato della persona
        '''
        return self.__indirizzo

    @property
    def eta(self) -> int:
        '''
        Metodo: eta
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        int -> età privata della persona
        '''
        return self.__eta

    @nome.setter
    def nome(self, nome: str) -> None:
        '''
        Metodo: nome
        Template per costruire i metodi
        Parametri formali:
        str nome -> nuovo nome della persona
        Valore di ritorno:
        None -> il metodo modifica il nome privato della persona
        '''
        # Aggiornamento dell'attributo privato __nome.
        self.__nome = nome

    @indirizzo.setter
    def indirizzo(self, indirizzo: str) -> None:
        '''
        Metodo: indirizzo
        Template per costruire i metodi
        Parametri formali:
        str indirizzo -> nuovo indirizzo della persona
        Valore di ritorno:
        None -> il metodo modifica l'indirizzo privato della persona
        '''
        # Aggiornamento dell'attributo privato __indirizzo.
        self.__indirizzo = indirizzo

    @eta.setter
    def eta(self, eta: int) -> None:
        '''
        Metodo: eta
        Template per costruire i metodi
        Parametri formali:
        int eta -> nuova età della persona
        Valore di ritorno:
        None -> il metodo modifica l'età privata della persona
        '''
        # Aggiornamento dell'attributo privato __eta.
        self.__eta = eta

    def __str__(self) -> str:
        '''
        Metodo: __str__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> stringa con nome ed età della persona
        '''
        return f"Persona di nome {self.__nome} e età {self.__eta} anno/i" 



class Studente(Persona):
    '''
    Classe: Studente
    Template per costruire le classi
    Attributi:
    str __scuola -> scuola privata dello studente
    float __media_voti -> media voti privata dello studente
    '''
    def __init__(self, nome: str, indirizzo: str, eta: int, scuola: str, media_voti: float) -> None:
        '''
        Metodo: __init__
        Template per costruire i metodi
        Parametri formali:
        str nome -> nome da assegnare allo studente
        str indirizzo -> indirizzo da assegnare allo studente
        int eta -> età da assegnare allo studente
        str scuola -> scuola da assegnare allo studente
        float media_voti -> media voti da assegnare allo studente
        Valore di ritorno:
        None -> il metodo inizializza l'oggetto
        '''
        # Inizializzazione degli attributi ereditati dalla classe Persona.
        super().__init__(nome, indirizzo, eta)
        # Inizializzazione degli attributi privati specifici dello studente.
        self.__scuola = scuola
        self.__media_voti = media_voti

    @property
    def scuola(self) -> str:
        '''
        Metodo: scuola
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> scuola privata dello studente
        '''
        return self.__scuola

    @property
    def media_voti(self) -> float:
        '''
        Metodo: media_voti
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> media voti privata dello studente
        '''
        return self.__media_voti

    @scuola.setter
    def scuola(self, scuola: str) -> None:
        '''
        Metodo: scuola
        Template per costruire i metodi
        Parametri formali:
        str scuola -> nuova scuola dello studente
        Valore di ritorno:
        None -> il metodo modifica la scuola privata dello studente
        '''
        # Aggiornamento dell'attributo privato __scuola.
        self.__scuola = scuola

    @media_voti.setter
    def media_voti(self, media_voti: int) -> None:
        '''
        Metodo: media_voti
        Template per costruire i metodi
        Parametri formali:
        int media_voti -> nuova media voti dello studente
        Valore di ritorno:
        None -> il metodo modifica la media voti privata dello studente
        '''
        # Aggiornamento dell'attributo privato __media_voti.
        self.__media_voti = media_voti

    def __str__(self) -> str:
        '''
        Metodo: __str__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> stringa con nome, scuola e media voti dello studente
        '''
        return f"Studente di nome {self.nome}, scuola {self.__scuola} e media voti: {self.__media_voti}"



class Lavoratore(Persona):
    '''
    Classe: Lavoratore
    Template per costruire le classi
    Attributi:
    str __azienda -> azienda privata del lavoratore
    int __stipendio -> stipendio privato del lavoratore
    '''

    def __init__(self, nome: str, indirizzo: str, eta: int, azienda: str, stipendio: int) -> None:
        '''
        Metodo: __init__
        Template per costruire i metodi
        Parametri formali:
        str nome -> nome da assegnare al lavoratore
        str indirizzo -> indirizzo da assegnare al lavoratore
        int eta -> età da assegnare al lavoratore
        str azienda -> azienda da assegnare al lavoratore
        int stipendio -> stipendio da assegnare al lavoratore
        Valore di ritorno:
        None -> il metodo inizializza l'oggetto
        '''
        # Inizializzazione degli attributi ereditati dalla classe Persona.
        super().__init__(nome, indirizzo, eta)
        # Inizializzazione degli attributi privati specifici del lavoratore.
        self.__azienda = azienda
        self.__stipendio = stipendio

    @property
    def azienda(self) -> str:
        '''
        Metodo: azienda
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> azienda privata del lavoratore
        '''
        return self.__azienda

    @property
    def stipendio(self) -> int:
        '''
        Metodo: stipendio
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        int -> stipendio privato del lavoratore
        '''
        return self.__stipendio

    @azienda.setter
    def azienda(self, azienda: str) -> None:
        '''
        Metodo: azienda
        Template per costruire i metodi
        Parametri formali:
        str azienda -> nuova azienda del lavoratore
        Valore di ritorno:
        None -> il metodo modifica l'azienda privata del lavoratore
        '''
        # Aggiornamento dell'attributo privato __azienda.
        self.__azienda = azienda

    @stipendio.setter
    def stipendio(self, stipendio: int) -> None:
        '''
        Metodo: stipendio
        Template per costruire i metodi
        Parametri formali:
        int stipendio -> nuovo stipendio del lavoratore
        Valore di ritorno:
        None -> il metodo modifica lo stipendio privato del lavoratore
        '''
        # Aggiornamento dell'attributo privato __stipendio.
        self.__stipendio = stipendio

    def __str__(self) -> str:
        '''
        Metodo: __str__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> stringa con nome, azienda e stipendio del lavoratore
        '''
        return f"Lavoratore di nome {self.nome}, azienda {self.__azienda} e stipendio: {self.__stipendio}€"

'''
Programma principale
Descrizione sintetica funzionalità
del programma principale.
'''
# Sezione di input Dati
# Inizializzazioni variabili
# Elaborazione
# Eventuali sotto processi di Elaborazione
# Sezione di output

p1 = Persona("pippo", "casa sua", 45)
print(p1)
p1.nome = "giovanni"
print(p1)
print(p1.eta)

print("-"*30)

p2 = Studente("ciccio", "casa sua anche lui", 12, "Vincenzo Lauro", 8.5)
print(p2)
p2.scuola = "Giacomo Puccini"
print(p2.scuola)

print("-"*30)

p3 = Lavoratore("anselmo", "in ufficio sotto la scrivania", 32, "Ansaldo", 2500)
print(p3)
p3.stipendio = 3000
print(p3)
print(p3.azienda)
