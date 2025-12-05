import pytest
from tempfile import TemporaryDirectory

from lib import ValidationService


def test_config():

    with pytest.raises(Exception):
        service = ValidationService()

    service = ValidationService(profiles=[])
    assert service.profiles() == []

    profiles = [{
        "id": "json",
        "checks": ["json"],
        "url": "https://json.org/"
    }]

    service = ValidationService(profiles=profiles)
    assert service.profiles() == [{"id": "json", "url": "https://json.org/"}]

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
