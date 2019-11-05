import json

import requests
from bs4 import BeautifulSoup
from urllib3.util import parse_url

from terroir.db.models import Grape, Wine


class LCModelParser(object):

    def __call__(self, req):
        soup = BeautifulSoup(req.text, 'html5lib')

        name = soup.find_all(attrs={'id': 'page-title'})[1].text

        upc = soup.find(
            attrs={'class': 'product_basic_details'}).find('div').find(
                'p').text.split('|')[1].strip().split(' ')[1]


        first_detail = soup.find(attrs={'class': 'product_details_detail'})
        details = first_detail.find('a').text.split('❭')
        _type = details[1].strip().split(' ')[0]
        grape = details[2].strip()
        grape = Grape({
            '_type': _type,
            'name': grape,
        })

        producer_links = soup.find(attrs={'class': 'producer_links'}).find_all(
            'a'
        )
        if len(producer_links) == 1 or len(producer_links) == 2:
            producer = producer_links[0].text
        elif len(producer_links) == 3:
            producer = producer_links[1].text
        else:
            producer = 'Unknown'

        price = soup.find(attrs={'class': 'product_price'}).text.strip()

        country = soup.find(
            attrs={'class': 'product_details_detail country'}).find_all(
                'a')[1].text

        profile = soup.find(
            attrs={'class': 'product_details_detail taste_profile'}).find(
                'a').get('title').split(' and ')

        description = soup.find(
            attrs={'class': 'product_basic_details'}).find_all(
                'div')[1].find_all('p')[1].text

        image = soup.find(
            attrs={'class': 'field-name-field-product-image-front'}).find(
                'img').get('src').split('?')[0]

        stores = [
            store.text.strip() for store in
            soup.find_all(attrs={'class': 'store-link'})
        ]
        url = parse_url(req.url)
        print(f'Scraping stores for {name}...')
        #stores = self._get_all_stores(f'{url.scheme}://{url.host}', soup, name)

        wine = Wine({
            'name': name,
            'upc': upc,
            'grape': grape,
            'producer': producer,
            'price': float(price[1:]),
            'country': country,
            'websites': [req.url],
            'profile': profile,
            'description': description,
            'image': image,
            'stores': stores,
        })

        return wine

    def _get_all_stores(self, domain, soup, name):
        stores = [
            store.text.strip() for store in
            soup.find_all(attrs={'class': 'store-link'})
        ]
        page_hrefs = [
            el.find('a').get('href') for el in
            soup.find_all(attrs={'class': 'pager-item'})
        ]

        for i, href in enumerate(page_hrefs):
            print(f'\tScraping store page {i+1}...')
            store_req = requests.get(domain + href)
            store_soup = BeautifulSoup(store_req.text, 'html5lib')
            stores.extend([
                store.text.strip() for store in
                store_soup.find_all(attrs={'class': 'store-link'})
            ])
        print(f'Done scraping stores for {name}')

        return stores