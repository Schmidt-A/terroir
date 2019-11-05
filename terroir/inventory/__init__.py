import os
import sys
import time
from configparser import ConfigParser

import click
import requests
from zope.dottedname.resolve import resolve as resolve_dotted


# Note: adding a command suffix to all commands to avoid module namespace issues
@click.command(name='fetch_inventory')
@click.argument('store', type=click.STRING)
@click.option(
    '-c', '--config_file', type=click.Path(),
    show_default=True, default='configs/fetch_inventory.ini')
@click.option(
    '-d', '--data_dir', type=click.Path(writable=True),
    show_default=True, default='data')
@click.option(
    '-f', '--force_overwrite', type=click.BOOL, is_flag=True,
    show_default=True, default=False)
def fetch_inventory_cmd(store, config_file, force_overwrite, data_dir):
    """Build up list of wines available on a store's website.

    Arguments:
    STORE: Store from which to fetch inventory.

        Supported options: kenaston, lc

    Options documentation:

    -c, --config: Path to config file.

    -s, --saved_urls: Location to save results to.

    -f, --force_overwrite: Overwrite file specified by --saved_urls. Useful if
        you want to refresh the list - new wines added, etc.
    """
    saved_urls = os.path.join(data_dir, 'inventory', store, 'urls.txt')
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
        req = requests.get(config[store]["base_url"] + next_page_url)
        wine_urls, next_page_url = list_parser(req)
        all_wine_urls.extend(wine_urls)
        time.sleep(0.1)

    print(f'Done fetching urls. Writing results to {saved_urls}')

    target_dir = os.path.dirname(saved_urls)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(saved_urls, 'w') as f:
        for url in all_wine_urls:
            f.write(config[store]['base_url'] + url + '\n')
