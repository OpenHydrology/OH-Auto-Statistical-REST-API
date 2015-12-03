from application import Application
import os

app = Application(os.environ, debug=False)
db = app.db
celery = app.celery()


