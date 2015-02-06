import tornado.ioloop
import config
import logging
import motor
import services


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
    # Get config parameters
    settings = config.settings
    debug = settings.DEBUG
    views_path = settings.VIEWS_PATH
    databases = settings.DATABASES
    app_port = settings.APP_PORT
    logger_settings = settings.LOGGER_SETTINGS
    riot_api_key = settings.RIOT_API_KEY
    routes = config.ROUTES

    log = configure_logger(**logger_settings)
    client, db = configure_mongodb(databases['mongodb'])
    services.initialize(db, riot_api_key)

    application = tornado.web.Application(
        routes,
        db=db,
        log=log,
        debug=debug,
        template_path=views_path
    )
    log.info('Starting server...')
    application.listen(app_port)
    log.info('Server started on port {}'.format(app_port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
