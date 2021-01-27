# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler

# local imports
from config import app_config
from . import scraper

# db variable initialization
db = SQLAlchemy()

# scheduler
scheduler = BackgroundScheduler()


# scheduling the scraper for each day

@scheduler.scheduled_job('cron', id='job_scraper', hour=0)
def run_scraper():
    scraper.run()
    scraper.update_database()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    Bootstrap(app)
    db.init_app(app)
    migrate = Migrate(app, db)

    from app import models

    from .criar import criar as create_blueprint
    app.register_blueprint(create_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .resultado import resultado as resultado_blueprint
    app.register_blueprint(resultado_blueprint)

    scheduler.start()

    return app
