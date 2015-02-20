import config.settings as settings


def summoners_by_names(summoners_name, region):
    version = 1.4
    api_key = settings.RIOT_API_KEY
    url = 'https://{0}.api.pvp.net/api/lol/{0}/v{1}/summoner/by-name/{2}' \
          '?api_key={3}'
    return url.format(region, version, summoners_name, api_key)


def game_by_summoner_id(summoner_id, platform_id, region):
    api_key = settings.RIOT_API_KEY
    url = 'https://{0}.api.pvp.net/observer-mode/rest/consumer/' \
          'getSpectatorGameInfo/{1}/{2}?api_key={3}'
    return url.format(region, platform_id, summoner_id, api_key)


def all_champions():
    api_key = settings.RIOT_API_KEY
    url = 'https://na.api.pvp.net/api/lol/static-data/na/v1.2/champion?' \
          'api_key={}'
    return url.format(api_key)


def all_summoners():
    api_key = settings.RIOT_API_KEY
    url = 'https://na.api.pvp.net/api/lol/static-data/na/v1.2/'\
          'summoner-spell?api_key={}'
    return url.format(api_key)


def summoners_leagues(summoners, region):
    api_key = settings.RIOT_API_KEY
    url = 'https://{0}.api.pvp.net/api/lol/{0}/v2.5/league/by-summoner/' \
          '{1}/entry?api_key={2}'
    return url.format(region, summoners, api_key)
