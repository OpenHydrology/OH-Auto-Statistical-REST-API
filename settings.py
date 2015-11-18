import os
import appdirs
here = os.path.dirname(__file__)
data_folder = appdirs.user_data_dir('autostatistical', 'Open Hydrology')

BROKER_URL                    = os.environ["CLOUDAMQP_URL"]
#BROKER_URL                   = 'sqla+sqlite:///' + os.path.join(data_folder, 'work', 'message_queue.sqlite')
CELERY_RESULT_BACKEND         = 'db+' + os.environ["DATABASE_URL"]
#CELERY_RESULT_BACKEND        =   'db+sqlite:///' + os.path.join(data_folder, 'work', 'results.sqlite')
#CELERY_IGNORE_RESULT         = False
#CELERY_RESULT_ENGINE_OPTIONS = {'echo': True}
CELERYD_CONCURRENCY           = 1
CELERY_ACCEPT_CONTENT         = ['json']
CELERY_TASK_SERIALIZER        = 'json'
CELERY_RESULT_SERIALIZER      = 'json'
CELERY_DISABLE_RATE_LIMITS    = True
CELERY_IMPORTS                = ['tasks']
