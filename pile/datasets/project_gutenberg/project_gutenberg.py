import logging
from pathlib import Path

from ...file_utils import stream_jsonl, stream_jsonl_zst
from ...templates import Dataset

logger = logging.getLogger(__name__)


class ProjectGutenberg(Dataset):
    name = "Project Gutenberg"

    license = "Public domain"

    urls = [""]

    checksum = ""

    def replicate(self):
        logger.info(f"{self.name} cannot be replicated - downloading from source")
        self.download()

    def documents(self):
        self.raise_if_not_exists()
        return stream_jsonl_zst(list(self.paths())[0])

    def paths(self):
        paths = [str(self.dataset_dir() / str(Path(self.url).name))]
        for path in paths:
            yield path

    def examples(self):
        return list(
            stream_jsonl(Path(__file__).parent / "project_gutenberg_examples.jsonl")
        )

    def size_on_disk(self):
        return -1

    def size(self):
        return -1

    def num_docs(self):
        return -1
