'''
Autore: Matteo Ninotti
Data: 25/05/2026
Titolo: 'Creare una classe Insegnante con attributi nome, età e stipendio, dove stipendio deve
essere un attributo privato.
Costruire tutti i metodi getter e setter per gli attributi (anche per quelli pubblici)
Effettuare l'overriding del metodo __str__ in maniera tale che restituisca gli attributi nome e età.
Provare la classe istanziando almeno due oggetti.'
'''
##
## Classi:
##
class Insegnante(object):
  '''
  Classe: Insegnante
  Template per costruire le classi
  Attributi:
  str nome -> nome dell'insegnante
  int eta -> età dell'insegnante
  float __stipendio -> stipendio privato dell'insegnante
  '''
  def __init__(self, nome:str, eta:int, stipendio:float):
    '''
    Metodo: __init__
    Template per costruire i metodi
    Parametri formali:
    str nome -> nome da assegnare all'insegnante
    int eta -> età da assegnare all'insegnante
    float stipendio -> stipendio da assegnare all'insegnante
    Valore di ritorno:
    None -> il metodo inizializza l'oggetto
    '''
    # Inizializzazione degli attributi dell'oggetto.
    self.nome = nome
    self.eta = eta
    self.__stipendio = stipendio
  
  def get_nome(self) -> str:
    '''
    Metodo: get_nome
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    str -> nome dell'insegnante
    '''
    return self.nome

  def get_eta(self) -> int:
    '''
    Metodo: get_eta
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    int -> età dell'insegnante
    '''
    return self.eta
  
  @property
  def stipendio(self) -> float:
    '''
    Metodo: stipendio
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    float -> stipendio privato dell'insegnante
    '''
    return self.__stipendio
  
  def set_nome(self, nome: str):
    '''
    Metodo: set_nome
    Template per costruire i metodi
    Parametri formali:
    str nome -> nuovo nome dell'insegnante
    Valore di ritorno:
    None -> il metodo modifica il nome dell'insegnante
    '''
    # Aggiornamento dell'attributo pubblico nome.
    self.nome = nome
    
  def set_eta(self) -> int:
    '''
    Metodo: set_eta
    Template per costruire i metodi
    Parametri formali:
    Nessuno
    Valore di ritorno:
    int -> età dell'insegnante
    '''
    return self.eta
  
  @stipendio.setter
  def stipendio(self, stipendio: float) -> None:
    '''
    Metodo: stipendio
    Template per costruire i metodi
    Parametri formali:
    float stipendio -> nuovo stipendio dell'insegnante
    Valore di ritorno:
    None -> il metodo modifica lo stipendio privato dell'insegnante
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
    str -> stringa con nome ed età dell'insegnante
    '''
    return f"nome: {self.nome} | età: {self.eta}"

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

ins1 = Insegnante("luisa baldi", 45, 2000)
print(ins1)
print(ins1.stipendio)
print(ins1.eta)
ins1.stipendio = 4900
print(ins1.stipendio)
