from tornado.web import RequestHandler
from config.settings import SESSION_COOKIE_NAME


class BaseHandler(RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie(SESSION_COOKIE_NAME)
