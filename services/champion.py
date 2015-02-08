import services

from tornado import gen


class Champion():
    cache_key = 'champ'

    @staticmethod
    @gen.coroutine
    def cache_all():
        db = services.db
        cachedb = services.cachedb
        pipe = cachedb.pipeline()
        champions = db.champions.find()
        for champ in (yield champions.to_list(length=None)):
            key = '{}:{}'.format(Champion.cache_key, champ['id'])
            pipe.set(key, champ['name'])
        yield gen.Task(pipe.execute)

    @staticmethod
    @gen.coroutine
    def find_cached_by_id(champion_id):
        cachedb = services.cachedb
        key = '{}:{}'.format(Champion.cache_key, champion_id)
        champ = yield gen.Task(cachedb.get, key)
        return champ
