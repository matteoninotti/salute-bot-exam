# salute-bot (versione esame)

Sistema di monitoraggio dei posti disponibili per le prenotazioni sanitarie (CUP).
Un **watcher** controlla periodicamente un sito di prenotazione e registra quando
compaiono nuovi posti (slot). L'utente si registra, indica la ricetta (NRE) da
seguire e consulta i posti trovati da riga di comando o da interfaccia web.

Versione semplificata realizzata per l'esame di Python (nessuna email, nessuno
scraping reale: il sito CUP è simulato).

## Architettura

Tre programmi che condividono un unico database SQLite:

1. **`cup_server.py`** — il *server*: un finto sito CUP (Flask) che risponde via
   HTTP e restituisce gli slot da un file di dati; gli slot **crescono nel tempo**
   così il watcher può vedere comparire un posto nuovo.
2. **`daemon.py`** — il *client*: interroga a intervalli regolari il server CUP,
   confronta gli slot con quelli già noti e salva i nuovi nel database. È l'unico
   programma che parla col server CUP.
3. **client** — l'interfaccia utente, che legge/scrive lo stesso database:
   - **`cli.py`** — client a riga di comando;
   - **`web.py`** — client web (Flask + HTML).

```
 cup_server.py  <--- HTTP --->  daemon.py  ---> [ SQLite ] <--- cli.py / web.py
    (server)                     (client)                        (interfaccia)
```

## Requisiti

- Python 3.10 o superiore (sviluppato su 3.14), su GNU/Linux.
- Le librerie in `requirements.txt`: Flask, requests, fpdf2.

## Installazione

```bash
cd salutebotexam
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Avvio (tre terminali)

Con l'ambiente virtuale attivo in ognuno:

**Terminale 1 — server CUP finto:**
```bash
python cup_server.py
```

**Terminale 2 — watcher (daemon):**
```bash
python daemon.py
```

**Terminale 3 — client a riga di comando:**
```bash
python cli.py register          # nuovo utente: CF + email + NRE
python cli.py slots  <CF>        # posti trovati per le prestazioni seguite
python cli.py history <CF>       # cronologia delle richieste
python cli.py add               # aggiungi un'altra prestazione (CF + NRE)
```

**oppure — client web:**
```bash
python web.py                   # poi apri http://127.0.0.1:5001
```

## Dati di prova

Nel file `data/fixtures.json` sono definite due ricette valide:

| NRE               | Prestazione                       |
|-------------------|-----------------------------------|
| `010A31234500001` | VISITA UROLOGICA DI CONTROLLO     |
| `020B45678900002` | ELETTROCARDIOGRAMMA               |

Codice Fiscale di esempio (formalmente valido): `RSSMRA85T10A562S`.
Qualsiasi altro NRE viene rifiutato come "non valido".

## Variabili d'ambiente (opzionali)

| Variabile                  | Default | Uso |
|----------------------------|---------|-----|
| `SALUTEBOT_DB`             | `salutebot.db` | percorso del database |
| `SALUTEBOT_FRAME_SECONDS`  | `10`    | secondi tra un "frame" di slot e il successivo, contati dal primo controllo della prestazione (abbassalo per una demo più rapida) |
| `SALUTEBOT_POLL_INTERVAL`  | `8`     | secondi tra un controllo del daemon e il successivo |
| `SALUTEBOT_CUP_PORT`       | `5050`  | porta del server CUP |
| `SALUTEBOT_WEB_PORT`       | `5001`  | porta del client web |

Esempio di demo veloce (nuovo posto in pochi secondi):
```bash
export SALUTEBOT_FRAME_SECONDS=3 SALUTEBOT_POLL_INTERVAL=1
```

## Struttura del progetto

```
salutebotexam/
├── config.py          impostazioni condivise (percorsi, porte, intervalli)
├── database.py        connessione SQLite + schema
├── models.py          classi Slot e Prestazione
├── store.py           tutte le query (classe Store)
├── cup_server.py      server: finto sito CUP (Flask)
├── cup_client.py      client HTTP verso il server CUP
├── detector.py        confronto slot nuovi / già visti
├── daemon.py          watcher (ciclo di controllo)
├── cli.py             client a riga di comando
├── web.py             client web (Flask)
├── report.py          generazione PDF dei posti
├── validation.py      controlli di formato (CF, NRE, email)
├── data/fixtures.json dati finti degli slot
├── templates/         pagine HTML del client web
└── static/style.css   stile del client web
```

## Nota (macOS)

Il server CUP usa la porta **5050** e non la 5000, perché su macOS la 5000 è
occupata da ControlCenter (Ricevitore AirPlay). Su GNU/Linux non fa differenza.
