# The purpose of this file to bump the "patch" version of the project
# after the "Monthly TLD Update" workflow runs

import tomllib
import toml
from pathlib import Path

# Creates Path object to root relative to "bump_version.py"
root_dir = Path(__file__).parent
pyproject_file = root_dir / "pyproject.toml"

with open(pyproject_file, 'rb') as f:
    toml_file = tomllib.load(f)

project_version = toml_file["project"]["version"]
(major, minor, patch) = [int(x) for x in project_version.split('.')]
patch += 1 # bump just the patch version

bumped_project_version = ".".join([str(x) for x in [major, minor, patch]])
toml_file["project"]["version"] = bumped_project_version

with open(pyproject_file, 'w') as f:
    toml.dump(toml_file, f)