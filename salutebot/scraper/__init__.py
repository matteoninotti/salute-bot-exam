"""Scraper package.

Split at the `parse | drive` seam (build strategy D):
    - parser.py -- pure, deterministic markup -> [Slot]; tested offline against
      the real recon capture (the trustworthy half).
    - drive (Playwright JSF navigation) -- added later; the only live-dependent
      half, validated by a local smoke run against the CUP site.
"""
