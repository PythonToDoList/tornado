import os
from sqlalchemy import create_engine
from tornado_todo.models import Base


def main():
    engine = create_engine(os.environ.get('DATABASE_URL'))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


"""to interact with the database in the command line...

from tornado_todo.models import Profile
from tornado_sqlalchemy import SessionFactory
import os

session = SessionFactory(os.environ.get('DATABASE_URL')).make_session()
session.query(Profile).all()
"""
