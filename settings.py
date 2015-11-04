import os.path
here = os.path.dirname(__file__)

BROKER_URL                    = 'sqla+sqlite:///' + os.path.join(here, 'message_queue.sqlite')
CELERY_RESULT_BACKEND         = 'db+sqlite:///'   + os.path.join(here, 'results.sqlite')
#CELERY_IGNORE_RESULT         = False
#CELERY_RESULT_ENGINE_OPTIONS = {'echo': True}
CELERYD_CONCURRENCY           = 1
CELERY_ACCEPT_CONTENT         = ['json']
CELERY_TASK_SERIALIZER        = 'json'
CELERY_RESULT_SERIALIZER      = 'json'
CELERY_DISABLE_RATE_LIMITS    = True
CELERY_IMPORTS                = ['tasks']