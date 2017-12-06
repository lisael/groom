import os
from pathlib import Path


from subprocess import check_output


def find_pony_stdlib_path():
    path = os.environ.get("GROOM_PONY_STDLIB", None)
    if path is None:
        ponyc_path = check_output(["which", "ponyc"])
        ponyc_path = Path(ponyc_path.decode().strip())
        path = ponyc_path.resolve().joinpath("../../packages").resolve()
        if not path.exists:
            raise FileNotFoundError()
        path = str(path)
        return path
