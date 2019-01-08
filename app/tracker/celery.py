from celery import Celery

from tracker.app import blueprints_to_import, create_app_celery, register_blueprints, register_admin

try:
    from flask import current_app
    # it is necessary to use current_app so that it's evaluated properly (as it is lazy)
    # and runs the code that raises RuntimeError in case of app not being started yet
    id(current_app)
    from celery import current_app as celery
except RuntimeError:
    current_app = create_app_celery()
    celery = Celery(
        current_app.import_name,
        include=list(
            map(lambda x: "tracker.blueprints.{}.tasks".format(x), blueprints_to_import)
        ),
    )
    celery.conf.update(current_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with current_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.set_default()
    # registering blueprints must take place when celery is already configured,
    # because views in blueprints might use imported tasks, which requires them to be already defined
    register_blueprints(current_app)
    register_admin(current_app)


if __name__ == '__main__':
    celery.start()
