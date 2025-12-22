from lib import ValidationError, parseXML, validateXML
import xml.etree.ElementTree as ET
from pathlib import Path
import json

not_wellformed = [
    ('<a>\n', {  # string
        "message": "no element found",
        "position": {"line": "2", "linecol": '2:1'}}),
    ('<a x="1"\n木="1" x="2"/>', {  # string
        "message": 'duplicate attribute',
        "position": {"line": "2", "linecol": "2:7"}}),
    ('<?xml version="1.0"?>\n<木/>?'.encode("UTF-8"), {  # binary
        "message": 'not well-formed (invalid token)',
        "position": {"line": "2", "linecol": "2:5"}}),
]

# TODO: check invalid DTD

def test_wellformed():
    assert isinstance(parseXML("<x/>"), ET.Element)


def test_not_wellformed():
    for (data, err) in not_wellformed:
        try:
            assert isinstance(parseXML(data), ET.Element)
            assert 0 == "ValidationError should have been thrown!"  # pragma: no cover
        except ValidationError as e:
            assert e.to_dict() == err


dir = Path(__file__).parent

with (dir / "xml-cases.json").open() as f:
    cases = json.load(f)


def test_invalid():
    for test in cases:
        file = dir / test["file"]
        xml = parseXML(file.read_text())
        errors = validateXML(xml, (dir / "schema.xsd"))
        assert [e.to_dict() for e in errors] == test["errors"]
