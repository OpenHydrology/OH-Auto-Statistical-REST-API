# -*- coding: utf-8 -*-

import auth
from flask_restful import Resource


class DataImportRes(Resource):
    @auth.requires_data_import_token
    def post(self):
        return '', 202
