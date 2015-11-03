# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import Response, url_for
from common.tasks import long_task


class AnalysisRes(Resource):
    def post(self):
        task = long_task.delay()
        return None, 202, {'Location': url_for('analyses_status', task_id=task.id)}

    def get(self, catchment_id):
        return Response("hello", mimetype='text/plain')


class AnalysisStatusRes(Resource):
    def get(self, task_id):
        task = long_task.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),  # this is the exception raised
            }
        return response

# class AnalysisQueueRes(Resource):
#     def get(self, queue_id):
#         finished = True
#         if finished:
#             return None, 303, {'Location': '/api/v0/analyses/8001'}
#         else:
#             return {'status': 'pending'}
