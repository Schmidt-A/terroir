import os
import sys
import time
from argparse import ArgumentParser
from configparser import ConfigParser

import click
import requests
from bs4 import BeautifulSoup
from zope.dottedname.resolve import resolve as resolve_dotted

# Note: adding a command suffix to all commands to avoid module namespace issues
@click.command(name='inventory')
@click.argument('store', type=click.STRING)
@click.option(
    '-c', '--config_file', type=click.Path(), default='configs/inventory.ini')
@click.option(
    '-s', '--saved_urls', type=click.Path(writable=True),
    default='data/saved_urls.txt')
@click.option(
    '-f', '--force_overwrite', type=click.BOOL, is_flag=True, default=False)
def inventory_cmd(store, config_file, force_overwrite, saved_urls):
    """Build up list of wines available on a store's website.

    Arguments:
    STORE: Store from which to fetch inventory.

        Supported options: lc

    Options documentation:

    -c, --config: Path to config file. default: configs/inventory.ini

    -s, --saved_urls: Location to save results to. default: data/saved_urls.txt

    -f, --force_overwrite: Overwrite file specified by --saved_urls. Useful if
        you want to refresh the list - new wines added, etc. default: False
    """

    config = ConfigParser()
    print(f'Reading config from {config_file}')
    config.read(config_file)

    all_wine_urls = []

    if os.path.exists(saved_urls) and not force_overwrite:
        print(
            f'URLs file {saved_urls} already exists and force overwrite '
            'was not specified. Use -f or --force-overwrite if you want to '
            'overwrite this file.\nExiting.'
        )
        sys.exit(0)
    if os.path.exists(saved_urls) and force_overwrite:
        print(
            f'URLs file {saved_urls} exists but force_overwrite was '
            'specified. Beginning URL fetch.'
        )
    elif not os.path.exists(saved_urls):
        print(f'Beginning URL fetch (this can take some time)...')

    # Setup for processing the first page
    next_page_url = config[store]["first_query_url"]

    # Initialize list parser defined for the given store
    list_parser = resolve_dotted(config[store]['list_parser'])()

    while next_page_url:
        # TODO: debug/verbose when logging set up.
        print(f'Processing {next_page_url}')
        wine_urls, next_page_url = list_parser(
            config[store]["base_url"] + next_page_url
        )
        all_wine_urls.extend(wine_urls)
        time.sleep(0.1)
    print(f'Done fetching urls. Writing results to {saved_urls}')

    with open(saved_urls, 'w') as f:
        for url in all_wine_urls:
            f.write(config[store]['base_url'] + url + '\n')