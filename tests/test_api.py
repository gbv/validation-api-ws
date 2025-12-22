import pytest
import tempfile
from pathlib import Path
import io
from app import app, init


def expect_fine(client, method, path, result=None, code=200, **kwargs):
    res = client.open(path, method=method, **kwargs)
    assert res.status_code == code
    if result:
        assert res.get_json() == result
    return res.get_json()


def expect_fail(client, method, path, error=None, code=400, **kwargs):
    res = client.open(path, method=method, **kwargs)
    assert res.status_code == code
    if error:
        error = {"message": error, "code": code}
        res = res.get_json()
        # print(res)
        for key in error:
            assert res.get(key, None) == error[key]


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tempdir:
        yield tempdir


@pytest.fixture
def client(tmp_dir):
    app.testing = True

    files = Path(__file__).parent / 'server'

    profiles = [{
        "id": "json",
        "checks": ["json"]
    }]
    init(dict(title="Validation Service Test", files=files, downloads=tmp_dir, profiles=profiles))

    with app.test_client() as client:
        setattr(client, 'fail', lambda *args, **kw: expect_fail(client, *args, **kw))
        setattr(client, 'fine', lambda *args, **kw: expect_fine(client, *args, **kw))
        setattr(client, 'files', files)
        yield client


def test_html(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"Validation Service Test" in resp.data

    client.fail('GET', '/?crash=1', code=500, error="boom!")


def test_api(client):

    client.fine('GET', '/profiles', [
        {"id": "json"}
    ])

    client.fail('GET', '/xxx/validate?data=123', code=404,
                error="Profile not found: xxx")

    client.fail('GET', '/json/validate', code=400,
                error="Expect exactely one query parameter: data, url, file")

    client.fail('GET', '/json/validate?url=http://example.org/&data=123', code=400,
                error="Expect exactely one query parameter: data, url, file")

    client.fine('GET', '/json/validate?data={}')

    client.fail('GET', '/json', code=404)

    client.fine('GET', '/json/validate?data={', [{
        'message': 'Expecting property name enclosed in double quotes',
        'position': {'line': '1', 'linecol': '1:2', 'offset': '1'}}
    ])


def test_validate_file(client):

    client.fail('GET', '/json/validate?file=?', code=400,
                error="Filename must contain only characters [a-zA-Z0-9._-]")

    client.fail('GET', '/json/validate?file=not.found', code=404,
                error="File not found in local files: not.found")

    client.fine('GET', '/json/validate?file=valid.json')

    client.fine('GET', '/json/validate?file=invalid.json', [{
        'message': 'Expecting value',
        'position': {'line': '1', 'linecol': '1:1', 'offset': '0'}}])


def test_validate_upload(client):

    data = {'file': (io.BytesIO(b"{}"), 'test.json')}
    client.fine('POST', '/json/validate', content_type='multipart/form-data', data=data)

    client.fail('POST', '/json/validate', content_type='multipart/form-data', data={},
                error="Missing file upload")

    client.fine('POST', '/json/validate', data=b"{}")

    client.fine('POST', '/json/validate', data=b"[1,2", result=[{
        "message": "Expecting ',' delimiter",
        "position": {
            "line": "1",
            "linecol": "1:5",
            "offset": "4"
        }
    }])
