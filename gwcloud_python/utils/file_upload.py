from pathlib import Path


def check_file(path):
    path = Path(path)
    if not path.is_file():
        raise Exception(f"The supporting file \"{str(path)}\" does not exist.")
    return path
