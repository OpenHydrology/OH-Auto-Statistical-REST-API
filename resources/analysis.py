# -*- coding: utf-8 -*-

import os.path
from flask_restful import Resource
from flask import Response, url_for, request
import core
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.utils import redirect


class AnalysisRes(Resource):
    def post(self):
        """
        Schedule an analysis task

        Requires a catchment file (.cd3 or .xml) to be posted, and optionally an AMAX file (.am).
        """
        try:
            catchment_id = int(request.form['nrfa-id'])
            task = core.tasks.do_analysis_from_id.delay(catchment_id)
        except (KeyError, ValueError):
            files = list(f for f in request.files.values() if f)  # filter out empty file input fields
            if len(files) < 1:
                raise BadRequest("Catchment file (.cd3 or .xml) required.")
            elif len(files) > 2:
                raise BadRequest("Too many files supplied.")
            else:
                try:
                    catchment_file = [f for f in files
                                      if os.path.splitext(f.filename)[1].lower() in ['.cd3', '.xml']][0]
                except IndexError:
                    raise BadRequest("Catchment file (.cd3 or .xml) required.")
                amax_file = None
                if len(files) == 2:
                    try:
                        amax_file = [f for f in files
                                     if os.path.splitext(f.filename)[1].lower() == '.am'][0]
                    except IndexError:
                        raise BadRequest("Second file must be AMAX (.am) file.")

            catchment_str = catchment_file.read().decode('utf-8').replace('\r\n', '\n')
            amax_str = amax_file.read().decode('utf-8').replace('\r\n', '\n') if amax_file else None
            task = core.tasks.do_analysis.delay(catchment_str, amax_str=amax_str)

        # Return status URL
        return '', 202, {'Location': url_for('analysis_status', _external=True, _scheme='https', task_id=task.id)}

    def get(self, task_id):
        """Return the results of the analysis task"""
        task = core.tasks.do_analysis.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            report_text = task.info['result']
            return Response(report_text, mimetype='text/plain')
        else:
            raise NotFound("Analysis does not exist.")


class AnalysisStatusRes(Resource):
    def get(self, task_id):
        """Return the status of the analyses task. Redirect to task results when finished."""
        task = core.tasks.do_analysis.AsyncResult(task_id)

        if task.state == 'PENDING':
            return {'state': task.state, 'message': ''}
        elif task.state != 'FAILURE':
            if 'result' in task.info:
                # Redirect to analysis task results
                return redirect(url_for('get_analysis', _external=True, _scheme='https', task_id=task.id),
                                code=303)
            else:
                return {'state': task.state, 'message': task.info.get('message', '')},
        else:
            return {'state': task.state, 'message': '', }
