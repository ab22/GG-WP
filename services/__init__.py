import config
import motor
import tornadoredis

from services.region import Region
from services.summoner import Summoner
from services.match import Match
from services.champion import Champion
from services.summoner_spell import SummonerSpell


db = None
cachedb = None

DEFAULT_MONGODB_PORT = 27017
DEFAULT_REDIS_PORT = 6379


def configure_mongodb(connection):
    host = connection.get('host', None)
    port = connection.get('port', DEFAULT_MONGODB_PORT)
    db = connection['database']
    client = motor.MotorClient(host, port)
    return client, client[db]


def configure_redis(connection):
    host = connection.get('host', None)
    port = connection.get('port', DEFAULT_REDIS_PORT)
    pw = connection.get('password', None)
    redis = tornadoredis.Client(host, port, password=pw)
    redis.connect()
    return redis


def initialize():
    global db
    global cachedb
    settings = config.settings
    databases = settings.DATABASES
    client, db = configure_mongodb(databases['mongodb'])
    cachedb = configure_redis(databases['redis'])
