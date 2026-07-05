"""Shared paths and settings (like state.py in the pipeline project).

Everything that more than one module needs to agree on lives here: the database
file, the fixtures file, the mock CUP address, and the daemon poll interval.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Database and data files
DB_PATH = str(BASE_DIR / "salutebot.db")
FIXTURES_PATH = str(BASE_DIR / "data" / "fixtures.json")
REPORT_DIR = str(BASE_DIR / "report")

# Mock CUP server (the "server" half: serves the slots over HTTP).
# Port 5050, not 5000: on macOS port 5000 is taken by ControlCenter (AirPlay
# Receiver), which would answer requests instead of our server.
CUP_HOST = "127.0.0.1"
CUP_PORT = 5050
CUP_URL = f"http://{CUP_HOST}:{CUP_PORT}"

# How many seconds each scripted slot "frame" lasts before the CUP server moves
# to the next one. Growth is on the wall clock, so new slots appear on schedule
# no matter how often the daemon polls.
FRAME_SECONDS = 20

# Web GUI client
WEB_PORT = 5001

# Daemon: seconds to wait between one sweep and the next
POLL_INTERVAL = 8
