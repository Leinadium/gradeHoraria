# run.py

import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

# RUN WITH gunicorn -workers=4 run_gunicorn:app
