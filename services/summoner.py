import services
import tornado.httpclient
import json

from utils import api_urls, request_handler
from tornado import gen


class Summoner():

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
        url = api_urls.summoners_by_names(summoner_name, region)
        client = tornado.httpclient.AsyncHTTPClient()
        summoner = None
        try:
            response = yield client.fetch(url)
        except tornado.httpclient.HTTPError as ex:
            code = ex.code
            request_handler.log_invalid_request(code, url)
            return (code, summoner)
        code = response.code
        db = services.db
        data = json.loads(response.body.decode('ascii'))
        summoner = data[summoner_name.lower()]
        summoner['name'] = summoner['name'].lower()
        summoner['region'] = region
        db.summoners.save(summoner)
        return (code, summoner)

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
            return (code, summoner)
        return (200, summoner)
