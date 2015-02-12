import tornado.web

from tornado import gen


class LoginHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        self.render('login.html')

    @gen.coroutine
    def post(self):
        self.write('Hello :D')
