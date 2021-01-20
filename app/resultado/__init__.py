from flask import Blueprint
from . import generator

resultado = Blueprint('resultado', __name__)
grade_generator = generator.run

from . import views
