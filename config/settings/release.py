import logging
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# SECURITY WARNING: don't commit the key to the public repos
RIOT_API_KEY = os.environ['RIOT_API_KEY']
APP_PORT = int(os.environ['PORT'])

DATABASES = {
    'mongodb': {
        'host': os.environ['MONGODB_HOST'],
        'database': os.environ['MONGODB_DB']
    },
    'redis': {
        'host': os.environ['REDIS_HOST'],
        'port': int(os.environ['REDIS_PORT']),
        'password': os.environ['REDIS_PASSWORD']
    }
}

LOGGER_SETTINGS = {
    'level': logging.WARN,
    'format': '[%(levelname)s][%(asctime)s]: %(message)s',
    'datefmt': '%H:%M:%S %d:%m:%Y'
}
