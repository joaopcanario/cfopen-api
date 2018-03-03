from flask import Flask

from .blueprints import debug, cfopen, core
from .extensions import celery, celeryconfig

from . import settings
from . import tasks


version = '1.0.0'


def _init_celery(app):
    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def _config_swagger(app):
    '''Swagger configuration'''

    specs_description = open('docs/specs_description.yml', 'r')

    app.config['SWAGGER'] = {
        "version": "2.0",
        "title": "Reebok CrossFit Games - Open Custom Leaderboard",
        "specs": [{
            "version": version,
            "title": f"API Spec v{version}",
            "endpoint": 'spec',
            "route": '/spec',
            "description": specs_description.read()
        }]
    }

    return app


def create_app(in_celery=False, in_swagger=False):
    '''App creation'''

    # Initialization
    app = Flask("cfgboard")
    app.config.update(settings.cfg)

    # Register blueprints
    app.register_blueprint(core)
    app.register_blueprint(debug, url_prefix='/api/v1/debug')
    app.register_blueprint(cfopen, url_prefix='/api/v1/open')

    if in_swagger:
        _init_celery(app)

    if in_swagger:
        from flasgger import Swagger

        app = _config_swagger(app)
        Swagger(app)

    app.app_context().push()

    return app
