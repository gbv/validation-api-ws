from .validate import Validator, ValidationError
from .urlcache import URLCache
from pathlib import Path
import validators
import io
import re


class ValidationService:
    def __init__(self, **config):

        for name in ['stage', 'reports', 'downloads']:
            path = config.get(name, False)
            if path:
                path = Path(path)
                setattr(self, name, path)
                if not path.is_dir():
                    raise FileNotFoundError(f"Missing {name} directory: {path}")
            else:
                setattr(self, name, None)

        if self.downloads:
            self.urlcache = URLCache(self.downloads)
        else:
            self.urlcache = None

        self.validator = Validator(**config)

    def profiles(self):
        return self.validator.profiles_metadata()

    def profile(self, id):
        return self.validator.profile(id)

    def validate(self, profile, data=None, url=None, file=None):

        if sum(1 for p in [data, file, url] if p or p == "") != 1:
            raise ValueError("Expect exactely one query parameter: data, url, file")

        if data:
            if isinstance(data, io.IOBase):
                data = data.read()
            if not (type(data) is str or type(data) is bytes):
                raise ValueError("Data must be string, bytes or IOBase")
        elif url:
            if self.urlcache:
                if not (validators.url(url) and re.match('^https?://') and len(url) <= 4096):
                    raise ValueError("URL invalid or too long")
                file, _ = self.urlcache.fetch(url)
            else:
                raise ValueError("This service does not support passing data via URL")
        else:
            if self.stage:
                if not re.match('^[a-zA-Z0-9_-][a-z0-9._-]*$', file):
                    raise ValueError("Filename must contain only characters [a-zA-Z0-9._-]")
                file = Path(self.stage / file)
                if not file.is_file():
                    raise LookupError(f"File not found in local stage: {file.name}")
            else:
                raise ValueError("This service does not support passing data at server")

        errors = []
        try:
            self.validator.execute(profile, data, file)
        except ValidationError as e:
            errors.append(e.to_dict())
        return errors
