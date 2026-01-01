from importlib import resources
from pathlib import Path


def load_tld_file() -> Path:
    with resources.as_file(resources.files("pyrolysate") / "tld.txt") as path:
        return path
