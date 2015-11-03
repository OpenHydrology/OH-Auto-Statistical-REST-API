# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import Response


class AnalysisRes(Resource):
    def post(self):
        return None, 202, {'Location': '/api/v0/analyses_queue/12345'}

    def get(self, catchment_id):
        return Response("hello", mimetype='text/plain')


class AnalysisQueueRes(Resource):
    def get(self, queue_id):
        finished = True
        if finished:
            return None, 303, {'Location': '/api/v0/analyses/8001'}
        else:
            return {'status': 'pending'}
