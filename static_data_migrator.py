import sys
import motor
import json
import tornado
import config.settings as settings
import utils.api_urls as api_urls

from tornado.ioloop import IOLoop


def configure_mongodb(connection):
    host = connection['host']
    port = connection['port']
    db = connection['database']
    client = motor.MotorClient(host, port)
    return (client, client[db])


@tornado.gen.coroutine
def request_all_champs():
    url = api_urls.all_champions()
    client = tornado.httpclient.HTTPClient()
    try:
        response = client.fetch(url)
    except tornado.httpclient.HTTPError as e:
        print("Error:", e)
        client.close()
        return None
    data = json.loads(response.body.decode('ascii'))
    return data['data']


@tornado.gen.coroutine
def request_all_summoners():
    url = api_urls.all_summoners()
    client = tornado.httpclient.HTTPClient()
    try:
        response = client.fetch(url)
    except tornado.httpclient.HTTPError as e:
        print("Error:", e)
        client.close()
        return None
    data = json.loads(response.body.decode('ascii'))
    return data['data']


@tornado.gen.coroutine
def migrate_champs(db):
    print('Requesting all champions...')
    champs = yield request_all_champs()
    if champs:
        print('Removing all champions...')
        yield db.champions.remove()
        print('Inserting new champions...')
        for key, champ in champs.items():
            yield db.champions.insert(champ)
        print('Champions database was updated successfully!')


@tornado.gen.coroutine
def migrate_summoners(db):
    print('Requesting all summoners...')
    summoners = yield request_all_summoners()
    if summoners:
        print('Removing all summoners...')
        yield db.summoner_spells.remove()
        print('Inserting new summoners')
        for key, summoner in summoners.items():
            yield db.summoner_spells.insert(summoner)
        print('Summoners database was updated successfully!')


@tornado.gen.coroutine
def main(args):
    all_options = [
        'champions',
        'summoner_spells'
    ]
    usage = 'Usage: {} [-r|--request|--request-all] ' \
            '<champions|summoner_spells>\r\n'.format(args[0])
    if len(args) <= 1:
        print(usage)
        IOLoop.instance().stop()
        return
    # Remove script name from args
    args = args[1:]
    if args[0] == '-r' or args[0] == '--request':
        # Remove -r|--request option from args
        args = args[1:]
    elif args[0] == '--request-all':
        args = all_options
    else:
        print(usage)
        IOLoop.instance().stop()
        return

    print('Starting migrator...')
    databases = settings.DATABASES

    print('Configuring database client...')
    client, db = configure_mongodb(databases['mongodb'])

    if 'champions' in args:
        yield migrate_champs(db)
    if 'summoner_spells' in args:
        yield migrate_summoners(db)
    IOLoop.instance().stop()


if __name__ == "__main__":
    main(sys.argv)
    IOLoop.instance().start()
