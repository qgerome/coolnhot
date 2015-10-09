from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from coolnhot.factory import create_app
from coolnhot.extensions import db
from coolnhot.manage import MeasureCommand, database

app = create_app(__name__)
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)
manager.add_command('measure', MeasureCommand)
manager.add_command('db', database.manager)


if __name__ == '__main__':
    manager.run()
