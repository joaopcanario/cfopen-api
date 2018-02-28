# Load celery
from leaderboard.extensions import celery
from leaderboard import create_app

from flasgger import Swagger

# Create App
app = create_app(in_celery=True, in_swagger=True)
Swagger(app)
