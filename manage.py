from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from coolnhot.factory import create_app
from coolnhot.extensions import db

app = create_app(__name__)
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
