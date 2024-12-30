import webbrowser

import click
import exiftool

from .hello import process_file


@click.group()
def cli():
    """midbuddy - helps with midjourney."""
    pass


@cli.group()
def meta() -> None:
    """metadata management commands."""
    pass


@meta.command()
@click.argument("path", type=click.Path(exists=True))
def add(path) -> None:
    """add midjourney metadata to an image file."""
    url = process_file(path)
    click.echo(f"added metadata url: {url}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def open(path) -> None:
    """
    opens the midjourney job in a web browser.
    """
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(path)[0]
            click.echo(f"Full metadata:\n{metadata}")

        description = (
            metadata.get("PNG:Description")
            or metadata.get("XMP:Description")
            or metadata.get("EXIF:ImageDescription")
        )
        click.echo(f"XMP:Description: {metadata.get('XMP:Description')}")
        click.echo(f"EXIF:ImageDescription: {metadata.get('EXIF:ImageDescription')}")

        if not description:
            raise ValueError("No description metadata found in the image.")

        job_id_prefix = "Job ID: "
        if job_id_prefix not in description:
            raise ValueError(f"No 'Job ID' field found in description: {description}")

        job_id = description.split(job_id_prefix)[-1].strip()
        if not job_id:
            raise ValueError("The 'Job ID' field is empty or invalid.")

        url = f"https://www.midjourney.com/jobs/{job_id}"
        click.echo(f"Opening URL: {url}")
        webbrowser.open(url)
    except Exception as e:
        click.echo(f"Unexpected Error: {e}", err=True)


if __name__ == "__main__":
    cli()
