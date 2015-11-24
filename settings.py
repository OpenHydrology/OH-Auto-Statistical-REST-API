import os

BROKER_URL                 = os.environ["REDIS_URL"]
CELERY_RESULT_BACKEND      = 'db+' + os.environ["DATABASE_URL"]
CELERY_ACCEPT_CONTENT      = ['json']
CELERY_TASK_SERIALIZER     = 'json'
CELERY_RESULT_SERIALIZER   = 'json'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_IMPORTS             = ['tasks']

DATABASE_URL               = os.environ["DATABASE_URL"]
