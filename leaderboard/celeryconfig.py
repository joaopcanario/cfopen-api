from celery.schedules import crontab

CELERY_IMPORTS = ('leaderboard.tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


CELERYBEAT_SCHEDULE = {
    'refresh_leaderboards': {
        'task': 'leaderboard.tasks.refresh_boards',
        # Every minute
        'schedule': crontab(minute=0, hour=0),
    }
}
