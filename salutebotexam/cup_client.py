"""The HTTP client the daemon uses to talk to the CUP server.

A thin wrapper over ``requests`` that turns JSON responses into our model
objects. The daemon is the only part of the app that uses this.
"""

import requests

from config import CUP_URL
from models import Prestazione, Slot


class CupError(Exception):
    """The CUP server could not be reached or returned an unexpected status."""


class CupClient:
    """Talks to the mock CUP server. The base URL is private (encapsulation)."""

    def __init__(self, base_url: str = CUP_URL) -> None:
        """Build the client.

        Args:
            base_url: the CUP server base URL (defaults to config.CUP_URL).
        """
        self.__base_url = base_url

    def resolve_prestazione(self, nre: str) -> Prestazione | None:
        """Ask the server which prestazione an NRE unlocks.

        Args:
            nre: the prescription number.
        Returns:
            A Prestazione, or None if the NRE is unknown (server replied 404).
        Raises:
            CupError: if the server is unreachable or misbehaves.
        """
        data = self.__get("/prestazione", {"nre": nre}, allow_404=True)
        prestazione = None
        if data is not None:
            prestazione = Prestazione(data["code"], data["descrizione"])
        return prestazione

    def fetch_slots(self, code: str) -> list[Slot]:
        """Fetch the current slots for a prestazione.

        Args:
            code: the prestazione code.
        Returns:
            The current slots as a list of Slot objects.
        Raises:
            CupError: if the server is unreachable or the code is unknown.
        """
        data = self.__get("/slots", {"code": code})
        return [Slot.from_dict(s) for s in data["slots"]]

    def __get(self, path: str, params: dict, allow_404: bool = False) -> dict | None:
        """Run a GET and return the parsed JSON.

        Args:
            path: URL path (e.g. "/slots").
            params: query-string parameters.
            allow_404: if True, a 404 returns None instead of raising.
        Returns:
            The parsed JSON dict, or None on an allowed 404.
        Raises:
            CupError: on a transport error or an unexpected status code.
        """
        try:
            response = requests.get(self.__base_url + path, params=params, timeout=10)
        except requests.RequestException as err:
            raise CupError(f"CUP non raggiungibile: {err}")
        if response.status_code == 404 and allow_404:
            data = None
        elif response.status_code != 200:
            raise CupError(f"stato inatteso dal CUP: {response.status_code}")
        else:
            data = response.json()
        return data
