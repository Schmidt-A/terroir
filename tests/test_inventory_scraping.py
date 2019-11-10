import os

import mock
import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner

from terroir.commands import terroir
from terroir.inventory.scrapers import LCListScraper, KenastonListScraper
from fixtures import get_config_data
from utils import MockResponse, write_isolated_file


test_params = [
    (
        'lc',
        'lc_last_wines.html',
        'www.liquormarts.ca',
        'zuccardi-tito-paraje-altamira',
    ),
    (
        'kenaston',
        'kenaston_last_wines.html',
        'https://kenastonwine.com',
        'products/zard-refoso-pro',
    )
]

test_get_href_params = [
    (
        KenastonListScraper,
        'kenaston_next_href.html',
    ),
    (
        LCListScraper,
        'lc_next_href.html',
    )
]


def mocked_requests_get(*args, **kwargs):
    path = os.path.join('tests', 'data')

    if 'liquormarts' in args[0]:
        path = os.path.join(path, 'lc_last_wines.html')
        url = ''
    elif 'kenaston' in args[0]:
        path = os.path.join(path, 'kenaston_last_wines.html')
        url = 'https://kenastonwine.com/collections/types?page=5&q=Sparkling'
    with open(path) as f:
        html = f.read()

    return MockResponse(html, url)

def mocked_get_next_wine_type(self):
    return None


@pytest.mark.parametrize(
    'store, html_file, out_str_1, out_str_2', test_params)
@mock.patch('requests.get', side_effect=mocked_requests_get)
#@mock.patch.object(KenastonListScraper, 'get_next_wine_type', mocked_get_next_wine_type)
def test_mocked_full_inventory_command(mock_get, get_config_data, store, html_file, out_str_1, out_str_2):
    runner = CliRunner()
    config_file = os.path.join('configs', 'fetch_inventory.ini')
    config_data = get_config_data(config_file)
    html_file = os.path.join('tests', 'data', html_file)
    with open(html_file) as f:
        html = f.read().replace('\n', '')

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(html_file, html)

        result = runner.invoke(terroir, ['fetch_inventory', store])
        print(result.output)
        # Make sure it wrote urls how we expect
        with open(os.path.join('data', 'inventory', store, 'urls.txt')) as f:
            parsed_urls = f.read()

        assert result.exit_code == 0
        assert len(parsed_urls) > 0
        assert out_str_1 in parsed_urls
        assert out_str_2 in parsed_urls


# TODO: assert next fetch gets next_page when present

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_mocked_inventory_force_overwrite(mock_get, get_config_data):
    store = 'lc'
    runner = CliRunner()
    config_file = os.path.join('configs', 'fetch_inventory.ini')
    config_data = get_config_data(config_file)
    html_file = os.path.join('tests', 'data', 'lc_last_wines.html')
    with open(html_file) as f:
        html = f.read().replace('\n', '')
    real_urls_file = os.path.join('data', 'inventory', store, 'urls.txt')

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(html_file, html)
        write_isolated_file(real_urls_file, 'testdata')

        result = runner.invoke(terroir, ['fetch_inventory', store, '-f'])

        # Make sure it wrote urls how we expect
        with open(os.path.join('data', 'inventory', 'lc', 'urls.txt')) as f:
            parsed_urls = f.read()

        assert result.exit_code == 0
        assert 'force_overwrite was specified' in result.output
        assert len(parsed_urls) > 0
        assert 'https://www.liquormarts.ca' in parsed_urls
        assert 'zuccardi-tito-paraje-altamira' in parsed_urls


def test_no_overwrite_without_flag(get_config_data):
    store = 'lc'
    url = 'test.com'
    runner = CliRunner()
    config_file = os.path.join('configs', 'fetch_inventory.ini')
    config_data = get_config_data(config_file)
    data_file = os.path.join('data', 'inventory', store, 'urls.txt')

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(data_file, url)

        result = runner.invoke(terroir, ['fetch_inventory', store])

        assert result.exit_code == 0
        assert 'Use -f or --force-overwrite' in result.output

@pytest.mark.parametrize('scraper, html_file', test_get_href_params)
def test_scraper_gets_next_href(scraper, html_file):
    with open(os.path.join('tests', 'data', html_file)) as f:
        html = f.read().replace('\n', '')
        soup = BeautifulSoup(html, 'html5lib')
        test_scraper = scraper()
        a = test_scraper.get_next_page_href(soup)

    assert a != None