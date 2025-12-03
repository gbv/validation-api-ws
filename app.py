from flask import Flask, jsonify, render_template
from waitress import serve
from lib import ApiError, ValidationError
import argparse
import os


app = Flask(__name__)
app.json.compact = False


def init(**config):
    title = config.get('title', os.getenv('TITLE', 'Validation Service'))

    if config.get("debug", False):
        app.debug = True
        title = f"{title} (debugging mode)"

    app.config['title'] = title
    app.config['stage'] = config.get('stage', os.getenv('STAGE', 'stage'))


@app.errorhandler(ApiError)
def handle_apierror(e):
    return jsonify(e.to_dict()), type(e).code


@app.errorhandler(ValidationError)
def handle_validationerror(e):
    e = e.to_dict()
    e["code"] = 400
    return jsonify(e), 400


def route(method, path, fn):
    fn.__name__ = f'{method}-{path}'
    app.add_url_rule(path, methods=[method], view_func=fn)


def api(method, path, fn):
    route(method, path, lambda *args, **kws: jsonify(fn(*args, **kws)))


route('GET', '/', lambda: render_template('index.html', **app.config))

# TODO: favicon
# route('GET', '/icon.png', lambda: send_file("static/nfdi4objects-logo.png"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=argparse.BooleanOptionalAction, help="Use WSGI")
    parser.add_argument('-p', '--port', type=int, default=7007)
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    init(debug=args.debug)
    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=args.port, threads=8)
    else:
        app.run(host="0.0.0.0", port=args.port, debug=args.debug)
