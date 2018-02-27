from flask import Flask

from leaderboard.blueprints import debug, cfopen, core
from leaderboard.extensions import celery
from leaderboard import celeryconfig

import leaderboard
import settings


def init_celery(app):
    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def create_app():
    '''App creation'''

    # Initialization
    app = Flask("cfgboard")
    app.config.update(settings.cfg)

    # Register blueprints
    app.register_blueprint(core)
    app.register_blueprint(debug, url_prefix='/api/v1/debug')
    app.register_blueprint(cfopen, url_prefix='/api/v1/open')

    return app


def config_swagger(app):
    '''Swagger configuration'''

    specs_description = open('docs/specs_description.yml', 'r')

    app.config['SWAGGER'] = {
        "version": "2.0",
        "title": "Reebok CrossFit Games - Open Custom Leaderboard",
        "schemes": ["http"],
        "consumes": ["application/json", "multipart/form-data"],
        "produces": ["application/json"],
        "specs": [{"version": leaderboard.version,
                   "title": "API Spec v" + leaderboard.version,
                   "endpoint": 'spec',
                   "route": '/spec',
                   "description": specs_description.read()}]}

    return app
