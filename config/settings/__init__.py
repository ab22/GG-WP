import os


ENV = os.environ.get('ENV', 'DEV')

if ENV == 'DEV':
    from .dev import *
elif ENV == 'RELEASE':
    from .release import *


# Get the path above this file (base path).
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
VIEWS_PATH = os.path.join(BASE_PATH, 'views')
STATIC_PATH = os.path.join(BASE_PATH, 'static')
SESSION_COOKIE_NAME = '__session'
