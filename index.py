import tornado.ioloop
import config
import logging
import motor


def configure_logger(**kwargs):
    logging.basicConfig(**kwargs)
    return logging.getLogger()


def configure_mongodb(connection):
    host = connection['host']
    port = connection['port']
    db = connection['database']
    client = motor.MotorClient(host, port)

    return (client, client[db])


def main():
    # Get the configuration parameters
    connections = config.settings.CONNECTIONS
    app_port = config.settings.APP_PORT
    logger_settings = config.settings.LOGGER_SETTINGS
    routes = config.ROUTES

    log = configure_logger(**logger_settings)
    client, db = configure_mongodb(connections['mongodb'])

    application = tornado.web.Application(
        routes,
        db=db,
        log=log
    )
    log.info('Starting server...')
    application.listen(app_port)
    log.info('Server started on port {}'.format(app_port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
