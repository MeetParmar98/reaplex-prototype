Reaplex Prototype
=================

Lightweight prototype of Reaplex — a Google scraper with multi-layer anti-bot evasion.

Quickstart
----------

Prerequisites
- Python 3.10+
- Chrome browser (required by `nodriver` browser layer)

Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Optional (recommended) parser for faster HTML parsing:

```powershell
python -m pip install lxml
```

Run the CLI

From the project root run:

```powershell
python src/search/cli.py search "coffee shops nyc"
```

This will start the stealth layers, launch a nodriver browser session, fetch the SERP HTML, and write SerpAPI-compatible JSON results.

Files
- `requirements.txt`: Inferred third-party deps (curl-cffi, beautifulsoup4, nodriver, typer, rich)
- `src/`: Source code

Notes
- If you want pinned versions, create a lock by running `pip freeze > requirements.txt` and commit the result.
- On Windows, ensure Chrome is installed and accessible for `nodriver` to drive a browser session.

License
- No license included — treat this as prototype code.
