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
        spells = yield db.summoner_spells.find().to_list(length=None)
        for spell in spells:
            key = '{}:{}'.format(SummonerSpell.cache_key, spell['id'])
            pipe.set(key, spell['name'])
        yield gen.Task(pipe.execute)

    @staticmethod
    @gen.coroutine
    def find_cached_by_id(spell_id):
        cachedb = services.cachedb
        key = '{}:{}'.format(SummonerSpell.cache_key, spell_id)
        spell = yield gen.Task(cachedb.get, key)
        return spell

    @staticmethod
    @gen.coroutine
    def get_all():
        db = services.db
        spells = yield db.summoner_spells.find().to_list(length=None)
        return spells

    @staticmethod
    def image_name(summoner_spell_name):
        """
            Replaces invalid characters from the champion name.

            For example:
                'To The King!' gets translated to SummonerToTheKing
        """
        invalid_characters = (' ', '!')
        cleaned_name = summoner_spell_name
        for invalid_char in invalid_characters:
            cleaned_name = cleaned_name.replace(invalid_char, '')
        return 'Summoner{}'.format(cleaned_name)

    @staticmethod
    @gen.coroutine
    def update_summoner_spells():
        code, spells = yield SummonerSpell.request_all()
        if spells is None:
            return code, spells
        yield SummonerSpell.migrate(spells)
        yield SummonerSpell.cache_all()
        return code, spells

