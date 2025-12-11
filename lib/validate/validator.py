import json
from pathlib import Path
from .json import parseJSON
from .jsonschema import validateJSON
from .xml import parseXML


schema = json.load((Path(__file__).parent / 'profiles-schema.json').open())


builtin = {
    "json": parseJSON,
    "xml": parseXML
}


def resolve(path, root):
    path = Path(path)
    if path.is_absolute() or not root:
        return path
    else:
        return root / path


def compile(check, root):
    if type(check) == str:
        if check in builtin:
            return builtin[check]
        else:
            # TODO: allow to reference another profile
            raise Exception(f"Unknown check: {config}")

    if "schema" in check and "language" in check:
        # TODO: support URL in additio to local file
        schema = resolve(check["schema"], root)

        match check["language"]:
            case "json-schema":
                schema = json.load(schema.open())
                return lambda data: validateJSON(parseJSON(data), schema)
            # case "xsd":
            #    pass  # TODO: load as local file or from URL with cache
            case _:
                raise Exception(f"Unsupported schema language: {check['language']}")

    raise Exception(f"Unkown check: {json.dumps(check)}")


class Validator(object):
    def __init__(self, profiles, **config):
        validateJSON(profiles, schema)

        root = config.get("root")

        checks = {p["id"]: p.get("checks", []) for p in profiles}
        if len(checks) != len(profiles):
            raise ValueError("Profiles must have unique ids")

        self.profiles = {}
        for p in profiles:
            id = p["id"]

            # TODO: support reference to profile as check
            checks[id] = [compile(c, root) for c in checks[id]]

            about = ['id', 'title', 'description', 'url', 'report']
            self.profiles[id] = {key: p[key] for key in about if p.get(key, False)}

        self.checks = checks

    def profile(self, id) -> dict:
        return self.profiles[id]

    def execute(self, profile, data=None, file=None):
        if file:
            data = Path(file).read_bytes()
        for check in self.checks[profile]:
            check(data)
