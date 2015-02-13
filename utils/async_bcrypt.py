import bcrypt

from tornado import gen
from tornado.process import cpu_count
from concurrent.futures import ThreadPoolExecutor


pool = ThreadPoolExecutor(cpu_count())


def generate_salt():
    return bcrypt.gensalt()


@gen.coroutine
def encrypt(data):
    data = data
    salt = generate_salt()
    hashed_data = yield pool.submit(bcrypt.hashpw, data, salt)
    return hashed_data


@gen.coroutine
def compare(hashed_data, data):
    data = data
    result = yield pool.submit(bcrypt.hashpw, data, hashed_data)
    return result == hashed_data
