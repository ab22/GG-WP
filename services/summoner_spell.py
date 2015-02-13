import services
import tornado.httpclient
import utils.api_urls as api_urls
import utils.request_handler as request_handler
import json

from tornado import gen


class SummonerSpell():
    cache_key = 'summ_spell'

    @staticmethod
    @tornado.gen.coroutine
    def request_all():
        url = api_urls.all_summoners()
        client = tornado.httpclient.HTTPClient()
        try:
            response = client.fetch(url)
        except tornado.httpclient.HTTPError as ex:
            code = ex.code
            request_handler.log_invalid_request(code, url)
            return code, None
        code = response.code
        data = json.loads(response.body.decode('utf-8'))
        return code, data['data']

    @staticmethod
    @tornado.gen.coroutine
    def migrate(summoners):
        db = services.db
        yield db.summoner_spells.remove()
        for key, summoner in summoners.items():
            yield db.summoner_spells.insert(summoner)

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
