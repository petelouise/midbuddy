import click

from .hello import process_file


@click.group()
def cli():
    """MidBuddy - Midjourney helper tools."""
    pass


@cli.group()
def meta():
    """Metadata management commands."""
    pass


@meta.command()
@click.argument("path", type=click.Path(exists=True))
def add(path):
    """Add Midjourney metadata to an image file."""
    url = process_file(path)
    click.echo(f"Added metadata URL: {url}")


if __name__ == "__main__":
    cli()
