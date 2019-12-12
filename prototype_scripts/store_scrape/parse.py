from argparse import ArgumentParser
import time

from bs4 import BeautifulSoup
import requests
'''
class WineScrapeArgParser(ArgumentParser):

    def __init__(self):
        ArgumentParser.__init__(
            self,
            description=(
                'Scrape MLCC website to build up list of individual wine pages.'
                'Then GET each in order to build models with store, etc.'
            )
        )
        self.add_argument(
            '--list_scrape', dest='scrape', default=False,
            help='Scrape for full list of wines. Only needed if don\'t already'
                 'have a list of wine URLs.'
        )
        self.add_argument('--store')
'''
BASE_URL = 'https://www.liquormarts.ca'
MAIN_URL = BASE_URL + '/search-products/712?f%5B0%5D=field_category_type%3A712&f%5B1%5D=field_out_of_stock%3A0'
prod_links = []

def process_list_page(url):
    print(url)
    next_page = None
    r = requests.get(url)
    page = r.text
    soup = BeautifulSoup(page, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href and 'product/' in href:
            prod_links.append(href)
        elif link.get('title') == 'Go to next page':
            next_page = link.get('href')

    return next_page

'''
// Get fetches to list all wines
next_page = process_list_page(MAIN_URL)
while next_page:
    next_page = process_list_page(BASE_URL+next_page)
    time.sleep(.1)

with open('wine_urls.txt', 'w') as f:
    for link in prod_links:
        f.write(BASE_URL + link + '\n')

'''
lines = [line.rstrip('\n') for line in open('wine_sorted.txt')]
# filter by store
for line in lines:
    r = requests.get(line)
    page = r.text
    soup = None

    if 'Bison' in page:
        print(line)