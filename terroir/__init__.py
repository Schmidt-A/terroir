import click

from terroir.inventory import fetch_inventory_cmd


@click.group()
def terroir():
    pass

def main():
    terroir.add_command(fetch_inventory_cmd)
    terroir()
