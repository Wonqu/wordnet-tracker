import logging
import os

from flask import Flask, render_template, url_for
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_login import login_manager
from werkzeug.contrib.fixers import ProxyFix

from tracker.blueprints.tracker_admin.models import AdminQuery
from tracker.blueprints.tracker_admin.views import AdminIndexView, AdminQueryView
from tracker.blueprints.user.models import User

from tracker.extensions import (
    debug_toolbar,
    db,
    login_manager,
    limiter,
    csrf
)

blueprints_to_import = [
    "tracker_admin",
    "page",
    "synset",
    "sense",
    "emotion",
    "user",
]


def create_app(settings_override=None):
    app = __create_app(settings_override)
    db.create_all(app=app)
    from tracker.celery import celery  # called to run celery setup correctly
    register_blueprints(app)
    register_admin(app)
    return app


def create_app_celery(setting_override=None):
    # blueprints can not be registered for celery before the object gets created,
    # as register_blueprints makes use of .tasks.py files, so it is necessary to first
    # create the app, then create celery, then finally register apps
    return __create_app(setting_override)


def register_blueprints(app):
    for bp in blueprints_to_import:
        # same meaning as for example
        # import tracker.blueprints.page
        # but automates and makes it easier to keep list of registered apps in one place
        imported = __import__('tracker.blueprints.{}'.format(bp), fromlist=[bp])
        app.logger.info("Importing blueprint: %s", bp)
        # get blueprint object by name
        app.register_blueprint(getattr(imported, bp))


def register_admin(app):
    with app.app_context():

        admin = Admin(
            app,
            name='Admin Panel',
            template_mode='bootstrap3',
            endpoint='admin',
            index_view=AdminIndexView()
        )
        app.logger.debug("Ok!")
        admin.add_link(MenuLink(name='Tracker Home', url=url_for('page.home')))
        admin.add_view(AdminQueryView(AdminQuery, db.session, category='Models'))


def __create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    # config
    app = Flask(__name__, instance_relative_config=True)
    config_file = os.environ['TRACKER_CONFIG_FILE']
    app.config.from_object('config.{}'.format(config_file))
    app.config.from_pyfile('{}.py'.format(config_file), silent=True)

    # logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    if settings_override:
        app.config.update(settings_override)

    # application
    __middleware(app)
    __error_templates(app)
    __extensions(app)
    __authentication(User)

    if app.debug:
        pass
        # for some reason does not work
        # app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
        # lessc(app).cssify('tracker/static/styles/main.less')
    return app


def __extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    return None


def __authentication(user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)


def __middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def __error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404, 429, 500]:
        app.errorhandler(error)(render_status)

    return None
