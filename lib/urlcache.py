from pathlib import Path
import hashlib
import requests
import json


class URLCache(object):

    def __init__(self, dir):
        self.dir = Path(dir)
        if not self.dir.is_dir():
            raise FileNotFoundError(f"Missing cache directory: {dir}")

    def hash(self, url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def fetch(self, url, cached=True):
        hash = self.hash(url)
        body_file = self.dir / hash
        meta_file = self.dir / f"{hash}.json"

        # return cached copy
        if cached and body_file.exists() and meta_file.exists():
            body = body_file.read_bytes()
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            return body_file, meta

        response = requests.get(url)
        response.raise_for_status()
        body = response.content
        meta = dict(response.headers)

        meta['url'] = url
        body_file.write_bytes(body)
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return body_file, meta
