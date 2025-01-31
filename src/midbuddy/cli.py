import os
import re
import webbrowser

import click
import exiftool
import pyexiv2


@click.group()
def cli() -> None:
    """
    midbuddy - helps with midjourney.
    """
    pass


@cli.group()
def meta() -> None:
    """
    metadata management commands.
    """
    pass


@meta.command()
@click.argument("path", type=click.Path(exists=True))
def add(path) -> None:
    """
    add midjourney metadata to an image file.
    """
    url = get_url(path)
    with pyexiv2.Image(path) as img:
        # Set IPTC Source metadata
        img.modify_iptc({"Iptc.Application2.Source": url})
        # Set XMP URL metadata
        img.modify_xmp({"Xmp.xmp.Identifier": url})
    click.echo(f"added metadata url: {url}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def open(path) -> None:
    """
    opens the midjourney job in a web browser.
    """
    url = get_url(path)
    click.echo(f"Opening URL: {url}")
    webbrowser.open(url)


def get_url(path: str) -> str:
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(path)[0]

    description = (
        metadata.get("PNG:Description")
        or metadata.get("XMP:Description")
        or metadata.get("EXIF:ImageDescription")
    )

    job_id = None
    job_id_prefix = "Job ID: "

    if description and job_id_prefix in description:
        click.echo("found job id prefix in description metadata")
        job_id = description.split(job_id_prefix)[-1].strip()

    name, _ = os.path.splitext(path)
    if not job_id:
        job_id = name[-38:-2]
    index = int(name[-1])
    if not job_id:
        raise ValueError("could not find job id in metadata or file path")

    url = f"https://www.midjourney.com/jobs/{job_id}"

    if index:
        url += f"?index={index}"

    return url


if __name__ == "__main__":
    cli()
