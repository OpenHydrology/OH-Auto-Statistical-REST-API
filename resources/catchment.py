# -*- coding: utf-8 -*-

from flask import g, abort
from flask_restful import Resource
from floodestimation.entities import Catchment


NRFA_URL = 'http://nrfa.ceh.ac.uk/data/station/info/'


class CatchmentListRes(Resource):
    def get(self):
        catchments = g.db_session.query(Catchment).order_by(Catchment.id).all()
        return [{'id': c.id,
                 'location': c.location,
                 'watercourse': c.watercourse,
                 'x': c.point.x,
                 'y': c.point.y,
                 'is_suitable_for_qmed': c.is_suitable_for_qmed,
                 'is_suitable_for_pooling': c.is_suitable_for_pooling,
                 'url': NRFA_URL + str(c.id)}
                for c in catchments]


class CatchmentRes(Resource):
    def get(self, catchment_id):
        c = g.db_session.query(Catchment).get(catchment_id)
        if c:
            return {'id': c.id,
                    'location': c.location,
                    'watercourse': c.watercourse,
                    'x': c.point.x,
                    'y': c.point.y,
                    'is_suitable_for_qmed': c.is_suitable_for_qmed,
                    'is_suitable_for_pooling': c.is_suitable_for_pooling,
                    'url': NRFA_URL + str(c.id)}
        else:
            abort(404)
