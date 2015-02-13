from tornado import gen
from tornado.web import authenticated
from .base_handler import BaseHandler
from services import Champion, SummonerSpell


class DashboardHandler(BaseHandler):

    @gen.coroutine
    def update_champions(self):
        code, champs = yield Champion.request_all()
        if champs is None:
            return
        yield Champion.migrate(champs)
        yield Champion.cache_all()

    @gen.coroutine
    def update_summoner_spells(self):
        code, spells = yield SummonerSpell.request_all()
        if spells is None:
            return
        yield SummonerSpell.migrate(spells)
        yield SummonerSpell.cache_all()

    @authenticated
    @gen.coroutine
    def get(self):
        self.render('dashboard.html')

    @authenticated
    @gen.coroutine
    def post(self):
        template = 'dashboard.html'
        action = self.get_body_argument('action', None)
        if action is None:
            self.render(template)
            return

        if action == 'champions':
            self.update_champions()
        elif action == 'summoner_spells':
            self.update_summoner_spells()
        self.render(template)
