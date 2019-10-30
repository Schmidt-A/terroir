import click

from terroir.inventory import inventory_cmd


@click.group()
def terroir():
    pass

def main():
    terroir.add_command(inventory_cmd)
    terroir()
