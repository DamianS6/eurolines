import click

from connections import find_connection


@click.command()
@click.option('--source')
@click.option('--destination')
@click.option('--departure_date')
def cli(source, destination, departure_date):
    passengers = 1
    find_connection(source, destination, passengers, departure_date)
