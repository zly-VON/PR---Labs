import requests
from bs4 import BeautifulSoup
import json

list_data = []

def parse(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        total_area = soup.select_one("span.adPage__content__features__key:-soup-contains('Suprafață totală') + span.adPage__content__features__value")
        condition = soup.select_one("span.adPage__content__features__key:-soup-contains('Starea apartamentului') + span.adPage__content__features__value")
        number_of_rooms = soup.select_one("span.adPage__content__features__key:-soup-contains('Numărul de camere') + span.adPage__content__features__value")
        housing_stock = soup.select_one("span.adPage__content__features__key:-soup-contains('Fond locativ') + span.adPage__content__features__value")

        data = {
            'url': url,
            "page_title": soup.select_one('header.adPage__header h1').text.strip(),
            "price": soup.select_one('span.adPage__content__price-feature__prices__price__value').text.strip(),
            "update_time": soup.select_one('div.adPage__aside__stats__date').text.strip(),
            "characteristics": {
                "total area": total_area.text.strip() if total_area is not None else "None",
                "condition": condition.text.strip() if condition is not None else "None",
                "number of rooms": number_of_rooms.text.strip() if number_of_rooms is not None else "None",
                "housing stock": housing_stock.text.strip() if housing_stock is not None else "None",
            }            
        }

        return data

def extract_data():
    with open('urls.txt', 'r') as file:
        for urls in file:
            data = parse(urls.strip())
            list_data.append(data)

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(list_data, file, indent=4,  ensure_ascii=False)

extract_data()
