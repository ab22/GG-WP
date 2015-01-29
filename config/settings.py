import logging


PORT = 8000

LOG_SETTINGS = {
    'level': logging.DEBUG,
    'format': '[%(levelname)s][%(asctime)s]: %(message)s',
    'datefmt': '%H:%M:%S %d:%m:%Y',
    'handlers': [
        logging.handlers.RotatingFileHandler(
            'logs/app.log',
            maxBytes=5*1024*1024,
            backupCount=5
        )
    ]
}
