import logging


def log_invalid_request(code, url):
    log = logging.getLogger()
    if code == 400 or code == 401 or code == 500:
        log.critical('Bad request was returned from the Riot API')
        log.critical('Response code: {}'.format(code))
        log.critical('Request URL: {}'.format(url))
    elif code == 429:
        log.error('Rate limit exceeded.')
    elif code == 503:
        log.error('Riot API service unavailable.')
