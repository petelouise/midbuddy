import click

from .hello import process_file


@click.group()
def cli():
    """midbuddy - helps with midjourney."""
    pass


@cli.group()
def meta():
    """metadata management commands."""
    pass


@meta.command()
@click.argument("path", type=click.Path(exists=True))
def add(path):
    """add midjourney metadata to an image file."""
    url = process_file(path)
    click.echo(f"added metadata url: {url}")


if __name__ == "__main__":
    cli()
