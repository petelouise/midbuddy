import os
from sys import argv
from PIL import Image
import piexif
import piexif.helper


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
    """Add the job URL as metadata to the image file using IPTC:Source."""
    job = Job.from_file_path(file_path)
    url = job.url

    with Image.open(file_path) as img:
        # Create a new info dictionary with existing metadata
        info = img.info
        info['Source'] = url
        
        # Save with metadata preserved
        img.save(file_path, format=img.format, **info)


def main():
    file_path = argv[1]
    job = Job.from_file_path(file_path)
    print(job.url)
    add_url_metadata(file_path)


if __name__ == "__main__":
    main()
