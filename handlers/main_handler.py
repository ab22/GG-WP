import tornado.web
from tornado import gen
from bson.json_util import dumps


class MainHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        db = self.settings['db']
        log = self.settings['log']
        summoner = yield db.summoners.find_one({'summoner_id': 22})
        log.debug(summoner)
        self.write(dumps(summoner))
