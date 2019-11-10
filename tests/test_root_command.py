import os

import pytest
from click.testing import CliRunner

from terroir.commands import terroir


commands = [
    'fetch_inventory',
    'update_models',
]


def test_root_terroir_command():
    runner = CliRunner()

    result = runner.invoke(terroir)

    assert result.exit_code == 0
    assert 'Usage: terroir [OPTIONS] COMMAND [ARGS]' in result.output
    for command in commands:
        assert command in result.output
