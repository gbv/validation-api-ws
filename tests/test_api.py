import pytest
import tempfile

# from unittest.mock import patch
# import os
# from pathlib import Path

from app import app, init

# cwd = Path().cwd()


def expect_error(client, method, path, json=None, error=None, code=400):
    res = client.open(path, method=method, json=json)
    assert res.status_code == code
    if error:
        if type(error) is str:
            error = {"message": error}
        error["code"] = code
        res = res.get_json()
        # print(res)
        for key in error:
            assert res.get(key, None) == error[key]


@pytest.fixture
def stage():
    with tempfile.TemporaryDirectory() as tempdir:
        yield tempdir


@pytest.fixture
def client(stage):
    app.testing = True

    init(title="Validation Service Test", stage=stage)

    with app.test_client() as client:
        def fail(*args, **kwargs):
            return expect_error(client, *args, **kwargs)
        yield client, fail  # , stage


def test_api(client):
    client, fail = client

    # start without collections
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"Validation Service Test" in resp.data
