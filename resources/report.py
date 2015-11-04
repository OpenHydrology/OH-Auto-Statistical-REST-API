# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import Response, url_for, abort
import core


class AnalysisRes(Resource):
    def post(self):
        """Schedule an analysis task"""
        task = core.tasks.do_analysis.delay()
        # Accept task and provide status URL
        return None, 202, {'Location': url_for('analyses_status', task_id=task.id)}

    def get(self, task_id):
        """Return the results of the analysis task"""
        task = core.tasks.do_analysis.AsyncResult(task_id)
        try:
            report_text = task.info['result']
            return Response(report_text, mimetype='text/plain')
        except KeyError:
            # If there's no result, analysis is still running
            abort(404)


class AnalysisStatusRes(Resource):
    def get(self, task_id):
        """Return the status of the analyses task. Redirect to task results when finished."""
        task = core.tasks.do_analysis.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'message': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'message': task.info.get('message', '')
            }
            if 'result' in task.info:
                # Redirect to analysis task results
                return None, 303, {'Location': url_for('analyses_get', task_id=task.id)}
        else:
            response = {
                'state': task.state,
                'message': "Error: {}".format(task.info),
            }
        return response

