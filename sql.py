import psycopg2
from psycopg2.extras import RealDictCursor

pg_config = {
    'host': 'pythonweekend.cikhbyfn2gm8.eu-west-1.rds.amazonaws.com',
    'database': 'pythonweekend',
    'user': 'shareduser',
    'password': 'NeverEverSharePasswordsInProductionEnvironement'
}


def save_into_db(journeys):
    sql_insert = """
        INSERT INTO journeys (source, destination, departure_datetime, arrival_datetime, carrier,
                              vehicle_type, price, currency)
        VALUES (%(source)s,
                %(destination)s,
                %(departure_datetime)s,
                %(arrival_datetime)s,
                'eurolines',
                'bus',
                %(price)s,
                'EUR');
    """

    conn = psycopg2.connect(**pg_config)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql_insert, journeys)
        conn.commit()
