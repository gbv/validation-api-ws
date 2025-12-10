import pytest
from tempfile import TemporaryDirectory

from lib import ValidationService

from pathlib import Path


def test_config():

    with pytest.raises(Exception):
        service = ValidationService()

    service = ValidationService(profiles=[])
    assert service.profiles() == []

    profiles = [{
        "id": "json",
        "checks": ["json"],
        "url": "https://json.org/"
    }, {
        "id": "xml",
        "checks": ["xml"]
    }]

    service = ValidationService(profiles=profiles)
    assert service.profiles() == [
        {"id": "json", "url": "https://json.org/"}, {"id": "xml"}]

    with pytest.raises(Exception, match=r"This service does not support passing data via URL"):
        service.validate('json', url="http://example.org/")

    with pytest.raises(Exception, match=r"This service does not support passing data at server"):
        service.validate('json', file="example.json")

    with pytest.raises(Exception, match=r"Data must be string, bytes or IOBase"):
        service.validate('json', data=42)

    with TemporaryDirectory() as path:
        service = ValidationService(stage=path, profiles=[])

        with pytest.raises(FileNotFoundError, match=r"Missing stage directory:"):
            service = ValidationService(stage=f"{path}/XXX", profiles=[])

        service = ValidationService(profiles=profiles, downloads=path)

        with pytest.raises(Exception, match=r"URL invalid or too long"):
            service.validate('json', url="example.org")            

    path = Path(__file__).parent
    service = ValidationService(path / "config.json")
    assert service.profiles() == [ {"id": "json"} ]

    assert service.validate('json', url="http://example.org/") == [
        {'message': 'Expecting value',
         'position': {'line': '1', 'linecol': '1:1', 'offset': '0'}}]

    assert service.validate('json', url="http://example.org/valid.json") == []





