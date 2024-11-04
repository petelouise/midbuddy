import os
import re
from sys import argv
from PIL import Image
import piexif
import piexif.helper
from libxmp import XMPFiles, consts


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
    """Add the job URL as metadata to the image file using IPTC:Source and XMP:url."""
    job = Job.from_file_path(file_path)
    url = job.url

    # Add IPTC Source
    exif_dict = piexif.load(file_path)
    if "Iptc" not in exif_dict:
        exif_dict["Iptc"] = {}
    exif_dict["Iptc"][(2, 115)] = url.encode('utf-8')  # 2:115 is Source
    piexif.insert(piexif.dump(exif_dict), file_path)

    # Add XMP url
    xmpfile = XMPFiles(file_path=file_path, open_forupdate=True)
    xmp = xmpfile.get_xmp()
    if xmp is None:
        xmp = libxmp.XMPMeta()
    xmp.set_property(consts.XMP_NS_XMP, 'url', url)
    if xmpfile.can_put_xmp(xmp):
        xmpfile.put_xmp(xmp)
    xmpfile.close_file()

def main():
    file_path = argv[1]
    job = Job.from_file_path(file_path)
    print(job.url)
    add_url_metadata(file_path)


if __name__ == "__main__":
    main()
