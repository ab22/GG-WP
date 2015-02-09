import tornado.web

from tornado import gen
from services import Region


class MainHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        supported_regions = Region.supported_regions
        regions_json = {str(x): str(x).upper() for x in supported_regions}
        self.render(
            'index.html',
            title='You Rage You Lose',
            supported_regions=regions_json
        )
