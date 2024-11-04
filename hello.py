import os
import re
from sys import argv


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


def main():
    job = Job.from_file_path(argv[1])
    print(job.url)


if __name__ == "__main__":
    main()
