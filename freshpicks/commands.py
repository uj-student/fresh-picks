import click
from flask.cli import with_appcontext

from freshpicks import db
from freshpicks.databaseModels import Customers, AdminUsers, Products, Orders, Messages

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()