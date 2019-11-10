import click

from terroir.commands import terroir
# Super strange behaviour from click - if these are not imported,
# the terroir() main command invocation does not know about them.
from terroir.db import update_models_cmd
from terroir.inventory import fetch_inventory_cmd

def main():
    terroir()
