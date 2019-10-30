from bs4 import BeautifulSoup

class LCListParser(object):

    def __call__(self, req):
        next_page = None
        wine_urls = []

        soup = BeautifulSoup(req.text, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if href and 'product/' in href:
                # there are multiple <a> elements with the product link so we wind
                # up with duplicates unless we filter
                if href not in wine_urls:
                    wine_urls.append(href)
            elif link.get('title') == 'Go to next page':
                next_page = href

        return wine_urls, next_page