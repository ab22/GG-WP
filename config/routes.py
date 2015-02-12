import handlers


ROUTES = [
    (r'/', handlers.MainHandler),
    (r'/match/([A-Za-z]+)/([A-Za-z0-9|\w|\W]+)', handlers.MatchHandler),
    (r'/login', handlers.LoginHandler)
]
