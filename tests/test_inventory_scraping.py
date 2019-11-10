import os

import mock
import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner

from terroir.commands import terroir
from terroir.inventory.scrapers import LCListScraper, KenastonListScraper
from fixtures import get_config_data
from utils import MockResponse, write_isolated_file


test_full_fetch_params = [
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


def common_conf_data(get_config_data, html_file):
    config_file = os.path.join('configs', 'fetch_inventory.ini')
    config_data = get_config_data(config_file)
    html_path = os.path.join('tests', 'data', html_file)
    with open(html_path) as f:
        html = f.read().replace('\n', '')

    return config_file, config_data, html_path, html


@pytest.mark.parametrize(
    'store, html_file, out_str_1, out_str_2', test_full_fetch_params)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_inventory_command(mock_get, get_config_data, store, html_file, out_str_1, out_str_2):
    runner = CliRunner()

    config_file, config_data, html_path, html = common_conf_data(
        get_config_data, html_file
    )

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(html_path, html)

        result = runner.invoke(terroir, ['fetch_inventory', store])

        # Make sure it wrote urls how we expect
        with open(os.path.join('data', 'inventory', store, 'urls.txt')) as f:
            parsed_urls = f.read()

        assert result.exit_code == 0
        assert len(parsed_urls) > 0
        assert out_str_1 in parsed_urls
        assert out_str_2 in parsed_urls


@pytest.mark.parametrize(
    'store, html_file, out_str_1, out_str_2', test_full_fetch_params)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_inventory_force_overwrite(
    mock_get, get_config_data, store, html_file, out_str_1, out_str_2):
    runner = CliRunner()
    config_file, config_data, html_path, html = common_conf_data(
        get_config_data, html_file
    )
    real_urls_file = os.path.join('data', 'inventory', store, 'urls.txt')

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(html_path, html)
        # Stub this in so app recognizes the data file exists.
        write_isolated_file(real_urls_file, 'testdata')

        result = runner.invoke(terroir, ['fetch_inventory', store, '-f'])

        # Make sure it wrote urls how we expect
        with open(os.path.join('data', 'inventory', store, 'urls.txt')) as f:
            parsed_urls = f.read()

        assert result.exit_code == 0
        assert 'force_overwrite was specified' in result.output
        assert len(parsed_urls) > 0
        assert out_str_1 in parsed_urls
        assert out_str_2 in parsed_urls


@pytest.mark.parametrize(
    'store',
    [
        ('lc'),
        ('kenaston')
    ])
def test_no_overwrite_without_flag(get_config_data, store):
    runner = CliRunner()
    config_file = os.path.join('configs', 'fetch_inventory.ini')
    config_data = get_config_data(config_file)

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(
            os.path.join('data', 'inventory', store, 'urls.txt'), 'testurl.com')

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