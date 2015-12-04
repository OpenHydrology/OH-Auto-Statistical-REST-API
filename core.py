from application import Application
import settings


app = Application(settings)
db = app.db
celery = app.celery()


import tasks
