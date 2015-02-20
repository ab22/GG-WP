import tornado.httpclient
import json

from utils import api_urls, request_handler
from tornado import gen
from services.champion import Champion
from services.summoner_spell import SummonerSpell
from services.summoner import Summoner


class Match():

    invalid_characters = (' ', '.', '\'')

    @staticmethod
    def filter_leagues_for_player(leagues, player_id, summoner_name):
        for key, league in leagues.items():
            if int(key) == player_id:
                return league
        return None

    @staticmethod
    def set_league_info(league, player):
        summoner_name = player['summonerName']
        player_league = player['league']
        league_data = None
        for entry in league['entries']:
            if entry['playerOrTeamName'] == summoner_name:
                league_data = entry
                break
        if league_data is None:
            return
        win_ratio = league_data['wins']
        win_ratio /= league_data['wins'] + league_data['losses']
        player_league['division'] = league_data['division']
        player_league['wins'] = league_data['wins']
        player_league['losses'] = league_data['losses']
        player_league['isVeteran'] = league_data['isVeteran']
        player_league['isHotStreak'] = league_data['isHotStreak']
        player_league['leaguePoints'] = league_data['leaguePoints']
        player_league['winRate'] = '{0:.2f}%'.format(win_ratio)
        player_league['tier'] = league['tier'].title()
        series = league_data.get('miniSeries', None)
        if series:
            player_league['series'] = series['progress']

    @staticmethod
    def match_players_leagues(players, leagues):
        for player in players:
            player_id = player['summonerId']
            summoner_name = player['summonerName']
            league = Match.filter_leagues_for_player(
                leagues,
                player_id,
                summoner_name
            )
            if league is None:
                continue
            Match.set_league_info(league[0], player)

    @staticmethod
    @gen.coroutine
    def filter_players_by_team(players, team_id):
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
                    'spell2Name': spell_name_2,
                    'league': {
                        'division': '',
                        'tier': 'Unranked',
                        'wins': 0,
                        'losses': 0,
                        'isVeteran': False,
                        'isHotStreak': False,
                        'leaguePoints': 0,
                        'winRate': '0.0%'
                    }
                }
                team_players.append(team_player)
        return team_players

    @staticmethod
    @gen.coroutine
    def filter_banned_champions_by_team(bans, team_id):
        team_bans = []
        for ban in bans:
            if ban['teamId'] == team_id:
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
    def get_team_ids(players, summoner_id):
        team_id = 0
        enemy_team_id = 0
        for player in players:
            if summoner_id == player['summonerId']:
                team_id = player['teamId']
                enemy_team_id = 100 if team_id == 200 else 200
                break
        return team_id, enemy_team_id

    @staticmethod
    @gen.coroutine
    def sanitize_game_data(game, summoner_id, leagues):
        players = game['participants']
        bans = game['bannedChampions']
        team_id, enemy_team_id = Match.get_team_ids(players, summoner_id)
        teammates = yield Match.filter_players_by_team(players, team_id)
        enemies = yield Match.filter_players_by_team(players, enemy_team_id)
        team_bans = yield Match.filter_banned_champions_by_team(
            bans,
            team_id
        )
        enemy_bans = yield Match.filter_banned_champions_by_team(
            bans,
            enemy_team_id
        )
        if leagues:
            Match.match_players_leagues(teammates + enemies, leagues)
        game = {
            'requester_id': summoner_id,
            'gameLength': game['gameLength'],
            'gameMode': game['gameMode'],
            'mapId': game['mapId'],
            'gameId': game['gameId'],
            'platformId': game['platformId'],
            'teams': [
                {
                    'title': 'Your Team',
                    'teamId': team_id,
                    'players': teammates,
                    'bannedChampions': team_bans
                },
                {
                    'title': 'Enemy Team',
                    'teamId': enemy_team_id,
                    'players': enemies,
                    'bannedChampions': enemy_bans
                },
            ]
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
            return code, game
        code = response.code
        game = json.loads(response.body.decode('utf-8'))
        return code, game

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
            return code, game
        summoners_ids = []
        for player in game['participants']:
            summoners_ids.append(player['summonerId'])

        code, leagues = yield Summoner.request_leagues_for_summoners(
            summoners_ids,
            region
        )
        game = yield Match.sanitize_game_data(
            game,
            summoner_id,
            leagues
        )
        return code, game
