'''
Autore: Matteo Ninotti
Data: 30/05/2026
Titolo: 'Creare una classe AritmeticaDue con attributi operando1 e operando2. Definire il
costruttore utilizzando parametri con valori predefiniti e il metodo str.
Aggiungere due metodi uno che restituisca la differenza e l'altro il prodotto dei due
operandi. Implementare un terzo metodo che permetta il confronto tra il risultato del
prodotto di due oggetti AritmeticaDue (in sostanza indicare se il prodotto è maggiore di
quello calcolato nell'oggetto AritmeticaDue passato come parametro).
Derivare dalla classe AritmeticaDue la classe AritmeticaTre aggiungendo l'attributo
operando3. Ridefinire il costruttore, il metodo str e i tre metodi differenza, prodotto e
confronto. Aggiungere un metodo per il calcolo della somma di tutti gli attributi.
Provare le classi e i metodi implementati.'
'''



##
## Classi:
##
class AritmeticaDue:
    '''
    Classe: AritmeticaDue
    Template per costruire le classi
    Attributi:
    float __op1 -> primo operando privato
    float __op2 -> secondo operando privato
    '''

    def __init__(self) -> None:
        '''
        Metodo: __init__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        None -> il metodo inizializza l'oggetto
        '''
        # Inizializzazione degli attributi privati dell'oggetto.
        self.__op1 = 1
        self.__op2 = 2

    @property
    def op1(self) -> float:
        '''
        Metodo: op1
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> primo operando privato
        '''
        return self.__op1

    @property
    def op2(self) -> float:
        '''
        Metodo: op2
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> secondo operando privato
        '''
        return self.__op2

    @op1.setter
    def op1(self, op1) -> None:
        '''
        Metodo: op1
        Template per costruire i metodi
        Parametri formali:
        float op1 -> nuovo valore del primo operando
        Valore di ritorno:
        None -> il metodo modifica il primo operando privato
        '''
        # Aggiornamento dell'attributo privato __op1.
        self.__op1 = op1

    @op2.setter
    def op2(self, op2) -> None:
        '''
        Metodo: op2
        Template per costruire i metodi
        Parametri formali:
        float op2 -> nuovo valore del secondo operando
        Valore di ritorno:
        None -> il metodo modifica il secondo operando privato
        '''
        # Aggiornamento dell'attributo privato __op2.
        self.__op2 = op2

    def __str__(self) -> str:
        '''
        Metodo: __str__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> stringa con i due operandi
        '''
        return f"{self.__op1}, {self.__op2}"

    def diff(self) -> float:
        '''
        Metodo: diff
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> differenza tra i due operandi
        '''
        # Calcolo della differenza tra il primo e il secondo operando.
        return self.__op1 - self.__op2

    def prod(self) -> float:
        '''
        Metodo: prod
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> prodotto tra i due operandi
        '''
        # Calcolo del prodotto tra il primo e il secondo operando.
        return self.__op1 * self.__op2

    def confr_prod(self, ogg2: "AritmeticaDue") -> bool:
        '''
        Metodo: confr_prod
        Template per costruire i metodi
        Parametri formali:
        AritmeticaDue ogg2 -> oggetto con cui confrontare il prodotto
        Valore di ritorno:
        bool -> True se il prodotto dell'oggetto chiamante è maggiore, False se non lo è
        '''
        # Confronto tra il prodotto dell'oggetto chiamante e quello dell'oggetto parametro.
        return self.prod() > ogg2.prod()



class AritmeticaTre(AritmeticaDue):
    '''
    Classe: AritmeticaTre
    Template per costruire le classi
    Attributi:
    float __op3 -> terzo operando privato
    '''

    def __init__(self) -> None:
        '''
        Metodo: __init__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        None -> il metodo inizializza l'oggetto
        '''
        # Inizializzazione degli attributi ereditati dalla classe AritmeticaDue.
        super().__init__()
        # Inizializzazione dell'attributo privato specifico di AritmeticaTre.
        self.__op3 = 3

    @property
    def op3(self) -> float:
        '''
        Metodo: op3
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> terzo operando privato
        '''
        return self.__op3

    @op3.setter
    def op3(self, op3: float) -> None:
        '''
        Metodo: op3
        Template per costruire i metodi
        Parametri formali:
        float op3 -> nuovo valore del terzo operando
        Valore di ritorno:
        None -> il metodo modifica il terzo operando privato
        '''
        # Aggiornamento dell'attributo privato __op3.
        self.__op3 = op3

    def __str__(self):
        '''
        Metodo: __str__
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        str -> stringa con i tre operandi
        '''
        return f"{self.op1}, {self.op2}, {self.__op3}"

    def diff(self) -> float:
        '''
        Metodo: diff
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> differenza tra i tre operandi
        '''
        # Calcolo della differenza tra il primo, il secondo e il terzo operando.
        return self.op1 - self.op2 - self.__op3

    def prod(self) -> float:
        '''
        Metodo: prod
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> prodotto tra i tre operandi
        '''
        # Calcolo del prodotto tra il primo, il secondo e il terzo operando.
        return self.op1 * self.op2 * self.__op3

    def confr_prod(self, ogg2: "AritmeticaTre") -> bool:
        '''
        Metodo: confr_prod
        Template per costruire i metodi
        Parametri formali:
        AritmeticaTre ogg2 -> oggetto con cui confrontare il prodotto
        Valore di ritorno:
        bool -> True se il prodotto dell'oggetto chiamante è maggiore, False se non lo è
        '''
        # Confronto tra il prodotto dell'oggetto chiamante e quello dell'oggetto parametro.
        return self.prod() > ogg2.prod()

    def addiz(self) -> float:
        '''
        Metodo: addiz
        Template per costruire i metodi
        Parametri formali:
        Nessuno
        Valore di ritorno:
        float -> somma dei tre operandi
        '''
        # Calcolo della somma tra il primo, il secondo e il terzo operando.
        return self.op1 + self.op2 + self.__op3



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
ogg1 = AritmeticaDue()

ogg2 = AritmeticaDue()
ogg2.op1 = 2
ogg2.op2 = 3

print(ogg1.prod())
print(ogg1.confr_prod(ogg2))

print("-" * 30)

ogg3 = AritmeticaTre()

ogg4 = AritmeticaTre()
ogg4.op3 = 1

print(f"{ogg4.op1}, {ogg4.op2}, {ogg4.op3}")
print(ogg3.diff())
print(ogg3.addiz())
print(ogg3.confr_prod(ogg4))
