"""View classes for the todo list."""
import json

from passlib.hash import pbkdf2_sha256 as hasher

from tornado_todo.models import Profile, Task

from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin, as_future


class BaseHandler(RequestHandler, SessionMixin):
    """Base request handler for all upcoming views."""

    def prepare(self, *args, **kwargs):
        """Set up some attributes before any method receives the request."""
        self.form_data = self._convert_to_unicode(self.request.arguments)
        self.response = {}

    def set_default_headers(self):
        """Set the default response header to be JSON."""
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    def send_response(self, data, status=200):
        """Construct and send a JSON response with appropriate status code."""
        self.set_status(status)
        self.write(json.dumps(data))

    def _convert_to_unicode(self, data_dict):
        """Convert the incoming data dictionary to have unicode values."""
        output = {key: [val.decode('utf8') for val in val_list] for key, val_list in data_dict.items()}
        return output


class InfoView(BaseHandler):
    """Simple view to return route information."""

    def get(self):
        """Handle a GET request for route information."""
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
    """View for registering a new user."""

    @coroutine
    def post(self):
        """Handle a POST request for user registration."""
        needed = ['username', 'email', 'password', 'password2']
        if all([key in self.form_data for key in needed]):
            username = self.form_data['username'][0]
            with self.make_session() as session:
                profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
                if not profile:
                    if self.form_data['password'] == self.form_data['password2']:
                        self.build_profile(session)
                    self.send_response({'msg': 'Profile created'}, status=201)

    def build_profile(self, session):
        """Create new profile using information from incoming request."""
        hashed_password = hasher.hash(self.form_data['password'][0])
        new_profile = Profile(
            username=self.form_data['username'][0],
            password=hashed_password,
            email=self.form_data['email'][0]
        )
        session.add(new_profile)
        session.commit()


class ProfileView(BaseHandler):
    """View for reading or modifying an existing profile."""

    @coroutine
    def get(self, username):
        """Handle incoming get request for a specific user's profile."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                self.send_response(profile.to_dict())
            else:
                self.send_response({'error': 'You do not have permission to access this profile.'}, status=403)

    @coroutine
    def put(self, username):
        """Handle incoming put request to update a specific profile."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                if 'username' in self.form_data:
                    profile.username = self.form_data['username'][0]
                if 'password' in self.form_data and 'password2' in self.form_data and self.form_data['password'] == self.form_data['password2'] and self.form_data['password'][0] != '':
                    profile.password = hasher.hash(self.form_data['password'][0])
                if 'email' in self.form_data:
                    profile.email = self.form_data['email'][0]
                session.add(profile)
                session.commit()
                self.send_response({
                    'msg': 'Profile updated.',
                    'profile': profile.to_dict(),
                    'username': profile.username
                }, status=202)
            else:
                self.send_response({'error': 'You do not have permission to access this profile.'}, status=403)

    @coroutine
    def delete(self, username):
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            session.delete(profile)
            session.commit()
            self.send_response({}, status=204)


class TaskListView(BaseHandler):

    @coroutine
    def get(self, username):
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                tasks = yield as_future(session.query(Task).all)

            else:
                self.send_response({'error': 'You do not have permission to access this profile.'}, status=403)


    @coroutine
    def post(self, username):
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                pass
            else:
                self.send_response({'error': 'You do not have permission to access this profile.'}, status=403)



class TaskView(BaseHandler):

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
