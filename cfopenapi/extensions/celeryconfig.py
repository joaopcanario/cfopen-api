from celery.schedules import crontab

CELERY_IMPORTS = ('cfopenapi.tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


CELERYBEAT_SCHEDULE = {
    'refresh_leaderboards': {
        'task': 'cfopenapi.tasks.refresh_boards',
        'schedule': crontab(minute='0', hour='*/4'),
    },
    'refresh_cfba_leaderboards': {
        'task': 'cfopenapi.tasks.refresh_cfbaboards',
        'schedule': crontab(minute='0', hour='*/1'),
    }
}
