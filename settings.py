import os

BROKER_URL                 = os.environ["CLOUDAMQP_URL"]
CELERY_RESULT_BACKEND      = 'db+' + os.environ["DATABASE_URL"]
CELERYD_CONCURRENCY        = 1
CELERY_ACCEPT_CONTENT      = ['json']
CELERY_TASK_SERIALIZER     = 'json'
CELERY_RESULT_SERIALIZER   = 'json'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_IMPORTS             = ['tasks']

DATABASE_URL               = os.environ["DATABASE_URL"]
