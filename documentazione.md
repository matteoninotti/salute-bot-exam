# salute-bot (versione esame) - Documentazione tecnica

**Autore:** Matteo Ninotti  
**Corso:** ITS ICT Piemonte - Python  
**Data:** 05/07/2026

## a. Oggetto

Il progetto e` un sistema di monitoraggio dei posti disponibili (slot) per le prenotazioni sanitarie tramite CUP. Un watcher controlla a intervalli regolari un sito di prenotazione e registra quando compaiono nuovi posti. L'utente si registra indicando la propria ricetta (NRE) e consulta i posti trovati da riga di comando o da interfaccia web.

## b. Scopo

Lo scopo e` automatizzare il controllo dei posti disponibili e mostrare all'utente, in modo chiaro, quelli legati alle prestazioni che segue, evidenziando i posti appena comparsi. Dal punto di vista didattico il progetto dimostra architettura client/server su HTTP, interfaccia web lato client, persistenza su database e generazione di PDF.

## c. Analisi tecnica

**Nota di sicurezza:** local demonstration only; CF-only access, no authentication.

### Architettura

Il sistema e` composto da tre programmi che condividono un database SQLite:

- **cup_server.py**: server finto CUP con Flask; risponde via HTTP e genera gli slot al volo con Faker (seed fisso).
- **daemon.py**: client che interroga il server CUP, confronta gli slot con quelli gia` noti e salva i nuovi nel database.
- **client**: **cli.py** (riga di comando) e **web.py** (interfaccia web Flask). Leggono e scrivono lo stesso database del daemon.

### Librerie usate

- **Flask**: server CUP e interfaccia web.
- **requests**: richieste HTTP dal daemon al server CUP.
- **fpdf2**: generazione del PDF dei posti e della documentazione.
- **Faker**: creazione degli slot finti in italiano, con seed fisso.
- **sqlite3**: database.
- Moduli standard: **hashlib**, **sys**, **datetime**, **os**, **pathlib**.

### Struttura del database

- **utenti**(cf)
- **prestazioni**(code, descrizione)
- **targets**(cf, code, nre)
- **slots**(code, slot_key, date, time, struttura, cap, address, first_seen, last_seen)
- **richieste**(id, cf, nre, code, descrizione, status, requested_at, resolved_at)

### Scelte principali

- **Identita` di uno slot**: SHA-256 sui campi data, ora, struttura e CAP.
- **Posti nuovi**: il daemon salva i nuovi slot e aggiorna `last_seen` per quelli gia` noti.
- **Evidenziazione dei nuovi**: uno slot e`nuovo se il suo`first_seen` e` il piu` recente della prestazione e diverso dal piu` vecchio.
- **Crescita degli slot**: il server mostra un numero crescente di slot in base al tempo trascorso dal primo controllo di quella prestazione.
- **Registrazione tramite daemon**: il client inserisce una richiesta in coda e attende che il daemon la risolva.

## d. Commenti su procedure specifiche

- **detector.detect_new_slots**: separa gli slot gia` noti da quelli nuovi.
- **store.\_mark_new**: calcola il flag `is_new`.
- **daemon.tick**: prima risolve le richieste in coda, poi controlla le prestazioni seguite.
- **cup_server.CupData.slots_for**: sceglie il frame corrente in base al tempo trascorso.
- **Incapsulamento**: le classi mantengono gli attributi privati e usano getter di sola lettura.

## e. Guida all'uso

**Installazione**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Avvio rapido**

```bash
python salutebotexam.py
```

Per l'avvio manuale:

1. `python cup_server.py`
2. `python daemon.py`
3. `python cli.py register` oppure `python web.py`

**Input attesi**

- Codice Fiscale: 16 caratteri
- NRE: 15 caratteri

NRE validi per le prove:

- `010A31234500001` - Visita urologica
- `020B45678900002` - Elettrocardiogramma

**Terminale 3 — client a riga di comando:**

```bash
python cli.py register          # nuovo utente: CF + NRE
python cli.py slots  <CF>        # posti trovati per le prestazioni seguite
python cli.py history <CF>       # cronologia delle richieste
python cli.py add               # aggiungi un'altra prestazione (CF + NRE)
```

**Output**

- elenco dei posti disponibili per le prestazioni seguite
- cronologia delle richieste
- report PDF scaricabile dei posti

## f. Conclusioni

Il progetto realizza gli obiettivi richiesti: client e server, interfaccia a riga di comando, interfaccia web lato client, report PDF e database con cronologia delle richieste. La separazione dei ruoli rende il sistema facile da spiegare e da estendere.
