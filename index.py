import tornado.ioloop
import config
import logging


logging.basicConfig(**config.settings.LOG_SETTINGS)
log = logging.getLogger('main')

application = tornado.web.Application(config.routes)

if __name__ == "__main__":
    log.info('Starting server...')
    port = config.settings.PORT
    application.listen(port)
    log.info('Server started. Listening on port {}'.format(port))
    tornado.ioloop.IOLoop.instance().start()
