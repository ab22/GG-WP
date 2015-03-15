import json

from tornado import gen
from tornado.web import authenticated
from .base_handlers import AuthHandler, JsonHandler
from services import Champion, SummonerSpell


class DashboardHandler(AuthHandler):
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
            yield Champion.update_champions()
        elif action == 'summoner_spells':
            yield SummonerSpell.update_summoner_spells()
        self.render(template)


class ChampionHandler(AuthHandler, JsonHandler):
    @authenticated
    @gen.coroutine
    def get(self):
        champions = yield Champion.get_all()
        filtered_champions = [
            {
                'id': champion['id'],
                'name': champion['name'],
                'title': champion['title'],
                'imageName': Champion.image_name(champion['name'])
            }
            for champion in champions
        ]
        json_data = json.dumps(filtered_champions)
        self.write(json_data)


class SummonerSpellHandler(AuthHandler, JsonHandler):
    @authenticated
    @gen.coroutine
    def get(self):
        spells = yield SummonerSpell.get_all()
        filtered_spells = [
            {
                'id': spell['id'],
                'name': spell['name'],
                'description': spell['description'],
                'summonerLevel': spell['summonerLevel'],
                'image': SummonerSpell.image_name(spell['name'])
            }
            for spell in spells
        ]
        json_data = json.dumps(filtered_spells)
        self.write(json_data)
