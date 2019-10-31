import re

from bs4 import BeautifulSoup
from urllib.parse import parse_qs
from urllib3.util import parse_url


class KenastonListParser(object):

    to_be_parsed = ['White', 'Rosé', 'Sparkling']
    parsed_wine_types = []

    def __call__(self, req):
        next_page = None
        wine_urls = []

        soup = BeautifulSoup(req.text, 'html.parser')
        links = [
            link for link in soup.find_all('a')
            if '/collections/types/products/' in link.get('href')
        ]

        for link in links:
            href = link.get('href')
            if href not in wine_urls:
                wine_urls.append(href)

        _, _, _, _, path, query, _ = parse_url(req.url)
        query_dict = parse_qs(query)
        _type = query_dict['q'][0]

        if len(links) > 0:
            next_page_num = int(query_dict['page'][0]) + 1
            next_page = path + '?' + re.sub(r'\d+', str(next_page_num), query)
        elif len(self.to_be_parsed) > 0:
            self.parsed_wine_types.append(_type)
            next_type = self.to_be_parsed.pop(0)
            next_page = path + '?'+ query.replace(_type, next_type)
            next_page = re.sub(r'\d+', '1', next_page)

        return wine_urls, next_page