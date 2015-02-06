from services.region import Region
from services.summoner import Summoner
from services.match import Match


db = None
cache_db = None
api_key = None


def initialize(database, riot_api_key, cache_database=None):
    global api_key
    global db
    global cache_db
    api_key = riot_api_key
    db = database
    cache_db = cache_database
