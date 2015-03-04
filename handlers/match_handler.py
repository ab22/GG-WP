import tornado.web

from tornado import gen
from services import Region, Summoner, Match


class MatchHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self, region, summoner_name):
        invalid_region = not Region.is_region_valid(region)
        if invalid_region:
            raise tornado.web.HTTPError(404, log_message='Invalid region')
        result = {
            'template_name': 'current_match.html',
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
            self.render(**result)
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
            self.render(**result)
            return
        result['game'] = game
        self.render(**result)
