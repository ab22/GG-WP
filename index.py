import tornado.ioloop
import config


application = tornado.web.Application(config.routes)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
