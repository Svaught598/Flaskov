import os
import sys
import tempfile

import pytest

from ..flaskov import *

app = create_app()

@pytest.fixture
def client():
    print(sys.path)
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        # with app.app_context():
        #     init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_index_route(client):
    rv = client.get("/")
    assert b'some link' in rv.data