from flask import Flask, jsonify, render_template, request
from waitress import serve
from lib import ValidationService
from pathlib import Path
import json
import argparse

app = Flask(__name__)
app.json.compact = False

service = None


def init(config):
    global service
    service = ValidationService(**config)
    app.config['title'] = config.get('title', 'Validation Service')
    return config.get('port', 7007)


class ApiError(Exception):
    code = 400


class NotFound(ApiError):
    code = 404


@app.errorhandler(ApiError)
def handle_apierror(e):
    body = {
        "code": type(e).code,
        "message": str(e)
    }
    return jsonify(body), body['code']

# TODO: handle internal server errors


@app.route('/')
def get_index():
    return render_template('index.html', **app.config)


@app.route('/profiles')
def get_profiles():
    return service.profiles()


@app.route('/<profile>/validate', methods=['GET', 'POST'])
def validate(profile):
    if not service.has(profile):
        raise NotFound(f"Profile not found: {profile}")

    if request.method == 'GET':
        params = ['data', 'url', 'file']
        args = dict([(k, request.args.get(k)) for k in params if k in request.args])
    else:
        mime = request.content_type or ''
        if mime == 'multipart/form-data':
            if 'file' not in request.files:
                raise ApiError("Missing file upload")
            args = {"data": request.files['file'].stream}
        else:
            args = {"data": request.get_data()}

    try:
        return service.validate(profile, **args)
    except ValueError as e:
        raise ApiError(str(e))
    except LookupError as e:
        raise NotFound(str(e))


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=argparse.BooleanOptionalAction, help="Use WSGI")
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction)

    config_file = "config.default.json"
    for file in [Path("config.json"), Path("config") / "config.json"]:
        if file.exists():
            config_file = file

    parser.add_argument('config', help="Config file or directory", default=config_file, nargs='?')
    args = parser.parse_args()

    if Path(args.config).is_dir():
        args.config = Path(args.config) / "config.json"

    print(f"Loading configuration from {args.config}")
    port = init(json.load(Path(args.config).open()))

    app.debug = args.debug

    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=port, threads=8)
    else:
        app.run(host="0.0.0.0", port=port, debug=args.debug)
