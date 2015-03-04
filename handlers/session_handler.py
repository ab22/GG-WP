import utils.async_bcrypt as async_bcrypt

from tornado import gen
from .base_handlers import AuthHandler
from config.settings import SESSION_COOKIE_NAME


class LoginHandler(AuthHandler):
    def set_session_cookies(self, data):
        self.set_secure_cookie(SESSION_COOKIE_NAME, data)

    @gen.coroutine
    def find_user_by_username(self, username):
        db = self.settings['db']
        user = yield db.users.find_one({'username': username})
        return user

    @gen.coroutine
    def get(self):
        self.render('login.html')

    @gen.coroutine
    def post(self):
        username = self.get_body_argument('username', None)
        password = self.get_body_argument('password', None)
        if username is None or password is None:
            self.render('login.html')
            return
        user = yield self.find_user_by_username(username)
        if user is None:
            self.render('login.html')
            return
        match = yield async_bcrypt.compare(user['password'], password)
        if not match:
            self.render('login.html')
            return
        self.set_session_cookies(user['username'])
        self.redirect('/dashboard')
