#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return 'hi'

if __name__ == '__main__':
    import waitress
    waitress.serve(app, host='127.0.0.1', port=32437)
