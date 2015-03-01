from tornado.web import RequestHandler
from config.settings import SESSION_COOKIE_NAME


class AuthHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie(SESSION_COOKIE_NAME)


class JsonHandler(RequestHandler):
    def prepare(self):
        self.set_header("Content-Type", "application/json")
