# -*- coding: utf-8 -*-

# OH Auto Statistical web API
# Copyright (C) 2015  Florenz A. P. Hollebrandse
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import Flask, g
from flask_restful import Api
from resources.report import AnalysisRes, AnalysisStatusRes
from resources.catchment import CatchmentListRes, CatchmentRes
from floodestimation import db


app = Flask(__name__)
api = Api(app)
app.config.from_object('settings')


@app.before_request
def before_request():
    g.db_session = db.Session()


@app.teardown_request
def teardown_request(exception):
    db_session = getattr(g, 'db_session', None)
    if db_session is not None:
        db_session.close()


api.add_resource(AnalysisRes,       '/api/v0/analyses/', endpoint='analyses_post')
api.add_resource(AnalysisRes,       '/api/v0/analyses/<int:catchment_id>')
api.add_resource(AnalysisStatusRes, '/api/v0/analyses_status/<task_id>', endpoint='analyses_status')
api.add_resource(CatchmentListRes,  '/api/v0/catchments/')
api.add_resource(CatchmentRes,      '/api/v0/catchments/<int:catchment_id>')

if __name__ == '__main__':
    app.run(debug=True)
