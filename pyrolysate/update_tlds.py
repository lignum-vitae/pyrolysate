# Function decorators and caching
from functools import cache

# Standard library
from datetime import datetime

# internal depedencies
from pyrolysate.utils import load_tld_file


@cache
def get_tlds_from_iana() -> tuple[str, list[str]] | None:
    # HTTP requests (third-party)
    import requests

    try:
        response = requests.get(
            "https://data.iana.org/TLD/tlds-alpha-by-domain.txt", timeout=10
        )
        response.raise_for_status()
        lines = response.text.split("\n")
        return lines[0], list(map(lambda x: x.lower(), filter(None, lines[1:])))
    except requests.RequestException as e:
        print(f"Error fetching TLD list: {e}")
        return None


@cache
def get_tlds_from_local(path_to_tlds_file: str = None) -> tuple[str, list[str]] | None:
    if path_to_tlds_file is None:
        path_to_tlds_file = load_tld_file()
    try:
        with open(path_to_tlds_file, "r") as file:
            lines = file.readlines()
            version = lines[1].strip()
            dated = lines[2].strip()
            last_updated = f"{version}, {dated}"
            tlds = [line.strip().lower() for line in lines[4:] if line.strip()]
            return last_updated, tlds
    except (IOError, IndexError) as e:
        print(f"Error reading local TLD file: {e}")
        return None


def update_local_tld_file(file_name: str = "tld") -> tuple[str, int]:
    if not isinstance(file_name, str):
        return "Failed to write file. File name must be a string.", 1
    tlds = get_tlds_from_iana()
    if tlds is None:
        return "Failed to fetch tlds", 1
    ver_dated, tldss = tlds
    version, dated = ver_dated.split(",")

    if not file_name.endswith(".txt"):
        file_name = f"{file_name}.txt"
    with open(file_name, "w") as file:
        file.write(f"File Created: {datetime.now().strftime('%d %B %Y %H:%M')}\n")
        file.write(f"{version}\n")
        file.write(f"{dated}\n\n")
        for tld in tldss:
            file.write(f"{tld}\n")
    return "File created successfully", 0


def update(file_name: str = "tld"):
    return update_local_tld_file(file_name)


if __name__ == "__main__":
    update()
