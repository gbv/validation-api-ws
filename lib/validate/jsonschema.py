from .error import ValidationError
import jsonschema


def validateJSON(data, schema):
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as err:
        pos = ""
        for elem in err.absolute_path:
            if isinstance(elem, int):
                pos += "/" + str(elem)
            else:
                pos += "/" + elem.replace("~", "~0").replace("/", "~1")
        pos = {"jsonpointer": pos}
        raise ValidationError(err.message, pos)
