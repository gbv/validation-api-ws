from .error import ValidationError
from io import IOBase
import xml.etree.ElementTree as ET
from xml.parsers.expat import ErrorString

def parseXML(data) -> ET.Element:
    try:
        if isinstance(data, IOBase):
            return ET.parse(data)
        else:
            return ET.fromstring(data)
    except ET.ParseError as e:
        line, col = e.position
        pos = {"line": f"{line}"}
        # if col > 0: # TODO: does col start with zero?
        pos["linecol"] = f"{line}:{col+1}"
        code = e.code
        raise ValidationError(ErrorString(code), pos)
