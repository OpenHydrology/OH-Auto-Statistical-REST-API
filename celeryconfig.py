import os.path
here = os.path.dirname(__file__)
BROKER_URL = 'sqla+sqlite:///' + os.path.join(here, 'common/celerydb.sqlite')
CELERY_RESULT_BACKEND = 'db+sqlite:///'+ os.path.join(here, 'common/results.sqlite')
CELERY_IGNORE_RESULT = False
CELERY_RESULT_ENGINE_OPTIONS = {'echo': True}