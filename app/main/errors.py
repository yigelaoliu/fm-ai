from flask import render_template
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html', e=e), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', e=e), 500
