from pathlib import Path


class Crawler:
    def __init__(self, boost_root: str):
        self._boost_root = Path(boost_root).resolve()

    def crawl(self, library_key: str) -> dict:
        raise NotImplementedError()
