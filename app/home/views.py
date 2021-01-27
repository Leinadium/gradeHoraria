from flask import render_template, redirect, url_for

from . import home

from .. import run_scraper


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


@home.route("/recarregar")
def recarregar():
    run_scraper()

    return redirect(url_for('home.homepage'))
