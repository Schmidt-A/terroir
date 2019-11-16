from terroir.db import setup_db


def test_db_initialization():
    db = setup_db('data/db/wines.json')

    assert db is not None
