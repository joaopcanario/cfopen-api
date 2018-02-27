web: gunicorn wsgi:app --bind 0.0.0.0:$PORT
worker: celery worker -A wsgi.celery --beat --loglevel=info