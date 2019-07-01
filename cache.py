from redis import StrictRedis

redis = None


def get_redis():
    redis_config = {
        'host': '157.230.124.217',
        'password': 'akd89DSk23Kldl0ram',
        'port': 6379,
    }
    global redis
    if redis:
        return redis
    redis = StrictRedis(socket_connect_timeout=3, **redis_config)
    return redis
