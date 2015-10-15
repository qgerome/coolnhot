# DEBUG = True
SQLALCHEMY_DATABASE_URI = ""
SECRET_KEY = "CHANGEME"
SENSOR_DEBUG = False

LOGGING_CONFIG = {
	'version': 1,
	'formatters': {
	'long': {
	'format': '%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s'},
	'short': {'format': '%(message)s'}},
	'handlers': {
		'default': {
			'level': 'INFO',
			'class': 'logging.StreamHandler',
		},
		'console': {
			'class': 'logging.StreamHandler',
			'formatter': 'short',
			'stream': 'ext:sys.stdout'
		},
		'file': {
			'class': 'logging.handlers.RotatingFileHandler',
			'formatter': 'long',
			'filename': 'sample_app.log', 'maxBytes': 16384, 'backupCount': 5
		}
	},
	'loggers': {
		'': {
			'level': 'INFO',
			'handlers': ['default']
		},
		'coolnhot': {
			'level': 'DEBUG',
		    'propagate': True
		},
		'sqlalchemy.engine': {
			'propagate': True
		},
	    'werkzeug': {
			'propagate': True}
	},
}