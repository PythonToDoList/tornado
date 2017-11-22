import json
import logging
import os
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import options, define
from tornado.web import RequestHandler, Application


define('port', default=8888, help='port to listen on')


class BaseHandler(RequestHandler):

    def prepare(self, *args, **kwargs):
        self.response = dict()

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')


class InfoView(BaseHandler):
    def get(self):
        routes = {
            'info': 'GET /api/v1',
            'register': 'POST /api/v1/accounts',
            'single profile detail': 'GET /api/v1/accounts/<username>',
            'edit profile': 'PUT /api/v1/accounts/<username>',
            'delete profile': 'DELETE /api/v1/accounts/<username>',
            'login': 'POST /api/v1/accounts/login',
            'logout': 'GET /api/v1/accounts/logout',
            "user's tasks": 'GET /api/v1/accounts/<username>/tasks',
            "create task": 'POST /api/v1/accounts/<username>/tasks',
            "task detail": 'GET /api/v1/accounts/<username>/tasks/<id>',
            "task update": 'PUT /api/v1/accounts/<username>/tasks/<id>',
            "delete task": 'DELETE /api/v1/accounts/<username>/tasks/<id>'
        }
        self.write(json.dumps(routes))


def main():
    app = Application([
        (r'/api/v1', InfoView)
    ], **options.group_dict('application'))
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    logging.info('Listening on http://localhost:%d' % options.port)
    IOLoop.current().start()

if __name__ == '__main__':
    main()
