import json

from passlib.hash import pbkdf2_sha256 as hasher

from tornado_todo.models import Profile

from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado_sqlalchemy import (
    SessionMixin,
    as_future
)


class BaseHandler(RequestHandler, SessionMixin):

    def prepare(self, *args, **kwargs):
        self.form_data = self._convert_to_unicode(self.request.arguments)
        self.response = {}

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def _convert_to_unicode(self, data_dict):
        output = {key: [val.decode('utf8') for val in val_list] for key, val_list in data_dict.items()}
        return output


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

    @coroutine
    def post(self):
        needed = ['username']#, 'email', 'password', 'password2']
        if all([key in self.form_data for key in needed]):
            username = self.form_data['username'][0]
            with self.make_session() as session:
                profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
                if not profile:
                    if self.form_data['password'] == self.form_data['password2']:
                        self.build_profile(session)

                    self.set_status(201)
                    self.write(json.dumps({'msg': 'Profile created'}))

    def build_profile(self, session):
        # hashed_password = yield executor.submit(hasher.hash, self.form_data['password'][0])
        hashed_password = hasher.hash(self.form_data['password'][0])
        new_profile = Profile(
            username=self.form_data['username'][0],
            password=hashed_password,
            email=self.form_data['email'][0]
        )
        session.add(new_profile)
        session.commit()


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
