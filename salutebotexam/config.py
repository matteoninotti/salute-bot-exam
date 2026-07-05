"""Shared paths and settings (like state.py in the pipeline project).

Everything that more than one module needs to agree on lives here: the database
file, the mock CUP address, and the daemon poll interval.

Most values can be overridden with an environment variable, which is handy for
testing and for a faster demo (e.g. a shorter FRAME_SECONDS).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Database and output files
DB_PATH = os.environ.get("SALUTEBOT_DB", str(BASE_DIR / "salutebot.db"))
REPORT_DIR = str(BASE_DIR / "report")

# Mock CUP server (the "server" half: serves the slots over HTTP).
# Port 5050, not 5000: on macOS port 5000 is taken by ControlCenter (AirPlay
# Receiver), which would answer requests instead of our server.
CUP_HOST = "127.0.0.1"
CUP_PORT = int(os.environ.get("SALUTEBOT_CUP_PORT", "5050"))
CUP_URL = f"http://{CUP_HOST}:{CUP_PORT}"

# Web GUI client
WEB_PORT = int(os.environ.get("SALUTEBOT_WEB_PORT", "5001"))

# Seconds between one generated slot and the next on the CUP server, counted from
# a prestazione's first request. A new slot appears about FRAME_SECONDS after
# watching starts; each slot then expires 60s after creation. Lower it for a
# quicker demo.
FRAME_SECONDS = float(os.environ.get("SALUTEBOT_FRAME_SECONDS", "10"))

# Seconds the daemon waits between one sweep and the next.
POLL_INTERVAL = float(os.environ.get("SALUTEBOT_POLL_INTERVAL", "8"))
