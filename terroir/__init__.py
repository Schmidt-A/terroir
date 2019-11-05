import click

from terroir.commands import terroir
from terroir.inventory import fetch_inventory_cmd
from terroir.db import update_models_cmd


def main():
    terroir()
