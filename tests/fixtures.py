import pytest

@pytest.fixture
def get_config_data():
    def _get_config_data(config_file):
        with open(config_file) as f:
            return f.readlines()

    return _get_config_data