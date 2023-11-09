import re
import requests
from bs4 import BeautifulSoup

links = set()
base_url = "https://999.md"
page_url = f"{base_url}/ro/list/real-estate/apartments-and-rooms"

def parse(url, page, max_page = 1):
    print(f"Parsing page {page}...")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for a_tag in soup.find_all('a', href=True):
        href = a_tag.get('href')
        if href and re.search(r'/ro/\d+', href):
            abs_url = f"{base_url}{href}"
            links.add(abs_url)

    if page < max_page:
        next_url = f"{page_url}?page={page + 1}"
        parse(next_url, page + 1)

    return links