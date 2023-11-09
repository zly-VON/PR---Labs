import requests
from bs4 import BeautifulSoup
import json

def parse(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    page_title = soup.select_one("header.adPage__header h1")
    price = soup.select_one("span.adPage__content__price-feature__prices__price__value")

    characteristics = {}
    for key in ['Suprafață totală', 'Nivelul']:
        value = soup.select_one(f"span.adPage__content__features__key:-soup-contains('{key}') + span.adPage__content__features__value")
        characteristics[key] = value.text.strip() if value else "None"

    data = {
        "url": url,
        "page_title": page_title.text.strip() if page_title else "None",
        "price": price.text.strip() if price else "None",
        "characteristics": characteristics
    }

    return data
