"""View classes for the todo list."""
from datetime import datetime
import json

from passlib.hash import pbkdf2_sha256 as hasher

from tornado_todo.models import Profile, Task

from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin, as_future


class BaseHandler(RequestHandler, SessionMixin):
    """Base request handler for all upcoming views."""

    def prepare(self):
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

class AuthenticationMixin:
    # todo: extend "prepare" method to include authentication
    def prepare(self):
        authorized = self.get_current_user()
        if authorized:
            super().prepare()
        else:
            self.send_forbidden_response()
            self.finish()

    def get_current_user(self):
        token_cookie = self.get_secure_cookie('auth_token')
        if token_cookie:
            username, token = token_cookie.split(':')
            with self.make_session() as session:
                profile = session.query(Profile).filter(Profile.username == username).first()
                if profile and profile.token == token:
                    return True

    def authenticate_response(self, profile):
        token_cookie = f"{profile.username}:{profile.token}"
        self.set_secure_cookie('auth_token', token_cookie)

    def send_forbidden_response(self):
        data = {'error': 'You do not have permission to access this profile.'}
        self.set_status(403)
        self.write(json.dumps(data))


class InfoView(BaseHandler):
    """Simple view to return route information."""
    SUPPORTED_METHODS = ("GET",)

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
    SUPPORTED_METHODS = ("POST",)

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
                    else:
                        self.send_response({'error': "Passwords don't match"}, status=400)

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


class ProfileView(AuthenticationMixin, BaseHandler):
    """View for reading or modifying an existing profile."""
    SUPPORTED_METHODS = ("GET", "PUT", "DELETE")

    @coroutine
    def get(self, username):
        """Handle incoming get request for a specific user's profile."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                self.authenticate_response(profile)
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
                self.authenticate_response(profile)
                self.send_response({
                    'msg': 'Profile updated.',
                    'profile': profile.to_dict(),
                    'username': profile.username
                }, status=202)
            else:
                self.send_response({'error': 'You do not have permission to access this profile.'}, status=403)

    @coroutine
    def delete(self, username):
        """Delete an existing task from the database."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            session.delete(profile)
            session.commit()
            self.send_response({}, status=204)


class TaskListView(AuthenticationMixin, BaseHandler):
    """View for reading and adding new tasks."""
    SUPPORTED_METHODS = ("GET", "POST",)

    @coroutine
    def get(self, username):
        """Get all tasks for an existing user."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                tasks = [task.to_dict() for task in profile.tasks]
                self.authenticate_response(profile)
                self.send_response({
                    'username': profile.username,
                    'tasks': tasks
                })
            else:
                self.send_response({'error': 'The profile does not exist'}, status=404)

    @coroutine
    def post(self, username):
        """Create a new task."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                due_date = self.form_data['due_date'][0]
                try:
                    task = Task(
                        name=self.form_data['name'][0],
                        note=self.form_data['note'][0],
                        creation_date=datetime.now(),
                        due_date=datetime.strptime(due_date, '%d/%m/%Y %H:%M:%S') if due_date else None,
                        completed=self.form_data['completed'][0],
                        profile_id=profile.id,
                        profile=profile
                    )
                    session.add(task)
                    session.commit()
                    self.authenticate_response(profile)
                    self.send_response({'msg': 'posted'}, status=201)
                except KeyError:
                    self.authenticate_response(profile)
                    self.send_response({'error': 'Some fields are missing'}, 400)
            else:
                self.send_response({'error': 'You do not have permission to access this profile.'}, status=404)


class TaskView(AuthenticationMixin, BaseHandler):
    """Request handling methods for an individual task."""
    SUPPORTED_METHODS = ("GET", "PUT", "DELETE")

    def get(self, username, task_id):
        """Get detail for an existing task given a username and task id."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                task = yield as_future(session.query(Task).filter(Task.profile == profile).get(task_id))
                if task:
                    self.authenticate_response(profile)
                    self.send_response({'username': username, 'task': task.to_dict()})
                else:
                    self.authenticate_response(profile)
                    self.send_response({'username': username, 'task': None}, status=404)
            else:
                self.send_response({'error': 'You do not have permission to access this data.'}, status=403)

    def put(self, username, task_id):
        """Update an existing task given a username and task id."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                task = yield as_future(session.query(Task).filter(Task.profile == profile).get(task_id))
                if task:
                    self.authenticate_response(profile)
                    self.send_response({'username': username, 'task': task.to_dict()})
                else:
                    self.authenticate_response(profile)
                    self.send_response({'username': username, 'task': None}, status=404)
            else:
                self.send_response({'error': 'You do not have permission to access this data.'}, status=403)

    def delete(self, username, task_id):
        """Delete an existing task given a username and task id."""
        with self.make_session() as session:
            profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
            if profile:
                task = yield as_future(session.query(Task).filter(Task.profile == profile).get(task_id))
                if task:
                    session.delete(task)
                    session.commit()
                self.authenticate_response(profile)
                self.send_response({'username': username, 'msg': 'Deleted.'})
            else:
                self.send_response({'error': 'You do not have permission to access this data.'}, status=403)


class LoginView(BaseHandler):
    """View for logging in."""
    SUPPORTED_METHODS = ("POST",)

    def post(self):
        """Log a user in."""
        needed = ['username', 'password']
        if all([key in self.form_data for key in needed]):
            with self.make_session() as session:
                profile = yield as_future(session.query(Profile).filter(Profile.username == username).first)
                if profile and hasher.verify(self.form_data['password'][0], profile.password):
                    self.authenticate_response(profile)
                    self.send_response({'msg': 'Authenticated'})
                else:
                    self.send_response({'error': 'Incorrect username/password combination.'}, status=400)

        else:
            self.send_response({'error': 'Some fields are missing'}, status=400)


class LogoutView(BaseHandler):
    """View for logging out."""
    SUPPORTED_METHODS = ("GET",)

    def get(self):
        """Log a user out."""
        self.send_response({'msg': 'Logged out.'})
