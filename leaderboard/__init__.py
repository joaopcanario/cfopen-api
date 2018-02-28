from .app import create_app, config_swagger, init_celery

from . import extensions
from . import tasks
from . import celeryconfig

version = '1.0.0'

__all__ = ['create_app', 'config_swagger', 'init_celery', 'version',
           'extensions', 'tasks', 'celeryconfig']
