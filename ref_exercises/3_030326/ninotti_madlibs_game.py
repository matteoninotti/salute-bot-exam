print("Benvenuto a Mad Libs!\n")

# Raccogli le parole dall'utente
nome = input("Inserisci un nome: ")
aggettivo1 = input("Inserisci un aggettivo: ")
aggettivo2 = input("Inserisci un altro aggettivo: ")
animale = input("Inserisci un animale: ")
cibo = input("Inserisci un cibo: ")
azione1 = input("Inserisci un'azione (verbo all'infinito): ")
azione2 = input("Inserisci un'altra azione (verbo all'infinito): ")
utensile = input("Inserisci un utensile o oggetto: ")

# Crea la storia inserendo le parole nei segnaposti
storia = f"""
C'era una volta {nome}, un avventuriero molto {aggettivo1}.
Un giorno, mentre esplorava una caverna oscura, incontrò un {animale} gigante stranamente {aggettivo2}.

Invece di attaccare, la creatura chiese educatamente del {cibo}.
Dopo aver mangiato, {nome} e la creatura decisero di {azione1} per festeggiare.

Ma improvvisamente dovettero scappare e usare un {utensile} portatile per riuscire a {azione2} sani e salvi.
Che giornata pazzesca!
"""

# Stampa la storia finale
print("\n--- LA TUA STORIA MAD LIBS ---")
print(storia)
print("------------------------------")

