import services
import tornado.httpclient
import json

from utils import api_urls, request_handler
from tornado import gen
from tornado.escape import url_escape


class Summoner():
    @staticmethod
    @gen.coroutine
    def request_leagues_for_summoners(summoners, region):
        """
            Request league information for all of the summoners.
        """
        region = region.lower()
        summoners_ids = ','.join(
            [str(x) for x in summoners]
        )
        url = api_urls.summoners_leagues(summoners_ids, region)
        client = tornado.httpclient.AsyncHTTPClient()
        leagues = None
        try:
            response = yield client.fetch(url)
        except tornado.httpclient.HTTPError as ex:
            code = ex.code
            request_handler.log_invalid_request(code, url)
            return (code, leagues)
        code = response.code
        leagues = json.loads(response.body.decode('utf-8'))
        return code, leagues

    @staticmethod
    @gen.coroutine
    def request_by_name(summoner_name, region):
        """
            Performs a request to the Riot API to attempt and find the
            specified summoner in the parameters for the region a specific
            region.

            If the summoner is found, it is inserted to the database with the
            region field added. The Riot API doesn't return the summoner data
            with the region that we send, so we must add it.
        """
        region = region.lower()
        html_summoner_name = url_escape(summoner_name, plus=False)
        url = api_urls.summoners_by_names(html_summoner_name, region)
        client = tornado.httpclient.AsyncHTTPClient()
        summoner = None
        try:
            response = yield client.fetch(url)
        except tornado.httpclient.HTTPError as ex:
            code = ex.code
            request_handler.log_invalid_request(code, url)
            return code, summoner
        code = response.code
        db = services.db
        data = json.loads(response.body.decode('utf-8'))
        summoner = data[summoner_name.lower().replace(' ', '')]
        summoner['name'] = summoner['name'].lower()
        summoner['region'] = region
        db.summoners.save(summoner)
        return code, summoner

    @staticmethod
    @gen.coroutine
    def find_by_name(summoner_name, region):
        db = services.db
        region = region.lower()
        summoner = yield db.summoners.find_one({
            'name': summoner_name.lower(),
            'region': region
        })
        if summoner is None:
            code, summoner = yield Summoner.request_by_name(
                summoner_name,
                region
            )
            return code, summoner
        return 200, summoner
