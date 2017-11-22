"""For initializing a new database."""
import os
from sqlalchemy import create_engine
from tornado_todo.models import Base


def main():
    """Tear down existing tables and create new ones."""
    engine = create_engine(os.environ.get('DATABASE_URL'))
    if bool(os.environ.get('DEBUG', 'True')):
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


"""to interact with the database in the command line...

from tornado_todo.models import Profile
from tornado_sqlalchemy import SessionFactory
import os

session = SessionFactory(os.environ.get('DATABASE_URL')).make_session()
session.query(Profile).all()
"""
