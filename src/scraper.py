from bs4 import BeautifulSoup
import requests

class Scraper:
    def __init__(self):
        self.client = requests.Session()