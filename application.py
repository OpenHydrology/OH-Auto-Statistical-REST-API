import flask
import flask_restful
from celery import Celery
from resources.report import AnalysisRes, AnalysisStatusRes
from resources.catchment import CatchmentListRes, CatchmentRes
import floodestimation


class Application(object):

    def __init__(self, config, debug=True):
        self.flask_app = flask.Flask(__name__)
        self.flask_app.config.from_object('settings')

        self.rest_api = flask_restful.Api(self.flask_app)

        self.db = floodestimation.db
        self._set_db_session()

        self.debug = debug
        self._set_routes()

    def _set_routes(self):
        self.rest_api.add_resource(AnalysisRes,       '/api/v0/analyses/', endpoint='analyses_post')
        self.rest_api.add_resource(AnalysisRes,       '/api/v0/analyses/<task_id>', endpoint='analyses_get')
        self.rest_api.add_resource(AnalysisStatusRes, '/api/v0/analyses_status/<task_id>', endpoint='analyses_status')
        self.rest_api.add_resource(CatchmentListRes,  '/api/v0/catchments/')
        self.rest_api.add_resource(CatchmentRes,      '/api/v0/catchments/<int:catchment_id>')

    def _set_db_session(self):
        @self.flask_app.before_request
        def before_request():
            flask.g.db_session = self.db.Session()

        @self.flask_app.teardown_request
        def teardown_request(exception):
            db_session = getattr(flask.g, 'db_session', None)
            if db_session is not None:
                db_session.close()

    def celery(self):
        app = self.flask_app
        celery = Celery(app.import_name)
        celery.conf.update(app.config)

        TaskBase = celery.Task

        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        celery.Task = ContextTask

        return celery

    def start_app(self):
        self.flask_app.run(debug=self.debug)
