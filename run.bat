@echo off
python --version 3 > NUL
if not errorlevel 0 (
    echo Python ist nicht installiert. Bitte lade dir Python von https://python.org herunter.
    pause
)
if not exist .venv\ (
    python -m venv .venv
)
call .venv\Scripts\activate.bat && (
    pip install -r requirements.txt --quiet
) && (
    python src/scraper.py
)


pause