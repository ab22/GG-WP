from services.region import Region
from services.summoner import Summoner
from services.match import Match
from services.champion import Champion
from services.summoner_spell import SummonerSpell


db = None
cachedb = None


def initialize(database, cache_database):
    global db
    global cachedb
    db = database
    cachedb = cache_database
