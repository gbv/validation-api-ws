from .error import ValidationError
import xmlschema


def validateXML(tree, schema):
    schema = xmlschema.XMLSchema(schema)

    # TODO: DTD validation with embedded DTD (with lxml)
    # TODO: Schematron validation with pyschematron

    return [
        ValidationError(e.reason, position={"xpath": e.path} if e.path else None)
        for e in schema.iter_errors(tree)
    ]
