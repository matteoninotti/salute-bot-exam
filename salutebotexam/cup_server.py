"""The mock CUP server: the "server" half of the client/server pair.

It stands in for the real Piemonte CUP website. It answers two HTTP requests:
what prestazione an NRE unlocks, and what slots a prestazione currently has.
The slot list grows over wall-clock time (scripted frames) so the daemon can
observe a new slot appearing.

Run:  python cup_server.py
"""

import json
import time

from flask import Flask, jsonify, request

from config import CUP_HOST, CUP_PORT, FIXTURES_PATH, FRAME_SECONDS


class CupData:
    """Holds the canned data and decides which slot frame is 'current'.

    All state is private. The current frame is chosen from the wall clock:
    frames advance every ``frame_seconds`` since the object was created, and the
    last frame is sticky. ``clock`` is injectable so the logic is testable
    without really waiting.
    """

    def __init__(self, fixtures_path: str, frame_seconds: float,
                 clock=time.time) -> None:
        """Load the fixture data and record the start time.

        Args:
            fixtures_path: path to the JSON fixtures file.
            frame_seconds: how long each slot frame lasts before advancing.
            clock: a callable returning the current time in seconds (injectable
                for tests).
        """
        with open(fixtures_path, encoding="utf-8") as f:
            data = json.load(f)
        self.__prestazioni = data["prestazioni"]
        self.__nre_to_code = data["nre_to_code"]
        self.__frames = data["frames"]
        self.__frame_seconds = frame_seconds
        self.__clock = clock
        self.__start = clock()

    def resolve_nre(self, nre: str) -> dict | None:
        """Resolve an NRE to the prestazione it unlocks.

        Args:
            nre: the prescription number.
        Returns:
            A dict {code, descrizione}, or None if the NRE is unknown.
        """
        code = self.__nre_to_code.get(nre)
        if code is None:
            return None
        return {"code": code, "descrizione": self.__prestazioni.get(code, code)}

    def slots_for(self, code: str) -> list | None:
        """Return the current frame of slots for a prestazione.

        Args:
            code: the prestazione code.
        Returns:
            The list of slot dicts for the frame selected by elapsed wall-clock
            time (last frame is sticky), or None if the code is unknown.
        """
        frames = self.__frames.get(code)
        if frames is None:
            return None
        elapsed = self.__clock() - self.__start
        index = int(elapsed // self.__frame_seconds)
        if index > len(frames) - 1:
            index = len(frames) - 1
        return frames[index]


app = Flask(__name__)
cup = CupData(FIXTURES_PATH, FRAME_SECONDS)


@app.get("/")
def home() -> str:
    """Return a short banner so the server is easy to check in a browser."""
    return "CUP finto attivo. Prova /prestazione?nre=... oppure /slots?code=..."


@app.get("/prestazione")
def prestazione():
    """Resolve an NRE to the prestazione it unlocks (used during registration).

    Query params:
        nre: the prescription number.
    Returns:
        JSON {code, descrizione} with status 200, or {error} with status 404.
    """
    nre = request.args.get("nre", "")
    result = cup.resolve_nre(nre)
    if result is None:
        return jsonify({"error": "NRE non riconosciuto"}), 404
    return jsonify(result)


@app.get("/slots")
def slots():
    """Return the current slots for a prestazione (the daemon polls this).

    Query params:
        code: the prestazione code.
    Returns:
        JSON {code, slots} with status 200, or {error} with status 404.
    """
    code = request.args.get("code", "")
    current = cup.slots_for(code)
    if current is None:
        return jsonify({"error": "prestazione sconosciuta"}), 404
    return jsonify({"code": code, "slots": current})


def main() -> None:
    """Start the Flask development server."""
    app.run(host=CUP_HOST, port=CUP_PORT, debug=False)


if __name__ == "__main__":
    main()
