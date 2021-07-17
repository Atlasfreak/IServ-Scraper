import csv
import datetime
from typing import BinaryIO

FIELDNAMES = [
    "Aufgabe",
    "Lehrer",
    "Startdatum",
    "Enddatum",
    "Link",
    "Beschreibung",
    "Abgabe",
]


def create_csv(file: BinaryIO, data: list[dict], fieldnames: list):
    writer = csv.DictWriter(file, fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return file


def create_zip_file():
    pass
