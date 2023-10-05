import os
import json
import requests
from bs4 import BeautifulSoup


os.makedirs("./output", exist_ok=True)

base_url = 'http://127.0.0.1:8080'
paths = ['/', '/about', '/contacts', '/product']


def parse(path):
    response = requests.get(base_url + path)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        filename = path.strip('/') + '.html'
        if filename == ".html" :
            filename = "homepage.html"

        with open('output/' + filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        if path == "/product":
            index = 0
            product_links = soup.find_all('a')
            for link in product_links:
                href = link.get('href')
                if href and href.startswith('/product/'):
                    parse_products(href, index)
                    index += 1

    else:
        print("Failed to retrieve the web page. Status code: {}".format(response.status_code))


def parse_products(href, index):
    response = requests.get(base_url + href)

    if response.status_code == 200:
        product_soup = BeautifulSoup(response.text, 'html.parser')
        
        product_detail = {
            "name": product_soup.find("h1").text,
            "author": product_soup.find('p', id="p1").text.split('Author: ')[1],
            "price": float(product_soup.find('p', id="p2").text.split('Price: ')[1]),
            "description": product_soup.find('p', id="p3").text.split('Description: ')[1]
        }

        filename = 'product{}.json'.format(index)
        with open('output/' + filename, 'w') as json_file:
            json.dump(product_detail, json_file, indent=4)

    else:
        print("Failed to retrieve the web page. Status code: {}".format(response.status_code))


for path in paths:
    parse(path)
