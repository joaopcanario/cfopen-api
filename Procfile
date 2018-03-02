web: gunicorn cfopenapi.wsgi:app
worker: celery worker -A cfopenapi.wsgi.celery --beat --loglevel=info