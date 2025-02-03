import os
import re
import shutil
import webbrowser
import zipfile
from glob import glob
from pathlib import Path

import click
import exiftool
import pyexiv2
from send2trash import send2trash


@click.group()
def cli() -> None:
    """
    midbuddy - helps with midjourney.
    """
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def add_metadata(path) -> None:
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


@cli.command()
@click.argument("output_dir", type=str)
@click.argument("input_paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--trash", is_flag=True, help="move input files to trash after collecting"
)
def collect(output_dir: str, input_paths, trash: bool) -> None:
    """
    collect files from input paths into a new directory.
    handles zip files and nested directories.
    """
    # create output directory
    output_path = Path(output_dir)
    if output_path.exists():
        raise click.ClickException(f"output directory {output_dir} already exists")
    output_path.mkdir(parents=True)

    temp_dir = output_path / "_tmp"

    for input_path in input_paths:
        path = Path(input_path)

        # handle zip files
        if path.suffix.lower() == ".zip":
            temp_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # move files from temp directory
            for file in temp_dir.rglob("*"):
                if file.is_file():
                    shutil.move(str(file), str(output_path / file.name))

            # clean up temp directory
            shutil.rmtree(temp_dir)

            if trash:
                send2trash(str(path))

        # handle directories
        elif path.is_dir():
            for file in path.rglob("*"):
                if file.is_file():
                    shutil.copy2(str(file), str(output_path / file.name))

            if trash:
                send2trash(str(path))

        # handle individual files
        else:
            shutil.copy2(str(path), str(output_path / path.name))
            if trash:
                send2trash(str(path))

    click.echo(f"Collected files into {output_dir}")
