# -*- coding: utf-8 -*-

import os.path
import tempfile
from flask_restful import Resource
from flask import Response, url_for, abort, request
import core


class AnalysisRes(Resource):
    def post(self):
        """
        Schedule an analysis task

        Requires a catchment file (.cd3 or .xml) to be posted, and optionally an AMAX file (.am).
        """
        files = list(f for f in request.files.values() if f)  # filter out empty file input fields
        if len(files) < 1:
            return {'message': "Catchment file (.cd3 or .xml) required."}, 400
        elif len(files) > 2:
            return {'message': "Too many files supplied."}, 400
        else:
            try:
                catchment_file = [f for f in files if os.path.splitext(f.filename)[1].lower() in ['.cd3', '.xml']][0]
                catchment_ext = os.path.splitext(catchment_file.filename)[1].lower()
            except IndexError:
                return {'message': "Catchment file (.cd3 or .xml) required."}, 400
            amax_file = None
            if len(files) == 2:
                try:
                    amax_file = [f for f in files if os.path.splitext(f.filename)[1].lower() == '.am'][0]
                except IndexError:
                    return {'message': "Second file must be AMAX (.am) file."}, 400

        catchment_str = catchment_file.read().decode('utf-8')
        amax_str = amax_file.read().decode('utf-8') if amax_file else None
        task = core.tasks.do_analysis.delay(catchment_str, catchment_ext, amax_str=amax_str)

        # Return status URL
        return '', 202, {'Location': url_for('analysis_status', _external=True, _scheme='https', task_id=task.id)}

    def get(self, task_id):
        """Return the results of the analysis task"""
        task = core.tasks.do_analysis.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            report_text = task.info['result']
            return Response(report_text, mimetype='text/plain')
        else:
            return {'message': "Analysis not yet completed."}, 404


class AnalysisStatusRes(Resource):
    def get(self, task_id):
        """Return the status of the analyses task. Redirect to task results when finished."""
        task = core.tasks.do_analysis.AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {'state': task.state, 'message': ''}
        elif task.state != 'FAILURE':
            if 'result' in task.info:
                # Redirect to analysis task results
                response = '', 303, {'Location': url_for('get_analysis', _external=True, _scheme='https',
                                                         task_id=task.id)}
            else:
                response = {'state': task.state, 'message': task.info.get('message', '')}
        else:
            response = {'state': task.state, 'message': '', }
        return response
