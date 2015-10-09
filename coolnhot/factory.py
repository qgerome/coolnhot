from flask import Flask
from extensions import db

class CoolnHotApp(Flask):
    pass


def create_app(name, config=None):
    app = CoolnHotApp(name)
    app.config.from_object('coolnhot.settings')
    if config:
        app.config.from_object(config)
    app.config.from_envvar('APPLICATION_SETTINGS', silent=True)

    db.init_app(app)

    return app
