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

    def __init__(self, fixtures_path, frame_seconds, clock=time.time):
        with open(fixtures_path, encoding="utf-8") as f:
            data = json.load(f)
        self.__prestazioni = data["prestazioni"]
        self.__nre_to_code = data["nre_to_code"]
        self.__frames = data["frames"]
        self.__frame_seconds = frame_seconds
        self.__clock = clock
        self.__start = clock()

    def resolve_nre(self, nre):
        """The prestazione an NRE unlocks, or None if the NRE is unknown."""
        code = self.__nre_to_code.get(nre)
        if code is None:
            return None
        return {"code": code, "descrizione": self.__prestazioni.get(code, code)}

    def slots_for(self, code):
        """The current frame of slots for a prestazione, or None if unknown."""
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
def home():
    return "CUP finto attivo. Prova /prestazione?nre=... oppure /slots?code=..."


@app.get("/prestazione")
def prestazione():
    """Resolve an NRE to the prestazione it unlocks (used during registration)."""
    nre = request.args.get("nre", "")
    result = cup.resolve_nre(nre)
    if result is None:
        return jsonify({"error": "NRE non riconosciuto"}), 404
    return jsonify(result)


@app.get("/slots")
def slots():
    """The current slots for a prestazione (the daemon polls this)."""
    code = request.args.get("code", "")
    current = cup.slots_for(code)
    if current is None:
        return jsonify({"error": "prestazione sconosciuta"}), 404
    return jsonify({"code": code, "slots": current})


def main():
    app.run(host=CUP_HOST, port=CUP_PORT, debug=False)


if __name__ == "__main__":
    main()
