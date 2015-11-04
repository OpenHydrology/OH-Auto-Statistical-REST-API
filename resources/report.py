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
        files = list(request.files.values())
        if len(files) < 1:
            return {'error': "Catchment file (.cd3 or .xml) required."}, 400
        elif len(files) > 2:
            return {'error': "Too many files supplied."}, 400
        else:
            catchment_file = [f for f in files if os.path.splitext(f.filename)[1].lower() in ['.cd3', '.xml']][0]
            catchment_ext = os.path.splitext(catchment_file.filename)[1].lower()
            amax_file = None
            if not catchment_file:
                return {'error': "Catchment file (.cd3 or .xml) required."}, 400
            if len(files) == 2:
                amax_file = [f for f in files if os.path.splitext(f.filename)[1].lower() == '.am'][0]
                if not amax_file:
                    return {'error': "Second file must AMAX (.am) file."}, 400

        # Save input files to a working folder
        work_folder = tempfile.mkdtemp(dir=core.app.flask_app.config['ANALYSIS_FOLDER'])
        catchment_file.save(os.path.join(work_folder, 'catchment' + catchment_ext))
        if amax_file:
            amax_file.save(os.path.join(work_folder, 'catchment.am'))

        # Task will pick up files from working folder
        task = core.tasks.do_analysis.delay(work_folder)

        # Return status URL
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

