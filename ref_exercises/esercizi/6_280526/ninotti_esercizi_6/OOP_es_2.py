'''
Autore: Matteo Ninotti
Data: 25/05/2026
Titolo: 'Creare una classe Rettangolo con attributi base e altezza. Costruire tutti i metodi setter e getter per gli attributi. Aggiungere i metodi per il calcolo dell'area e del perimetro.
Implementare un metodo di nome: “contiene” che ha come parametro un oggetto
rettangolo. Tale metodo deve restituire true se il rettangolo oggetto chiamante contiene il rettangolo oggetto parametro, false se non lo contiene. Un rettangolo “contiene” un altro quando la sua altezza e la sua base sono maggiori rispettivamente della base e dell'altezza del secondo rettangolo.'
'''
##
## Classi:
##
class Rettangolo:
  '''
  Classe: Rettangolo
  Template per costruire le classi
  Attributi:
  float __base -> base privata del rettangolo
  float __altezza -> altezza privata del rettangolo
  '''
  def __init__(self, base: float, altezza: float) -> None:
    '''
    Metodo: __init__
    Template per costruire i metodi
    Parametri formali:
    float base -> base da assegnare al rettangolo
    float altezza -> altezza da assegnare al rettangolo
    Valore di ritorno:
    None -> il metodo inizializza l'oggetto
    '''
    # Inizializzazione degli attributi privati dell'oggetto.
    self.__base = base
    self.__altezza = altezza
  
  @property
  def base(self):
    '''
    Metodo: base
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    float -> base privata del rettangolo
    '''
    return self.__base

  @base.setter
  def base(self, base:int) -> None:
    '''
    Metodo: base
    Template per costruire i metodi
    Parametri formali:
    int base -> nuova base del rettangolo
    Valore di ritorno:
    None -> il metodo modifica la base privata del rettangolo
    '''
    # Aggiornamento dell'attributo privato __base.
    self.__base = base
    
  @property
  def altezza(self) -> float:
    '''
    Metodo: altezza
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    float -> altezza privata del rettangolo
    '''
    return self.__altezza
  
  @altezza.setter
  def altezza(self, altezza:float) -> None:
    '''
    Metodo: altezza
    Template per costruire i metodi
    Parametri formali:
    float altezza -> nuova altezza del rettangolo
    Valore di ritorno:
    None -> il metodo modifica l'altezza privata del rettangolo
    '''
    # Aggiornamento dell'attributo privato __altezza.
    self.__altezza = altezza
    
  def calc_perim(self) -> float:
    '''
    Metodo: calc_perim
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    float -> perimetro del rettangolo
    '''
    return 2*(self.__altezza + self.__base)
  
  def calc_area(self) -> float:
    '''
    Metodo: calc_area
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    float -> area del rettangolo
    '''
    return self.__base * self.__altezza
  
  def contiene(self, rett2: 'Rettangolo') -> bool:
    '''
    Metodo: contiene
    Template per costruire i metodi
    Parametri formali:
    Rettangolo rett2 -> rettangolo da confrontare con l'oggetto chiamante
    Valore di ritorno:
    bool -> True se l'oggetto chiamante contiene rett2, False se non lo contiene
    '''
    # Controllo che base e altezza siano maggiori di quelle del secondo rettangolo.
    return self.__base > rett2.base and self.__altezza > rett2.altezza
    
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
rett1 = Rettangolo(2,3)
rett2 = Rettangolo(1,1)

print(rett1.calc_area())
print(rett1.calc_perim())
print(rett1.contiene(rett2))
