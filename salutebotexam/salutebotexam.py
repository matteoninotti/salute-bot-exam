"""Avvio unico dell'applicazione.

Lancia in background i tre programmi (server CUP, daemon, client web) con un
solo comando, cosi' non servono tre terminali. I log finiscono in ``logs/`` e i
PID vengono salvati per poterli fermare.

Uso:
    python salutebotexam.py           # avvia tutto in background
    python salutebotexam.py stop      # ferma i processi avviati
    python salutebotexam.py status    # mostra lo stato dei processi

Il client a riga di comando (cli.py) resta separato: dopo l'avvio, usa
``python cli.py register`` / ``slots`` / ``history`` in un altro terminale, oppure
apri l'interfaccia web.
"""

import json
import os
import signal
import socket
import subprocess
import sys
import time

from config import CUP_HOST, CUP_PORT, WEB_PORT

_BASE = os.path.dirname(os.path.abspath(__file__))
_LOG_DIR = os.path.join(_BASE, "logs")
_PID_FILE = os.path.join(_LOG_DIR, "pids.json")
# nome logico -> script da eseguire, nell'ordine di avvio (il server CUP per primo)
_SERVICES = [("cup_server", "cup_server.py"), ("daemon", "daemon.py"), ("web", "web.py")]


class Launcher:
    """Avvia/ferma i tre processi dell'app. Stato privato (incapsulamento)."""

    def __init__(self) -> None:
        """Prepara il launcher (crea la cartella dei log se manca)."""
        self.__base = _BASE
        os.makedirs(_LOG_DIR, exist_ok=True)

    def start(self) -> None:
        """Avvia server CUP, daemon e web in background e salva i PID."""
        if self.__running():
            print("Sembra gia' in esecuzione. Ferma prima con: python salutebotexam.py stop")
            return
        pids: dict[str, int] = {}
        for name, script in _SERVICES:
            pids[name] = self.__spawn(script)
            if name == "cup_server" and not self.__wait_port(CUP_HOST, CUP_PORT):
                print("Attenzione: il server CUP non risponde. Controlla logs/cup_server.log")
        with open(_PID_FILE, "w", encoding="utf-8") as f:
            json.dump(pids, f)
        self.__wait_port(CUP_HOST, WEB_PORT)
        print("Avviato in background:")
        print(f"  server CUP  ->  http://{CUP_HOST}:{CUP_PORT}")
        print("  daemon      ->  watcher attivo")
        print(f"  web         ->  http://{CUP_HOST}:{WEB_PORT}")
        print(f"Log in {_LOG_DIR}/ . Per fermare: python salutebotexam.py stop")

    def stop(self) -> None:
        """Ferma i processi elencati nel file dei PID."""
        pids = self.__read_pids()
        if not pids:
            print("Nessun processo registrato.")
            return
        for name, pid in pids.items():
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"fermato {name} (pid {pid})")
            except ProcessLookupError:
                print(f"{name} (pid {pid}) era gia' fermo")
        os.remove(_PID_FILE)

    def status(self) -> None:
        """Stampa quali processi sono attivi."""
        pids = self.__read_pids()
        if not pids:
            print("Non in esecuzione.")
            return
        for name, pid in pids.items():
            stato = "attivo" if self.__alive(pid) else "fermo"
            print(f"  {name}: {stato} (pid {pid})")

    # ----- helper privati -----

    def __spawn(self, script: str) -> int:
        """Avvia uno script in una sessione separata; restituisce il suo PID.

        Args:
            script: nome del file da eseguire (es. "cup_server.py").
        Returns:
            Il PID del processo avviato.
        """
        log_path = os.path.join(_LOG_DIR, script.replace(".py", ".log"))
        log = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, script], cwd=self.__base,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
        )
        return proc.pid

    def __wait_port(self, host: str, port: int, tries: int = 50) -> bool:
        """Attende che una porta accetti connessioni.

        Args:
            host: host da contattare.
            port: porta da contattare.
            tries: numero massimo di tentativi (0.2s l'uno).
        Returns:
            True se la porta risponde entro il tempo previsto, False altrimenti.
        """
        for _ in range(tries):
            sock = socket.socket()
            try:
                sock.connect((host, port))
                sock.close()
                return True
            except OSError:
                time.sleep(0.2)
        return False

    def __read_pids(self) -> dict[str, int]:
        """Legge il file dei PID; restituisce un dict vuoto se non esiste."""
        if not os.path.exists(_PID_FILE):
            return {}
        with open(_PID_FILE, encoding="utf-8") as f:
            return json.load(f)

    def __running(self) -> bool:
        """True se almeno uno dei processi registrati e' ancora attivo."""
        return any(self.__alive(pid) for pid in self.__read_pids().values())

    def __alive(self, pid: int) -> bool:
        """True se esiste un processo con questo PID."""
        try:
            os.kill(pid, 0)  # segnale 0 = solo verifica di esistenza
            return True
        except OSError:
            return False


def main() -> None:
    """Legge il comando (start/stop/status) ed esegue l'azione."""
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    launcher = Launcher()
    if command == "start":
        launcher.start()
    elif command == "stop":
        launcher.stop()
    elif command == "status":
        launcher.status()
    else:
        print("Comandi disponibili: start | stop | status")


if __name__ == "__main__":
    main()
