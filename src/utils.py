import csv
import datetime
from typing import BinaryIO

FIELDNAMES = [
    "Aufgabe",
    "Lehrer",
    "Startdatum",
    "Enddatum",
    "Link",
    "Tags",
    "Beschreibung",
    "Bereitgestellte Dateien",
    "Abgabetext",
    "Abgabedateien",
    "Rückmeldungstext",
    "Rückmeldungsdateien",
]


def create_csv(file: BinaryIO, data: list[dict], fieldnames: list = None):
    fieldnames = fieldnames if fieldnames is not None else FIELDNAMES
    writer = csv.DictWriter(file, fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return file


def create_zip_file():
    pass
