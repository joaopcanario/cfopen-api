from decouple import config


cfg = {
    # Configuration file of api project. This file is loaded as a dict object
    # and will update the config of flask app
    'DEBUG': config('DEBUG', cast=bool),
    'TESTING': config('TESTING', cast=bool),

    ## Test Data
    'DATA_FOLDER': config('DATA_FOLDER'),

    # Celery
    'CELERY_BROKER_URL':  config('CELERY_BROKER_URL'),
    'CELERY_RESULT_BACKEND':  config('CELERY_RESULT_BACKEND'),
    'CELERY_TIMEZONE':  config('CELERY_TIMEZONE'),

    ## MongoDB
    'MONGO_DBNAME': config('MONGO_DBNAME'),
    'MONGO_URI': config('MONGO_URI'),

    ## Security
    # This is the secret key that is used for session signing.
    # You can generate a secure key with os.urandom(24)
    'SECRET_KEY': config('SECRET_KEY'),

    ## Protection against form post fraud
    # You can generate the WTF_CSRF_SECRET_KEY the same way as you have
    # generated the SECRET_KEY. If no WTF_CSRF_SECRET_KEY is provided, it will
    # use the SECRET_KEY.
    'WTF_CSRF_ENABLED': config('WTF_CSRF_ENABLED', cast=bool),
    'WTF_CSRF_SECRET_KEY': config('WTF_CSRF_SECRET_KEY'),
}