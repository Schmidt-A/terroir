from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlencode
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
        url_params = parse_qs(query)
        _type = url_params['q'][0]

        if len(links) > 0:
            url_params['q'] = _type
            url_params['page'] = int(url_params['page'][0]) + 1
            next_page = path + '?' + urlencode(url_params)
        elif len(self.to_be_parsed) > 0:
            self.parsed_wine_types.append(_type)
            url_params['q'] = self.to_be_parsed.pop(0)
            url_params['page'] = 1
            next_page = path + '?' + urlencode(url_params)

        return wine_urls, next_page