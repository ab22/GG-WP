import handlers


ROUTES = [
    (r'/', handlers.MainHandler),
    (r'/summoner/([A-Za-z]+)/([A-Za-z0-9]+)', handlers.SummonerHandler)
]
