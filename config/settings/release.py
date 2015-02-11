import logging
import os

from logging.handlers import RotatingFileHandler

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

# SECURITY WARNING: don't commit the key to the public repos
RIOT_API_KEY = os.environ['RIOT_API_KEY']

DATABASES = {
    'mongodb': {
        'host': os.environ['MONGODB_HOST'],
        'database': os.environ['MONGODB_DB']
    },
    'redis': {
        'host': os.environ['REDIS_HOST']
    }
}

LOGGER_SETTINGS = {
    'level': logging.WARN,
    'format': '[%(levelname)s][%(asctime)s]: %(message)s',
    'datefmt': '%H:%M:%S %d:%m:%Y',
    'handlers': [
        RotatingFileHandler(
            'logs/app.log',
            maxBytes=5*1024*1024,
            backupCount=5
        )
    ]
}
