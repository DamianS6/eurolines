from requests_html import HTMLSession
from slugify import slugify
from datetime import datetime, timedelta
from cache import get_redis
import json

# TODO: Consider other stops (stops id, not first general city id)?

# TODO: Write locations (key - source name, val - source code?) to redis

# TODO: Correct this redis working to leave only pipeline. DONE??????

# TODO: REDIS DOESN'T WORK! Correct source and destination so it everywhere takes the same (full slugified stop name)

# TODO: Optional date_to.

# TODO: Use autocomplete selector with cities from eurolines api??????????????????

# TODO: Store cities list in redis and read from it

# TODO: Use INNER JOIN to create combinations, implement API that return them

# TODO: SQLAlchemy


def cities_list():
    redis = get_redis()
    session = HTMLSession()
    cities = []
    for i in range(150):
        r = session.get(f'https://back.eurolines.eu/euroline_api/countries/{i}/cities')
        country_info = r.json()
        print(country_info)
        if r.json() is None:
            continue
        else:
            for city in country_info:
                cities.append(city['Name'])

    for city in cities:
        redis.setex(
            city,
            60*60,
            json.dumps(city)
        )
    return cities


def find_city_code(city_name):
    session = HTMLSession()
    r = session.get(f'https://back.eurolines.eu/euroline_api/origins?q={city_name}&favorite=true')
    city_info = r.json()
    # print(city_info)
    # print(city_info[0]['stops'][0]['id']) # ??????????????????????????????????
    # TODO!
    try:
        #if len(city_info[0]['stops']) == 1:
            # print("Only one stop")
            #return city_info[0]['id']
        #else:
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

        return itineraries


def redis_work(source, destination, passengers, departure_date, carrier):
    source = slugify(source, separator='_')
    destination = slugify(destination, separator='_')
    # print(f'journey:{source}_{destination}_{departure_date}_{carrier}')
    redis = get_redis()
    redis_info = redis.get(f'journey:{source}_{destination}_{departure_date}_{carrier}')
    if redis_info is None:
        return redis_write(source, destination, passengers, departure_date, carrier, redis)
    else:
        return json.loads(redis_info)


def find_connection(source, destination, passengers, departure_date):
    """English names, date in format YYYY-MM-DD."""
    print(departure_date)
    redis_result = redis_work(source, destination, passengers, departure_date, carrier='eurolines')
    redis_filtered = [x for x in redis_result if x['free_seats'] >= passengers]
    if not redis_filtered:
        print("No results.")
        return []

    print(redis_filtered)
    return redis_filtered


def find_all(source, destination, passengers, date_from, date_to):
    print(date_to, date_from)
    days_number = datetime.strptime(date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")
    departure_date = datetime.strptime(date_from, "%Y-%m-%d").date()
    connections = []
    for i in range(days_number.days + 1):
        connections.append(find_connection(source, destination, passengers, departure_date))
        departure_date += timedelta(days=1)

    redis = get_redis()
    pipe = redis.pipeline()
    for day in connections:
        source = slugify(day[0]['source'], separator='_')
        destination = slugify(day[0]['destination'], separator='_')
        # print(f"journey:{source}_{destination}_{day[0]['departure_datetime'][:10]}_eurolines")
        pipe.setex(
            f"journey:{source}_{destination}_{day[0]['departure_datetime'][:10]}_eurolines",
            60*60,
            json.dumps(day)
        )
    pipe.execute()

    return connections
