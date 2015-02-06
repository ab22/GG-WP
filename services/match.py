import tornado.httpclient
import json

from utils import api_urls, request_handler
from tornado import gen


class Match():

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
        return (code, game)
