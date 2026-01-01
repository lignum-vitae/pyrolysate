# Source - https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
# Posted by RikH, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-01, License - CC BY-SA 4.0

from pathlib import Path


def get_project_root() -> Path:
    """ Return root of project relative to utils.py script"""
    return Path(__file__).absolute().parent.parent


def load_tld_file() -> Path:
    """ Load pyrolysate's tld.txt file """
    root = get_project_root()
    return root / "pyrolysate" / "tld.txt"
