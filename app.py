from flask import Flask, jsonify, render_template, request
from waitress import serve
from lib import Validator, ApiError, NotFound, ValidationError
from pathlib import Path
import json
import argparse
import os

app = Flask(__name__)
app.json.compact = False

validator = None


def init(**config):
    global validator

    if config.get("debug", False):
        app.debug = True

    app.config['title'] = config.get('title', 'Validation Service')
    app.config['stage'] = config.get('stage', os.getenv('STAGE', 'stage'))

    validator = Validator(**config)


@app.errorhandler(ApiError)
def handle_apierror(e):
    return jsonify(e.to_dict()), type(e).code


@app.errorhandler(ValidationError)
def handle_validationerror(e):
    e = e.to_dict()
    e["code"] = 400
    return jsonify(e), 400


@app.route('/')
def get_index():
    return render_template('index.html', **app.config)

# TODO: favicon
# route('GET', '/icon.png', lambda: send_file("static/nfdi4objects-logo.png"))


@app.route('/profiles')
def get_profiles():
    return validator.profiles_metadata()


def profile_defined(profile):
    try:
        validator.profile(profile)
    except KeyError:
        raise NotFound(f"Profile not found: {profile}")


def validate(profile, data):
    errors = []
    try:
        validator.execute(profile, data)
    except ValidationError as e:
        errors.append(e.to_dict())
    return errors


@app.route('/validate/<profile>')
def get_validate(profile):
    profile_defined(profile)
    params = dict([(k, request.args.get(k)) for k in ['file', 'url', 'data'] if k in request.args])
    if len(params) != 1:
        raise ApiError("Expect exactely one query parameter: data, url, or file")
    data = params['data']  # TODO: support file and URL
    return validate(profile, data)


@app.route('/validate/<profile>', methods=['POST'])
def post_validate(profile):
    profile_defined(profile)
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        if 'file' not in request.files:
            raise ApiError("Missing file upload")
        file = request.files['file']
        data = file.read()
    else:
        data = request.data
        if not data:
            raise ApiError("Missing request body")
    return validate(profile, data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=argparse.BooleanOptionalAction, help="Use WSGI")
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction)

    config_file = "config.json" if Path('config.json').exists() else "config.default.json"
    parser.add_argument('config', help="Config file", default=config_file, nargs='?')
    args = parser.parse_args()

    print(f"Loading configuration from {args.config}")
    config = json.load(Path(args.config).open())
    # TODO: check: config must be object with profiles

    config['debug'] = args.debug
    port = config.get('port', 7007)
    init(**config)
    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=port, threads=8)
    else:
        app.run(host="0.0.0.0", port=port, debug=args.debug)
