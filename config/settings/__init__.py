import os

try:
    from .dev import *
    print('Dev settings found')
except ImportError as e:
    from .release import *
    print('Dev settings not found..')


# Get the path above this file (base path).
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
VIEWS_PATH = os.path.join(BASE_PATH, 'views')
STATIC_PATH = os.path.join(BASE_PATH, 'static')

APP_PORT = 8080
