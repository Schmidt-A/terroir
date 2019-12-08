import os

import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner
from schematics.exceptions import DataError
from tinydb import TinyDB

from terroir.commands import terroir
from terroir.db.models import Grape, Wine
from terroir.db.scrapers import LCModelScraper
from terroir.inventory import fetch_inventory_cmd
from utils import write_isolated_file


stores = [
    'lc',
    'kenaston',
]

model_urls = [
    (
        'lc',
        'https://www.liquormarts.ca/product/14-hands-hot-trot-red-blend/750-ml',
        '14 Hands Hot to Trot Red Blend',
        'Varietal Blend',
        'Red',
    ),
    (
        'lc',
        'https://www.liquormarts.ca/product/hen-house-ruffled-red-vqa/750-ml',
        'Hen House Ruffled Red VQA',
        'Varietal Blend',
        'Red',
    )
]
@pytest.mark.slow()
@pytest.mark.parametrize('store, url, wine, grape, _type', model_urls)
def test_update_models_command(store, url, wine, grape, _type, get_config_data):
    runner = CliRunner()
    config_file = os.path.join('configs', 'update_models.ini')
    config_data = get_config_data(config_file)
    data_file = os.path.join('data', 'inventory', store, 'urls.txt')
    db_file = os.path.join('data', 'db', 'wines.json')

    with runner.isolated_filesystem():
        # Set up config and data
        write_isolated_file(config_file, config_data)
        write_isolated_file(data_file, url)
        write_isolated_file(db_file, '{"_default": {}}')

        result = runner.invoke(terroir, ['update_models', store])
        assert result.exit_code == 0
        print(result.output)

        db = TinyDB(db_file)
        test_wine = Wine(db.all()[0])
        assert test_wine.name == wine
        assert test_wine.grape.name == grape
        assert test_wine.grape._type == _type  # pylint: disable-all
        assert len(test_wine.stores) > 0

@pytest.mark.slow()
@pytest.mark.parametrize('store', stores)
def test_update_models_no_urls(store):
    runner = CliRunner()
    out_str = f'Inventory list data/inventory/{store}/urls.txt does not exist'

    with runner.isolated_filesystem():
        result = runner.invoke(terroir, ['update_models', store])

        assert out_str in result.output
        assert result.exit_code == 1

@pytest.mark.slow()
def test_lc_unhandled_producer_links_marks_unknown():
    scraper = LCModelScraper()
    with open('tests/data/lc_test_nonstandard_producer_links.html') as f:
        page_data = f.read().replace('\n', '')

    producer = scraper._get_producer(BeautifulSoup(page_data, 'html5lib'))

    assert producer == 'Unknown'

def test_invalid_type_raises_error():
    with pytest.raises(DataError):
        broken_grape = Grape({
            'name': 'broken_grape',
            '_type': 'not a valid wine type'
        })
        broken_grape.validate()