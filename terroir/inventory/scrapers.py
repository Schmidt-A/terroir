from urllib.parse import parse_qs, urlencode

from bs4 import BeautifulSoup
from urllib3.util import parse_url


class LCListScraper(object):

    def __call__(self, req):
        soup = BeautifulSoup(req.text, 'html5lib')
        wine_urls = self.get_wine_links(soup)
        next_page = self.get_next_page_href(soup)

        return wine_urls, next_page

    def get_wine_links(self, soup):
        wine_urls = []

        links = soup.find('ul', attrs={'class': 'product-list'}).find_all(
            'a', href=lambda href: href and "product" in href)

        # there are multiple <a> elements with the product link so we wind
        # up with duplicates unless we filter
        for link in links:
            href = link.get('href')
            if href not in wine_urls:
                wine_urls.append(href)

        return wine_urls

    def get_next_page_href(self, soup):
        a = soup.find('a', attrs={'title': 'Go to next page'})
        if a:
            return a.get('href')
        return None

class KenastonListScraper(object):

    to_be_parsed = ['White', 'Rosé', 'Sparkling']
    parsed_wine_types = []

    def __call__(self, req):
        next_page = None
        wine_urls = []

        soup = BeautifulSoup(req.text, 'html.parser')

        wine_urls = self.get_wine_links(soup)
        next_page = self.get_next_page_href(soup)
        _, _, _, _, path, query, _ = parse_url(req.url)
        url_params = parse_qs(query)
        _type = url_params['q'][0]

        if not next_page:
            next_type = self.get_next_wine_type()
            if next_type:
                self.parsed_wine_types.append(_type)
                url_params['q'] = next_type
                url_params['page'] = 1
                next_page = path + '?' + urlencode(url_params)

        return wine_urls, next_page

    def get_wine_links(self, soup):
        wine_urls = []

        links = [
            link for link in soup.find_all('a')
            if '/collections/types/products/' in link.get('href')
        ]

        for link in links:
            href = f'{link.get("href")}.json'
            if href not in wine_urls:
                wine_urls.append(href)

        return wine_urls

    def get_next_page_href(self, soup):
        a = soup.find('a', attrs={'class': 'next'})
        if a:
            return a.get('href')
        return None

    def get_next_wine_type(self):
        if len(self.to_be_parsed) > 0:
            return self.to_be_parsed.pop(0)
        return None
