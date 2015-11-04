web: gunicorn core:app.flask_app --log-file -
worker: celery -A core.celery worker -l info
