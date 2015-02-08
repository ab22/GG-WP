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
    host = connection['host']
    port = connection['port']
    db = connection['database']
    client = motor.MotorClient(host, port)
    return (client, client[db])


def configure_redis():
    redis = tornadoredis.Client()
    redis.connect()
    return redis


def main():
    # Get config parameters
    settings = config.settings
    debug = settings.DEBUG
    views_path = settings.VIEWS_PATH
    static_path = settings.STATIC_PATH
    databases = settings.DATABASES
    app_port = settings.APP_PORT
    logger_settings = settings.LOGGER_SETTINGS
    riot_api_key = settings.RIOT_API_KEY
    routes = config.ROUTES

    log = configure_logger(**logger_settings)
    client, db = configure_mongodb(databases['mongodb'])
    cachedb = configure_redis()

    services.initialize(db, riot_api_key, cachedb)
    log.info('Loading champions to cache...')
    services.Champion.cache_all()
    log.info('Loading summoner spells to cache...')
    services.SummonerSpell.cache_all()

    application = tornado.web.Application(
        routes,
        db=db,
        log=log,
        debug=debug,
        template_path=views_path,
        static_path=static_path
    )
    log.info('Starting server...')
    application.listen(app_port)
    log.info('Server started on port {}'.format(app_port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
