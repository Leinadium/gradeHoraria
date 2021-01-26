from flask import render_template

from . import home

from .. import scheduler


@home.route('/')
def homepage():
    """
    Render the homepage template on the /route
    """
    return render_template('home/index.html', title="Home")


@home.route('/about')
def about():
    """
    Render the about template on the /route
    """
    return render_template('home/about.html', title='About')
