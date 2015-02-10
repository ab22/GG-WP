import tornado.web
from tornado import gen
from services import Region, Summoner, Match, Champion, SummonerSpell


class MatchHandler(tornado.web.RequestHandler):
    invalid_characters = (' ', '.', '\'')

    def filter_leagues_for_player(self, leagues, player_id, summoner_name):
        for key, league in leagues.items():
            if int(key) == player_id:
                return league
        return None

    def set_league_info(self, league, player):
        summoner_name = player['summonerName']
        player_league = player['league']
        league_data = None
        for entry in league['entries']:
            if entry['playerOrTeamName'] == summoner_name:
                league_data = entry
                break
        player_league['division'] = league_data['division']
        player_league['wins'] = league_data['wins']
        player_league['losses'] = league_data['losses']
        player_league['isVeteran'] = league_data['isVeteran']
        player_league['isHotStreak'] = league_data['isHotStreak']
        player_league['leaguePoints'] = league_data['leaguePoints']
        player_league['winRate'] = '{0:.2f}'.format(
            league_data['wins'] / (league_data['wins'] + league_data['losses'])
        )
        player_league['tier'] = league['tier']

    def match_players_leagues(self, players, leagues):
        for player in players:
            player_id = player['summonerId']
            summoner_name = player['summonerName']
            league = self.filter_leagues_for_player(
                leagues,
                player_id,
                summoner_name
            )
            if league is None:
                continue
            self.set_league_info(league[0], player)

    @gen.coroutine
    def filter_players_by_team(self, players, team_id):
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
                for invalid_char in MatchHandler.invalid_characters:
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
                        'tier': 'UNRANKED',
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

    @gen.coroutine
    def filter_banned_champions_by_team(self, bans, team_id):
        team_bans = []
        for ban in bans:
            if ban['teamId'] == team_id:
                champion_id = ban['championId']
                champion_name = yield Champion.find_cached_by_id(champion_id)
                champ_img_name = champion_name
                for invalid_char in MatchHandler.invalid_characters:
                    champ_img_name = champ_img_name.replace(invalid_char, '')
                team_ban = {
                    'championName': champion_name,
                    'championImageName': champ_img_name,
                    'pickTurn': ban['pickTurn']
                }
                team_bans.append(team_ban)
        return team_bans

    def get_team_ids(self, players, summoner_id):
        team_id = 0
        enemy_team_id = 0
        for player in players:
            if summoner_id == player['summonerId']:
                team_id = player['teamId']
                enemy_team_id = 100 if team_id == 200 else 200
                break
        return (team_id, enemy_team_id)

    @gen.coroutine
    def sanitize_game_data(self, game, summoner_id, leagues):
        players = game['participants']
        bans = game['bannedChampions']
        team_id, enemy_team_id = self.get_team_ids(players, summoner_id)
        teammates = yield self.filter_players_by_team(players, team_id)
        enemies = yield self.filter_players_by_team(players, enemy_team_id)
        team_bans = yield self.filter_banned_champions_by_team(
            bans,
            team_id
        )
        enemy_bans = yield self.filter_banned_champions_by_team(
            bans,
            enemy_team_id
        )
        if leagues:
            self.match_players_leagues(teammates + enemies, leagues)
        game = {
            'gameLength': game['gameLength'],
            'gameMode': game['gameMode'],
            'mapId': game['mapId'],
            'gameId': game['gameId'],
            'platformId': game['platformId'],
            'team': {
                'teamId': team_id,
                'players': teammates,
                'bannedChampions': team_bans
            },
            'enemyTeam': {
                'teamId': enemy_team_id,
                'players': enemies,
                'bannedChampions': enemy_bans
            }
        }
        return game

    @gen.coroutine
    def get(self, region, summoner_name):
        invalid_region = not Region.is_region_valid(region)
        if invalid_region:
            raise tornado.web.HTTPError(404, log_message='Invalid region')
        result = {
            'error_msg': None,
            'game': None
        }
        code, summoner = yield Summoner.find_by_name(summoner_name, region)
        if summoner is None:
            if code == 404:
                result['error_msg'] = 'Summoner not found!'
            elif code == 429 or code == 503:
                result['error_msg'] = 'Server is overloaded!'
            else:
                result['error_msg'] = 'An error ocurred while performing ' \
                                      'your request.'
            self.render('current_match.html', **result)
            return
        summoner_id = summoner['id']
        platform_id = Region.to_platform_id(region)
        code, game = yield Match.find_by_summoner_id(
            summoner_id,
            platform_id,
            region
        )
        if game is None:
            if code == 404:
                result['error_msg'] = 'Summoner is not in a game!'
            elif code == 429 or code == 503:
                result['error_msg'] = 'Server is overloaded!'
            else:
                result['error_msg'] = 'An error ocurred while performing ' \
                                      'your request.'
            self.render('current_match.html', **result)
            return
        summoners_ids = []
        for player in game['participants']:
            summoners_ids.append(player['summonerId'])

        res, leagues = yield Summoner.request_leagues_for_summoners(
            summoners_ids,
            region
        )
        game = yield self.sanitize_game_data(game, summoner_id, leagues)
        result['game'] = game
        self.render('current_match.html', **result)
