from flask import Blueprint

criar = Blueprint('criar', __name__)

from . import views
