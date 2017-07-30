#!/usr/bin/env python3

from werkzeug.wsgi import responder
from werkzeug.wrappers import Request
from paste.proxy import Proxy
import flask

proxy_app = Proxy('http://127.0.0.1:51358')

auth_app = flask.Flask(__name__)


@auth_app.route('/__auth/')
def home():
    return "login goes here"


@responder
def dispatch(environ, start_response):
    request = Request(environ, shallow=True)

    if request.path.startswith('/__auth/'):
        return auth_app

    return proxy_app


if __name__ == '__main__':
    import waitress
    waitress.serve(dispatch, host='127.0.0.1', port=32437)
