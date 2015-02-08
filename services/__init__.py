from services.region import Region
from services.summoner import Summoner
from services.match import Match
from services.champion import Champion
from services.summoner_spell import SummonerSpell


db = None
cachedb = None
api_key = None


def initialize(database, riot_api_key, cache_database=None):
    global api_key
    global db
    global cachedb
    api_key = riot_api_key
    db = database
    cachedb = cache_database
