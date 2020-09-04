from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from freshpicks.commands import create_tables

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = 'customers.login'
login_manager.login_message_category = 'alert-warning'


def create_app(config_file='settings.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    db.init_app(app)
    login_manager.init_app(app)

    from freshpicks.main.routes import main
    from freshpicks.customers.routes import customers
    from freshpicks.admins.routes import admins

    app.register_blueprint(main)
    app.register_blueprint(customers)
    app.register_blueprint(admins)
    app.cli.add_command(create_tables)

    return app
