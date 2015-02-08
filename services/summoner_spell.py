import services
from tornado import gen


class SummonerSpell():
    cache_key = 'summ_spell'

    @staticmethod
    @gen.coroutine
    def cache_all():
        db = services.db
        cachedb = services.cachedb
        pipe = cachedb.pipeline()
        spells = db.summoner_spells.find()
        for spell in (yield spells.to_list(length=None)):
            key = '{}:{}'.format(SummonerSpell.cache_key, spell['id'])
            pipe.set(key, spell['key'])
        yield gen.Task(pipe.execute)

    @staticmethod
    @gen.coroutine
    def find_cached_by_id(spell_id):
        cachedb = services.cachedb
        key = '{}:{}'.format(SummonerSpell.cache_key, spell_id)
        champ = yield gen.Task(cachedb.get, key)
        return champ
