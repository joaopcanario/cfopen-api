# Load celery
from . import celery, create_app

# Create App
app = create_app(in_celery=True, in_swagger=True)
