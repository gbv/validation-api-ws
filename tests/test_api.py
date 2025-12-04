import pytest
import tempfile

# from unittest.mock import patch
# import os
# from pathlib import Path

from app import app, init


def expect_fine(client, method, path, result=None, code=200):
    res = client.open(path, method=method)
    assert res.status_code == code
    if result:
        assert res.get_json() == result
    return res.get_json()


def expect_fail(client, method, path, error=None, code=400, **kwargs):
    res = client.open(path, method=method, **kwargs)
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

    profiles = [{
        "id": "json",
        "checks": ["json"]
    }]
    init(title="Validation Service Test", stage=stage, profiles=profiles)

    with app.test_client() as client:
        setattr(client, 'fail', lambda *args, **kw: expect_fail(client, *args, **kw))
        setattr(client, 'fine', lambda *args, **kw: expect_fine(client, *args, **kw))
        setattr(client, 'stage', stage)
        yield client


def test_html(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"Validation Service Test" in resp.data


def test_api(client):

    client.fine('GET', '/profiles', [
        {"id": "json"}
    ])

    client.fail('GET', '/validate/xxx?data=123', code=404,
                error="Profile not found: xxx")

    client.fail('GET', '/validate/json', code=400,
                error="Expect exactely one query parameter: data, url, or file")

    client.fail('GET', '/validate/json?url=http://example.org/&data=123', code=400,
                error="Expect exactely one query parameter: data, url, or file")

    client.fine('GET', '/validate/json?data={}')

    client.fine('GET', '/validate/json?data={', [{
        'message': 'Expecting property name enclosed in double quotes',
        'position': {'line': '1', 'linecol': '1:2', 'offset': '1'}}
    ])


# TODO: test file upload
"""
def test_post_validate_profile_upload(client):
    data = {'file': (io.BytesIO(b"file content"), 'test.txt')}
    response = client.post('/validate/profileA', content_type='multipart/form-data', data=data)
"""
