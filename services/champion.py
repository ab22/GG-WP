import services
import tornado.httpclient
import utils.api_urls as api_urls
import utils.request_handler as request_handler
import json

from tornado import gen


class Champion():
    cache_key = 'champ'

    @staticmethod
    @tornado.gen.coroutine
    def request_all():
        url = api_urls.all_champions()
        client = tornado.httpclient.HTTPClient()
        try:
            response = client.fetch(url)
        except tornado.httpclient.HTTPError as ex:
            code = ex.code
            request_handler.log_invalid_request(code, url)
            return code, None
        data = json.loads(response.body.decode('utf-8'))
        return 200, data['data']

    @staticmethod
    @tornado.gen.coroutine
    def migrate(champs):
        db = services.db
        yield db.champions.remove()
        for key, champ in champs.items():
            yield db.champions.insert(champ)

    @staticmethod
    @gen.coroutine
    def cache_all():
        db = services.db
        cachedb = services.cachedb
        pipe = cachedb.pipeline()
        champions = yield db.champions.find().to_list(length=None)
        for champ in champions:
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

    @staticmethod
    @gen.coroutine
    def get_all():
        db = services.db
        champions = yield db.champions.find().to_list(length=None)
        return champions

    @staticmethod
    def image_name(champion_name):
        """
            Replaces invalid characters from the champion name.

            For example:
                Cho'Gath gets translated to ChoGath.
        """
        invalid_characters = (' ', '.', '\'')
        cleaned_name = champion_name
        for invalid_char in invalid_characters:
            cleaned_name = cleaned_name.replace(invalid_char, '')
        return cleaned_name

    @staticmethod
    @gen.coroutine
    def update_champions():
        code, champs = yield Champion.request_all()
        if champs is None:
            return code, champs
        yield Champion.migrate(champs)
        yield Champion.cache_all()
        return code, champs
