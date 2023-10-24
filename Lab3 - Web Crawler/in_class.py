import re
import requests
import itertools
from bs4 import BeautifulSoup

items = set()
pattern = re.compile(r'ro/\d+')

base_url = 'https://999.md'
url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page={}'

def parse(url, page):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(requests.get(url.format(page)).content, 'html.parser')
        links = soup.find_all('a', href=pattern)

        for link in links:
            href = link.get('href')
            if href:
                abs_url = base_url + href
                items.add(abs_url)

        if page == max_page:
            with open('urls.txt', 'w') as file:
                for item in items:
                    file.write(item + '\n')

    else:
        print(f'Failed to retrieve the web page. Status code: {response.status_code}')


max_page = 5
for page in range(1, max_page + 1):
    parse(url, page)