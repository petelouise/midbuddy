import os

import pyexiv2


class Job:
    def __init__(self, job_id: str, index: int):
        self.job_id = job_id
        self.index = index

    @staticmethod
    def from_file_path(file_path: str):
        job_id, index = parse_file_path(file_path)
        return Job(job_id, index)

    @property
    def url(self) -> str:
        return f"https://midjourney.com/jobs/{self.job_id}?index={self.index}"


def parse_file_path(file_path) -> tuple[str, int]:
    name, _ = os.path.splitext(file_path)
    job_id = name[-38:-2]
    index = int(name[-1])
    return job_id, index


def add_url_metadata(file_path: str) -> None:
    """Add the job URL as metadata to the image file using IPTC Source and XMP URL."""
    job = Job.from_file_path(file_path)
    url = job.url

    with pyexiv2.Image(file_path) as img:
        # Set IPTC Source metadata
        img.modify_iptc({"Iptc.Application2.Source": url})
        # Set XMP URL metadata
        img.modify_xmp({"Xmp.xmp.Identifier": url})


def process_file(file_path: str) -> str:
    """Process a file by adding metadata and returning the job URL."""
    job = Job.from_file_path(file_path)
    add_url_metadata(file_path)
    return job.url
