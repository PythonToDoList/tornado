import json

from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado_sqlalchemy import (
    SessionMixin,
    as_future
)


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


class RegistrationView(BaseHandler):

    def post(self):
        pass


class ProfileView(BaseHandler):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


class LoginView(BaseHandler):

    def post(self):
        pass


class LogoutView(BaseHandler):

    def get(self):
        pass


class TaskListView(BaseHandler):

    def get(self):
        pass

    def post(self):
        pass


class TaskView(BaseHandler):

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass
