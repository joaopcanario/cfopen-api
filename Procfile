web: gunicorn wsgi:app
worker: celery worker -A wsgi.celery --beat --loglevel=info