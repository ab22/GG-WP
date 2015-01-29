import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        data = {
            'key': 'value',
            'Ab': 'Mendoza'
        }
        self.write(data)
