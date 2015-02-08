import tornado.httpclient
import json

from utils import api_urls, request_handler
from tornado import gen
from services.champion import Champion
from services.summoner_spell import SummonerSpell


def get_test_game():
    with open('match_data.json') as match_file:
        match = match_file.read()
    game = json.loads(match)
    return game


class Match():
    invalid_characters = (' ', '.', '\'')

    @staticmethod
    @gen.coroutine
    def get_players_by_team_id(players, team_id):
        team_players = []
        for player in players:
            if int(player['teamId']) == team_id:
                champion_id = player['championId']
                spell_id_1 = player['spell1Id']
                spell_id_2 = player['spell2Id']
                champion_name = yield Champion.find_cached_by_id(champion_id)
                spell_name_1 = yield SummonerSpell.find_cached_by_id(
                    spell_id_1
                )
                spell_name_2 = yield SummonerSpell.find_cached_by_id(
                    spell_id_2
                )
                champ_img_name = champion_name
                for invalid_char in Match.invalid_characters:
                    champ_img_name = champ_img_name.replace(invalid_char, '')
                team_player = {
                    'summonerId': player['summonerId'],
                    'summonerName': player['summonerName'],
                    'championName': champion_name,
                    'championImageName': champ_img_name,
                    'spell1Name': spell_name_1,
                    'spell2Name': spell_name_2
                }
                team_players.append(team_player)
        return team_players

    @staticmethod
    @gen.coroutine
    def get_banned_champions_by_team_id(bans, team_id):
        team_bans = []
        for ban in bans:
            if int(ban['teamId']) == team_id:
                champion_id = ban['championId']
                champion_name = yield Champion.find_cached_by_id(champion_id)
                champ_img_name = champion_name
                for invalid_char in Match.invalid_characters:
                    champ_img_name = champ_img_name.replace(invalid_char, '')
                team_ban = {
                    'championName': champion_name,
                    'championImageName': champ_img_name,
                    'pickTurn': ban['pickTurn']
                }
                team_bans.append(team_ban)
        return team_bans

    @staticmethod
    @gen.coroutine
    def sanitize_game_data(data, summoner_id):
        team_id = 0
        enemy_team_id = 0
        for participant in data['participants']:
            if summoner_id == int(participant['summonerId']):
                team_id = participant['teamId']
                enemy_team_id = 100 if team_id == 200 else 200
                print(team_id, enemy_team_id)
                break

        players = yield Match.get_players_by_team_id(
            data['participants'],
            team_id
        )
        enemy_players = yield Match.get_players_by_team_id(
            data['participants'],
            enemy_team_id
        )
        banned_champions = yield Match.get_banned_champions_by_team_id(
            data['bannedChampions'],
            team_id
        )
        enemy_banned_champions = yield Match.get_banned_champions_by_team_id(
            data['bannedChampions'],
            enemy_team_id
        )
        game = {
            'gameLength': data['gameLength'],
            'gameMode': data['gameMode'],
            'mapId': data['mapId'],
            'gameId': data['gameId'],
            'platformId': data['platformId'],
            'team': {
                'teamId': team_id,
                'players': players,
                'bannedChampions': banned_champions
            },
            'enemyTeam': {
                'teamId': enemy_team_id,
                'players': enemy_players,
                'bannedChampions': enemy_banned_champions
            }
        }
        return game

    @staticmethod
    @gen.coroutine
    def request_by_summoner_id(summoner_id, platform_id, region):
        """
            Performs a request to the Riot API to attempt and find a current
            game that the summoner id is on.

            #TODO:
                - If a game is found, store it in a cache db.
                - Store all summoner's data for future queries to avoid hitting
                  the API.
        """
        region = region.lower()
        url = api_urls.game_by_summoner_id(summoner_id, platform_id, region)
        client = tornado.httpclient.AsyncHTTPClient()
        game = None
        try:
            response = yield client.fetch(url)
        except tornado.httpclient.HTTPError as ex:
            code = ex.code
            request_handler.log_invalid_request(code, url)
            return (code, game)
        code = response.code
        game = json.loads(response.body.decode('ascii'))
        return (code, game)

    @staticmethod
    @gen.coroutine
    def find_by_summoner_id(summoner_id, platform_id, region):
        """
            Finds the current game for a given summoner id. Ideally, the games
            for the players must be cached to avoid multiple request hits to
            the Riot API.

            #TODO:
                - Store the game data in a cache db.
                - Since all player ids are returned in the current game data,
                  then all players must be related to that data in the cache
                  db aswell.
        """
        region = region.lower()
        code, game = yield Match.request_by_summoner_id(
            summoner_id,
            platform_id,
            region
        )
        if game is None:
            return (code, game)

        sanitized_game_data = yield Match.sanitize_game_data(
            game,
            summoner_id
        )
        return (code, sanitized_game_data)
