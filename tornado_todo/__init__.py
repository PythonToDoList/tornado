import logging
import os

from tornado_todo.views import InfoView

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
    app = Application([
        (r'/api/v1', InfoView)
    ],
        **options.group_dict('application'),
        session_factory=factory
    )
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    logging.info('Listening on http://localhost:%d' % options.port)
    IOLoop.current().start()
