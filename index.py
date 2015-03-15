import config
import logging
import services
import tornado


def configure_logger(**kwargs):
    logging.basicConfig(**kwargs)
    return logging.getLogger()


def main():
    # Get config parameters
    settings = config.settings
    app_port = settings.APP_PORT
    logger_settings = settings.LOGGER_SETTINGS
    log = configure_logger(**logger_settings)
    services.initialize()

    params = {
        'handlers': config.ROUTES,
        'debug': settings.DEBUG,
        'template_path': settings.VIEWS_PATH,
        'static_path': settings.STATIC_PATH,
        'log': log,
        'cookie_secret': settings.SECRET_KEY,
        'login_url': settings.LOGIN_URL,
        'db': services.db
    }
    application = tornado.web.Application(**params)

    log.info('Starting server...')
    application.listen(app_port)
    log.info('Server started on port {}'.format(app_port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
