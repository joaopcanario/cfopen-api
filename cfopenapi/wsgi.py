# Load celery
from . import celery, create_app

from flasgger import Swagger

# Create App
app = create_app(in_celery=True, in_swagger=True)
Swagger(app)
