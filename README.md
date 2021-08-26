# IServ Scraper

# Inhaltsübersicht
- [IServ Scraper](#iserv-scraper)
- [Inhaltsübersicht](#inhaltsübersicht)
- [Voraussetzungen](#voraussetzungen)
- [Script ausführen](#script-ausführen)
  - [Ohne Python Kenntnisse](#ohne-python-kenntnisse)
  - [Mit Python Kenntnissen (Mehr als Informatikunterricht)](#mit-python-kenntnissen-mehr-als-informatikunterricht)
- [Konfiguration](#konfiguration)
  - [Filter einstellen](#filter-einstellen)
  - [Fortgeschritten](#fortgeschritten)
- [Fehler melden](#fehler-melden)

# Voraussetzungen

- Python 3.6+
- Alle Pakete die in der requirements.txt Datei aufgeführt sind:
  - httpx
  - beautifulsoup4
  - sanitize-filename

# Script ausführen
**Zugangsdaten (Passwörter und Benutzernamen) ausschließlich an vertraute Personen weitergeben!**

---
## Ohne Python Kenntnisse
[Python von python.org herunterladen](https://www.python.org/downloads/) und installieren,
**bei der Installation darauf achten den Haken bei `ADD Python to PATH` zu setzen!**

Einfach die run.bat Datei ausführen.

Es öffnet sich ein Konsolen Fenster in welchem nach Benutzername (`Username`) und Passwort (`Password`) gefragt wird.
Hier bitte ihren IServ Benutzernamen und Passwort eingeben.

Nun läuft das Script und sammelt ihre Daten.
Nicht wundern es hat einen `.venv` Ordner erstellt, dieser beinhaltet alle für das Script benötigten Pakete.

---
## Mit Python Kenntnissen (Mehr als Informatikunterricht)
Optimalerweise ein Virtualenviroment anlegen. (`python -m venv .venv`), das dann auch aktivieren.

Dependencies installieren `pip install -r requirements.txt`

Script ausführen `python src/scraper.py`

# Konfiguration
## Filter einstellen
Beim ersten ausführen des Scripts wird eine `filters.cfg` Datei erstellt.
Hier kann man Filter für den Namen einer Aufgabe einfügen, pro Zeile ein Filter.

Alle Aufgaben, deren Name eine oder mehrere dieser Filter enthält, werden nicht heruntergeladen.

**Achtung Groß-/Kleinschreibung wird beachtet!**

### Beispiel: <!-- omit in toc -->
filters.cfg:
```
WHG-Online Team
Sozialkunde
Mathe
```
In diesem Fall würden alle Aufgaben, deren Name "WHG-Online Team", "Sozialkunde" oder "Mathe" enthält,
ignoriert und dem entsprechend nicht verarbeitet.

- `"WHG-Online Team: Treffen"` würde ignoriert
- `"Sozialkunde Hausaufgaben"` würde ignoriert
- `"whg-online team: treffen"` würde **nicht** ignoriert, da Groß-/Kleinschreibung beachtet wird
- `"Deutsch Hausaufgaben"` würde nicht ignoriert, da der Name keinen der Filter enthält

---
## Fortgeschritten
**Achtung bitte mit den einzelnen Paketen vertraut machen und den Code anschauen!**

`scraper.py` enthält eine Klasse `Scraper` diese hat folgende Parameter:

- client Typ: `httpx.AsyncClient`
  - hier kann ein eigener Client bereitgestellt werden, falls man zum Beispiel einen anderen User-Agent verwenden möchte
- url Typ: `str`
  - eine URL zu einer IServ Instanz, standard mäßig die des Werner-Heisenberg-Gymnasiums Bad Dürkheim
- username  Typ: `str` **Auf keinen Fall auf GitHub pushen**
  - ein Benutzername, hilfreich wenn das Script automatisch laufen soll
- password Typ: `str` **Auf keinen Fall auf GitHub pushen**
  - ein Passwort, hilfreich wenn das Script automatisch laufen soll
- filters Typ: `list`
  - Liste an Filtern, die Klasse liest nicht selbst di `filters.cfg` Datei

# Fehler melden

Fehler bitte möglichst als GitHub Issue melden.
Möglichst die Fehlermeldung kopieren und anfügen.
Alternativ einen Screenshot mit der vollständigen Fehlermeldung bereitstellen.

Dabei darauf achten **keine Zugangsdaten oder andere sensible Daten** mit zu senden.