import config
import logging
import motor
import services
import tornadoredis
import tornado


def configure_logger(**kwargs):
    logging.basicConfig(**kwargs)
    return logging.getLogger()


def configure_mongodb(connection):
    default_port = 27017
    host = connection.get('host', None)
    port = connection.get('port', default_port)
    db = connection['database']
    client = motor.MotorClient(host, port)
    return client, client[db]


def configure_redis(connection):
    default_port = 6379
    host = connection.get('host', None)
    port = connection.get('port', default_port)
    pw = connection.get('password', None)
    redis = tornadoredis.Client(host, port, password=pw)
    redis.connect()
    return redis


def main():
    # Get config parameters
    settings = config.settings

    databases = settings.DATABASES
    app_port = settings.APP_PORT
    logger_settings = settings.LOGGER_SETTINGS

    log = configure_logger(**logger_settings)
    client, db = configure_mongodb(databases['mongodb'])
    cachedb = configure_redis(databases['redis'])
    services.initialize(db, cachedb)

    params = {
        'handlers': config.ROUTES,
        'debug': settings.DEBUG,
        'template_path': settings.VIEWS_PATH,
        'static_path': settings.STATIC_PATH,
        'db': db,
        'log': log,
        'cookie_secret': settings.SECRET_KEY,
        'login_url': settings.LOGIN_URL
    }
    application = tornado.web.Application(**params)

    log.info('Starting server...')
    application.listen(app_port)
    log.info('Server started on port {}'.format(app_port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
