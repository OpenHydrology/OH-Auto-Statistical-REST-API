# -*- coding: utf-8 -*-

import functools
import flask
import core
import jwt
import base64
from werkzeug.exceptions import Unauthorized


def requires_data_import_token(f):
    """
    Decorator function for *simple token string* authentication only.

    For server to server communication only. Token must not be passed to users or javascript clients.
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = auth_token(flask.request.headers)
        if token != core.app.flask_app.config['DATA_IMPORT_TOKEN']:  # just a straight comparison
            raise Unauthorized('Bearer token not valid')

        return f(*args, **kwargs)

    return decorated


def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = auth_token(flask.request.headers)
        flask.g.user = authenticate_user(token)
        return f(*args, **kwargs)

    return decorated


def auth_token(headers):
    """
    Return Bearer token from Authorization header.

    Raises :class:`werkzeug.exceptions.Unauthorized` if no or invalid Authorization header provided.

    :param headers: request headers
    :type headers: dict
    :return: Bearer token
    :rtype: str
    """
    auth = headers.get('Authorization', None)
    if not auth:
        raise Unauthorized('Authorization header is expected')
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise Unauthorized('Authorization header must start with Bearer')
    elif len(parts) == 1:
        raise Unauthorized('Token not found')
    elif len(parts) > 2:
        raise Unauthorized('Authorization header must be Bearer + \s + token')

    return parts[1]


def authenticate_user(token):
    """
    Authenticate and return user from JSON Web Token.

    Raises :class:`werkzeug.exceptions.Unauthorized` if token is invalid.

    :param token: JWT
    :type token: str
    :return: user
    :rtype: dict
    """
    client_id = core.app.flask_app.config['AUTH_CLIENT_ID']
    client_secret = core.app.flask_app.config['AUTH_CLIENT_SECRET']
    try:
        payload = jwt.decode(
            token,
            base64.b64decode(client_secret.replace("_", "/").replace("-", "+")),
            audience=client_id
        )
    except jwt.ExpiredSignature:
        raise Unauthorized('Token is expired')
    except jwt.InvalidAudienceError:
        raise Unauthorized('Incorrect audience')
    except jwt.DecodeError:
        raise Unauthorized('Token signature is invalid')
    except jwt.InvalidTokenError:
        raise Unauthorized('Token invalid')

    return payload
