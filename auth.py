# -*- coding: utf-8 -*-

import functools
import flask
import core


def authenticate(error):
    resp = flask.jsonify(error)
    resp.status_code = 401
    return resp


def requires_data_import_token(f):
    """
    Decorator function for *simple token* authentication only.

    For server to server communication only. Token must not be passed to users or javascript clients.
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.headers.get('Authorization', None)
        if not auth:
            return authenticate({
                'code': 'authorization_header_missing',
                'description': 'Authorization header is expected'
            })
        parts = auth.split()
        if parts[0].lower() != 'bearer':
            return authenticate({
                'code': 'invalid_header',
                'description': 'Authorization header must start with Bearer'})
        elif len(parts) == 1:
            return authenticate({
                'code': 'invalid_header',
                'description': 'Token not found'
            })
        elif len(parts) > 2:
            return authenticate({
                'code': 'invalid_header',
                'description': 'Authorization header must be Bearer + \s + token'
            })

        token = parts[1]
        if token != core.app.flask_app.config['DATA_IMPORT_TOKEN']:  # just a straight comparison
            return authenticate({
                'code': 'invalid_header',
                'description': 'Bearer token not valid'
            })

        return f(*args, **kwargs)

    return decorated
