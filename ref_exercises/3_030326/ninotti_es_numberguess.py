from random import randint as rnd

def main():
  random_number = gen_random_number()
  number = ask_number()
  attempts = 0
  while not compare_number(number, random_number) and attempts < 6:
    number = ask_number()
    attempts += 1
  game_end(attempts) # if attempts > 7 --> player loses

def gen_random_number():
  return rnd(1, 100)

def ask_number():
  number = int(input("inserisci un numero, 0 per uscire: "))
  if number == 0:
    exit()
  return number

def compare_number(number, random_number):
  if number == random_number:
    return True
  else:
    if number < random_number:
      print("troppo basso")
    else:
      print("troppo alto")
    return False

def game_end(attempts):
  if attempts < 6:
    print("hai indovinato")
  else: print ("hai perso")
  restart = input("premi 1 per ricominciare, tasto qualsiasi per uscire: ")
  if restart == "1":
    main()
  else: exit

if __name__ == "__main__":
  main()