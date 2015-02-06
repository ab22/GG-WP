import tornado.web
from tornado import gen


class MainHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        self.render('index.html', title='You Rage You Lose')
