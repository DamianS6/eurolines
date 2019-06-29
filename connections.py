from requests_html import HTMLSession
from redis import StrictRedis
from slugify import slugify
import json

# TODO: Consider other stops (stops id, not first general city id)?

# TODO: Write locations (key - source name, val - source code?) to redis


def find_city_code(city_name):
    session = HTMLSession()
    r = session.get(f'https://back.eurolines.eu/euroline_api/origins?q={city_name}&favorite=true')
    city_info = r.json()
    # print(city_info)
    # print(city_info[0]['stops'][0]['id']) # ??????????????????????????????????
    # TODO
    try:
        if len(city_info[0]['stops']) == 1:
            # print("Only one stop")
            return city_info[0]['id']
        else:
            # print("More stops")
            return city_info[0]['id']
    except IndexError:
        print("I haven't found one of the given cities.")
        return None


def redis_write(source, destination, passengers, departure_date, carrier, redis):
    source_code = find_city_code(source)
    destination_code = find_city_code(destination)
    if not (source_code and destination_code):
        return None

    session = HTMLSession()
    session.get('https://www.eurolines.eu/')
    # TODO Change URL to consider stops code, not city code even if there's just one stop
    r = session.get(f'https://back.eurolines.eu/euroline_api/journeys?date={departure_date}&flexibility=0'
                    f'&currency=CURRENCY.EUR&passengers=BONUS_SCHEME_GROUP.ADULT,1&promoCode=&direct=false'
                    f'&originCity={source_code}&destinationCity={destination_code}')

    itineraries = []
    for item in r.json():
        if item['remaining'] >= int(passengers):
            itineraries.append({
                'departure_datetime': item['departure'],
                'arrival_datetime': item['arrival'],
                'source': item['origin']['name'],
                'destination': item['destination']['name'],
                'price': item['price'],
                'duration': item['duration'],
                'free_seats': item['remaining'],
                'source_ID': item['origin']['id'],
                'destination_ID': item['destination']['id'],
            })

    redis.setex(
        f'journey:{source}_{destination}_{departure_date}_{carrier}',
        60*60,
        json.dumps(itineraries)
    )
    return itineraries


def redis_work(source, destination, passengers, departure_date, carrier):
    source = slugify(source)
    destination = slugify(destination, separator='_')

    redis_config = {
        'host': '157.230.124.217',
        'password': 'akd89DSk23Kldl0ram',
        'port': 6379,
    }
    redis = StrictRedis(socket_connect_timeout=3, **redis_config)
    redis_info = redis.get(f'journey:{source}_{destination}_{departure_date}_{carrier}')

    if redis_info is None:
        return redis_write(source, destination, passengers, departure_date, carrier, redis)
    else:
        return json.loads(redis_info)


def find_connection(source, destination, departure_date, passengers):
    """English names, date in format YYYY-MM-DD."""
    redis_result = redis_work(source, destination, passengers, departure_date, carrier='eurolines')
    redis_filtered = [x for x in redis_result if x['free_seats'] >= passengers]
    if not redis_filtered:
        print("No results.")
        return []

    print(redis_filtered)
    return redis_filtered

