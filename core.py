from application import Application
import os

app = Application(os.environ, debug=True)
db = app.db
celery = app.celery()


import tasks
