# -*- coding: utf-8 -*-

from flask_restful import Resource


class Report(Resource):
    def get(self, catchment_id):
        return {'id': catchment_id}
