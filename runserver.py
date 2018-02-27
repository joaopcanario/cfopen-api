#!/usr/bin/env python

from flasgger import Swagger

from leaderboard.extensions import celery
from leaderboard import create_app, init_celery, config_swagger

# Create App
app = create_app()

# Init celery
init_celery(app)

# Config Swagger
Swagger(config_swagger(app))

if __name__ == "__main__":
    app.run(debug=True)
