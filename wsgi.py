from leaderboard.extensions import celery
from leaderboard import create_app, init_celery

# Create App
app = create_app()

# Init celery
init_celery(app)
