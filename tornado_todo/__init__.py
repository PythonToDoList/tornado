"""Main configuration for application."""
import logging
import os

from tornado_todo.views import (
    InfoView,
    ProfileView,
    RegistrationView,
    TaskListView,
    TaskView
)

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import options, define
from tornado_sqlalchemy import make_session_factory
from tornado.web import Application


define('port', default=8888, help='port to listen on')
factory = make_session_factory(os.environ.get(
    'DATABASE_URL',
    'postgres://localhost:5432/tornado_todo'
))


def main():
    """Construct and serve the application."""
    api_root = '/api/v1'
    app = Application([
        (api_root, InfoView),
        (api_root + r'/accounts', RegistrationView),
        (api_root + r'/accounts/([\w]+)', ProfileView),
        (api_root + r'/accounts/([\w]+)/tasks', TaskListView),
        (api_root + r'/accounts/([\w]+)/tasks/([\d]+)', TaskView),
    ],
        **options.group_dict('application'),
        session_factory=factory
    )
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    logging.info('Listening on http://localhost:%d' % options.port)
    IOLoop.current().start()
