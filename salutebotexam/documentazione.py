"""Generatore della documentazione tecnica in PDF (deliverable d'esame).

Produce ``documentazione.pdf`` a partire dal contenuto HTML qui sotto, usando
la libreria fpdf2 (la stessa del report degli slot). Esegui:

    python documentazione.py
"""

import os
from datetime import datetime

from fpdf import FPDF

from config import BASE_DIR

_OGGI = datetime.now().strftime("%d/%m/%Y")

# Contenuto della documentazione, in HTML (fpdf2 sa renderizzare i tag di base).
_HTML = f"""
<h1>salute-bot (versione esame) - Documentazione tecnica</h1>
<p><b>Autore:</b> Matteo Ninotti<br>
<b>Corso:</b> ITS ICT Piemonte - Python<br>
<b>Data:</b> {_OGGI}</p>

<h2>a. Oggetto</h2>
<p>Il progetto &egrave; un sistema di monitoraggio dei posti disponibili (slot)
per le prenotazioni sanitarie tramite CUP. Un componente "watcher" controlla a
intervalli regolari un sito di prenotazione e registra quando compaiono nuovi
posti; l'utente si registra indicando la propria ricetta (NRE) e consulta i posti
trovati da riga di comando o da interfaccia web, con la possibilit&agrave; di
esportarli in PDF.</p>
<p>&Egrave; una versione semplificata di un progetto pi&ugrave; ampio: il sito CUP
reale &egrave; sostituito da un server finto e non vengono inviate email.</p>

<h2>b. Scopo</h2>
<p>Prenotare una visita tramite CUP &egrave; difficile quando non ci sono posti:
bisogna ricontrollare il portale di continuo. Lo scopo del programma &egrave;
automatizzare questo controllo e mostrare all'utente, in un colpo d'occhio, i
posti disponibili per le prestazioni che segue, evidenziando quelli appena
comparsi. Sul piano didattico il progetto dimostra: architettura client/server su
HTTP, un'interfaccia grafica lato client, la persistenza su database e la
generazione di documenti PDF.</p>

<h2>c. Analisi tecnica</h2>

<h3>Architettura</h3>
<p>Il sistema &egrave; composto da tre programmi che condividono un unico database
SQLite:</p>
<ul>
<li><b>cup_server.py</b> (server): un finto sito CUP realizzato con Flask, che
risponde via HTTP e restituisce gli slot leggendoli da un file di dati. Gli slot
crescono nel tempo (a "frame"), cos&igrave; il watcher pu&ograve; osservare la
comparsa di un posto nuovo.</li>
<li><b>daemon.py</b> (client): interroga periodicamente il server CUP, confronta
gli slot con quelli gi&agrave; noti e salva i nuovi nel database. &Egrave; l'unico
programma che comunica col server CUP.</li>
<li><b>client</b> (interfaccia utente): <b>cli.py</b> (riga di comando) e
<b>web.py</b> (interfaccia web Flask). Leggono e scrivono lo stesso database del
daemon, senza dialogare direttamente con lui.</li>
</ul>
<p>La comunicazione HTTP tra daemon e server CUP realizza il requisito
"client/server"; il coordinamento tra client e daemon avviene solo tramite il
file di database condiviso (nessuna gestione client/server "vera" tra i due).</p>

<h3>Librerie utilizzate</h3>
<ul>
<li><b>Flask</b> - per il server CUP e per l'interfaccia web del client
(rotte HTTP e template HTML).</li>
<li><b>requests</b> - usata dal daemon per interrogare il server CUP via
HTTP.</li>
<li><b>fpdf2</b> - per generare il PDF dei posti e questa documentazione.</li>
<li><b>sqlite3</b> (libreria standard) - per il database.</li>
<li>Altri moduli standard: <b>hashlib</b> (chiave degli slot), <b>argparse</b>
(comandi CLI), <b>datetime</b>, <b>os</b>, <b>pathlib</b>.</li>
</ul>

<h3>Struttura del database</h3>
<ul>
<li><b>utenti</b>(cf, email)</li>
<li><b>prestazioni</b>(code, descrizione)</li>
<li><b>targets</b>(cf, code, nre) - l'iscrizione di un utente a una
prestazione</li>
<li><b>slots</b>(code, slot_key, date, time, struttura, cap, address, first_seen,
last_seen) - i posti trovati, condivisi per prestazione</li>
<li><b>richieste</b>(id, cf, email, nre, code, descrizione, status, requested_at,
resolved_at) - coda delle registrazioni <i>e</i> cronologia per utente</li>
</ul>

<h3>Algoritmi e scelte principali</h3>
<ul>
<li><b>Identit&agrave; di uno slot (chiave naturale).</b> Il CUP non fornisce un
id stabile per lo slot, quindi ne calcoliamo uno con SHA-256 a partire dai campi
identificativi (data, ora, struttura, CAP). Cos&igrave; lo stesso posto viene
riconosciuto da un controllo all'altro. L'indirizzo &egrave; escluso dalla chiave
perch&eacute; puramente descrittivo.</li>
<li><b>Rilevamento dei posti nuovi.</b> A ogni controllo il daemon confronta gli
slot ricevuti con le chiavi gi&agrave; salvate: quelli gi&agrave; noti aggiornano
il campo last_seen, quelli nuovi vengono inseriti con first_seen = adesso.</li>
<li><b>Evidenziazione dei "nuovi".</b> Uno slot &egrave; mostrato come NUOVO se il
suo first_seen &egrave; il pi&ugrave; recente della prestazione <i>ed</i> &egrave;
diverso dal pi&ugrave; vecchio: cos&igrave; l'insieme iniziale (tutti con lo stesso
istante) non viene evidenziato, mentre un posto comparso dopo s&igrave;.</li>
<li><b>Crescita degli slot sull'orologio.</b> Il server CUP sceglie il "frame" di
slot in base al tempo trascorso dal proprio avvio (frame = tempo // FRAME_SECONDS),
non al numero di richieste: la crescita &egrave; quindi deterministica e
indipendente dalla frequenza di controllo.</li>
<li><b>Registrazione tramite il daemon.</b> Il client non contatta mai il server
CUP: inserisce una richiesta "pending" nella tabella richieste e attende. Il
daemon la prende in carico, risolve l'NRE sul server CUP, crea utente e iscrizione,
registra come "gi&agrave; visti" gli slot correnti (baseline) e segna l'esito
(ok/invalid). La stessa tabella richieste funge da cronologia personale.</li>
</ul>

<h2>d. Commenti su procedure specifiche</h2>
<ul>
<li><b>detector.detect_new_slots</b> - separa gli slot ricevuti in "gi&agrave;
noti" (aggiorna last_seen) e "nuovi" (restituiti al daemon, che li salva insieme
con lo stesso istante).</li>
<li><b>store._mark_new</b> - calcola il flag is_new confrontando i first_seen
della prestazione, secondo la regola descritta sopra.</li>
<li><b>daemon.tick</b> - un ciclo completo: prima risolve le richieste di
registrazione in coda, poi controlla ogni prestazione seguita.</li>
<li><b>cup_server.CupData.slots_for</b> - sceglie il frame corrente in base
al tempo trascorso; l'ultimo frame resta fisso.</li>
<li><b>Incapsulamento</b> - le classi (Slot, Prestazione, Store, CupData,
CupClient, Daemon, SlotReport, CLI) tengono gli attributi privati (name mangling
<code>__attr</code>) ed espongono getter di sola lettura, come richiesto.</li>
</ul>

<h2>e. Guida all'uso (input / output)</h2>
<p><b>Installazione:</b> creare un ambiente virtuale e installare le dipendenze:
<code>python3 -m venv .venv</code>, <code>source .venv/bin/activate</code>,
<code>pip install -r requirements.txt</code>.</p>
<p><b>Avvio</b> (tre terminali): 1) <code>python cup_server.py</code>;
2) <code>python daemon.py</code>; 3) il client, a scelta:
<code>python cli.py register</code> oppure <code>python web.py</code>
(poi aprire http://127.0.0.1:5001).</p>
<p><b>Input attesi:</b> Codice Fiscale (16 caratteri), email, NRE (15 caratteri).
Per le prove sono validi gli NRE <code>010A31234500001</code> (Visita urologica) e
<code>020B45678900002</code> (Elettrocardiogramma); ogni altro NRE viene rifiutato.</p>
<p><b>Output:</b> l'elenco dei posti disponibili per le prestazioni seguite, con i
nuovi evidenziati; la cronologia delle richieste; un report PDF scaricabile dei
posti.</p>

<h2>f. Conclusioni</h2>
<p>Il progetto realizza tutti gli obiettivi richiesti: presenza di client e server
con interfaccia a riga di comando, interfaccia grafica web lato client, stampa PDF
dei report, database lato server con cronologia delle richieste per utente. La
struttura a tre componenti tiene separate le responsabilit&agrave; (chi fornisce i
dati, chi li raccoglie, chi li mostra) e rende il sistema facile da spiegare e da
estendere. Possibili sviluppi futuri: notifiche reali (email), scraping del sito
CUP effettivo, autenticazione degli utenti.</p>
"""


def build(out_path: str | None = None) -> str:
    """Genera il PDF della documentazione tecnica.

    Args:
        out_path: percorso del PDF da creare; se None usa
            ``documentazione.pdf`` nella cartella del progetto.
    Returns:
        Il percorso del file PDF creato.
    """
    if out_path is None:
        out_path = os.path.join(str(BASE_DIR), "documentazione.pdf")
    pdf = FPDF()
    pdf.set_title("salute-bot (versione esame) - Documentazione tecnica")
    pdf.add_page()
    pdf.write_html(_HTML)
    pdf.output(out_path)
    return out_path


def main() -> None:
    """Crea documentazione.pdf e stampa il percorso."""
    path = build()
    print(f"Documentazione creata: {path}")


if __name__ == "__main__":
    main()
