# -*- coding: utf-8 -*-

import functools
import flask
import core
from werkzeug.exceptions import Unauthorized


def requires_data_import_token(f):
    """
    Decorator function for *simple token* authentication only.

    For server to server communication only. Token must not be passed to users or javascript clients.
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.headers.get('Authorization', None)
        if not auth:
            raise Unauthorized('Authorization header is expected')
        parts = auth.split()
        if parts[0].lower() != 'bearer':
            raise Unauthorized('Authorization header must start with Bearer')
        elif len(parts) == 1:
            raise Unauthorized('Token not found')
        elif len(parts) > 2:
            raise Unauthorized('Authorization header must be Bearer + \s + token')

        token = parts[1]
        if token != core.app.flask_app.config['DATA_IMPORT_TOKEN']:  # just a straight comparison
            raise Unauthorized('Bearer token not valid')

        return f(*args, **kwargs)

    return decorated
