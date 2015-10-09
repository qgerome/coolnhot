from flask import Flask
from extensions import db, sensor
import settings
import logging
import logging.config


class CoolnHotApp(Flask):
	pass


def create_app(name, config=None):
	app = CoolnHotApp(name)
	app.config.from_object(settings)
	if config:
		app.config.from_object(config)
	app.config.from_pyfile("./localsettings.py")
	app.config.from_envvar('APPLICATION_SETTINGS', silent=True)
	logging.config.dictConfig(app.config.get('LOGGING_CONFIG'))

	db.init_app(app)
	sensor.init_app(app)

	return app
