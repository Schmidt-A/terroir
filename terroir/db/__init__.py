import json
import os
import sys
from configparser import ConfigParser

import requests

import click
from zope.dottedname.resolve import resolve as resolve_dotted


@click.command(name='update_models')
@click.argument('store', type=click.STRING)
@click.option(
    '-c', '--config_file', type=click.Path(),
    show_default=True, default='configs/update_models.ini')
@click.option(
    '-d', '--data-dir', type=click.Path(),
    show_default=True, default='data')
def update_models_cmd(store, config_file, data_dir):
    saved_urls = os.path.join(data_dir, 'inventory', store, 'urls.txt')

    if not os.path.exists(saved_urls):
        print(
            f'Inventory list {saved_urls} does not exist. Please run the '
            f'fetch_inventory command for store {store} and then try again.'
        )
        sys.exit(1)

    config = ConfigParser()
    print(f'Reading config from {config_file}')
    config.read(config_file)

    parser = resolve_dotted(config[store]['parser'])()

    i = 0
    with open(saved_urls) as f:
        for url in f:
            url = url.strip()
            print(f'Fetching and scraping {url}')
            req = requests.get(url)
            data = parser(req)
            print(json.dumps(data.to_primitive()))
            i += 1
            if i > 4:
                break