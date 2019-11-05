import click

from terroir.inventory import fetch_inventory_cmd
from terroir.db import update_models_cmd


@click.group()
def terroir():
    pass

def main():
    terroir.add_command(fetch_inventory_cmd)
    terroir.add_command(update_models_cmd)
    terroir()
