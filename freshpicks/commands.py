import click
from flask.cli import with_appcontext


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    from freshpicks import db
    db.create_all()


# db.session.remove()
# db.drop_all()
# db.create_all()
