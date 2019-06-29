import click

from connections import find_connection


@click.command()
@click.option('--source')
@click.option('--destination')
@click.option('--departure_date')
def cli(source, destination, departure_date):
    find_connection(source, destination, departure_date)


if __name__ == '__main__':
    cli()
