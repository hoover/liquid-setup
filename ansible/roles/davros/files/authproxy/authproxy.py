#!/usr/bin/env python3

import sys
import requests
from paste.proxy import Proxy
import flask

upstream = Proxy('http://127.0.0.1:51358')

app = flask.Flask(__name__)

config = app.config
config.from_pyfile('config/basename.py')
config.from_pyfile('config/secret.py')
config.from_pyfile('config/oauth.py')


def authenticate():
    access_token = flask.session.get('access_token')
    if not access_token:
        print('auth fail - no access token', file=sys.stderr)
        return False

    profile_url = config['LIQUID_URL'] + '/accounts/profile'
    profile_resp = requests.get(profile_url, headers={
        'Authorization': 'Bearer {}'.format(flask.session['access_token']),
    })

    if profile_resp.status_code != 200:
        print('auth fail - profile response: {!r}'.format(profile_resp))
        return False

    profile = profile_resp.json()
    if not profile:
        print('auth fail - empty profile: {!r}'.format(profile))
        return False

    return True


@app.before_request
def dispatch():
    if not flask.request.path.startswith('/__auth/'):
        if not authenticate():
            flask.session.pop('access_token', None)
            return flask.redirect('/__auth/')

        return upstream


@app.route('/__auth/')
def login():
    return flask.redirect(
        '{}/o/authorize/?response_type=code&client_id={}'
        .format(config['LIQUID_URL'], config['LIQUID_CLIENT_ID'])
    )


@app.route('/__auth/callback')
def callback():
    redirect_uri = flask.request.base_url
    token_resp = requests.post(
        config['LIQUID_URL'] + '/o/token/',
        data={
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
            'code': flask.request.args['code'],
        },
        auth=(config['LIQUID_CLIENT_ID'], config['LIQUID_CLIENT_SECRET']),
    )
    if token_resp.status_code != 200:
        raise RuntimeError("Could not get token: {!r}".format(token_resp))

    token_data = token_resp.json()
    token_type = token_data['token_type']
    if token_type != 'Bearer':
        raise RuntimeError(
            "Expected token_type='Bearer', got {!r}"
            .format(token_type)
        )

    flask.session['access_token'] = token_data['access_token']
    return flask.redirect('/')


LOGGED_OUT = """\
<!doctype html>
<p>You have been logged out.</p>
<p><a href="/">home</a></p>
"""


@app.route('/__auth/logout')
def logout():
    flask.session.pop('access_token', None)
    return LOGGED_OUT


if __name__ == '__main__':
    import waitress
    waitress.serve(app, host='127.0.0.1', port=32437)
