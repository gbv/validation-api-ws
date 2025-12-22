from lib import ValidationError, parseXML, validateXML
from xml.parsers.expat.errors import codes
import xml.etree.ElementTree as ET
from pathlib import Path

not_wellformed = [
    ('<a x="1"\n木="1" x="2"/>', {  # string
        "message": 'duplicate attribute',
        "position": {"line": "2", "linecol": "2:7"}}),
    ('<?xml version="1.0"?>\n<木/>?'.encode("UTF-8"), {  # binary
        "message": 'not well-formed (invalid token)',
        "position": {"line": "2", "linecol": "2:5"}}),
]


def test_wellformed():
    assert isinstance(parseXML("<x/>"), ET.Element)


def test_not_wellformed():
    for (data, err) in not_wellformed:
        try:
            assert isinstance(parseXML(data), ET.Element)
            assert 0 == "ValidationError should have been thrown!"  # pragma: no cover
        except ValidationError as e:
            assert e.to_dict() == err


files = Path(__file__).parent / 'files'
