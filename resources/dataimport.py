# -*- coding: utf-8 -*-

import auth
import flask
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
import core


class DataImportRes(Resource):
    @auth.requires_data_import_token
    def post(self):
        """
        Start a data import task

        JSON body must include `url` key to import data from (zip file)
        """
        data = flask.request.get_json()
        if not data:
            raise BadRequest("Request data must be JSON.")
        try:
            from_url = data['url']
        except KeyError:
            raise BadRequest("JSON body must include `url` key.")
        if not from_url.lower().endswith('.zip'):
            raise BadRequest("Download URL must be a .zip file. `{}` was provided.".format(from_url))

        core.tasks.import_data.delay(from_url)
        return '', 202
