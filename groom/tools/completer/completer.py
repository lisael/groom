import os

from groom.utils import find_pony_stdlib_path
from .parser import get_parser


class Loader:
    """
    Resolve imports and load scopes
    """
    def __init__(self, uses=None, path=None, ponypath=None):
        self.path = path
        self.set_ponypath(ponypath)
        self.uses = uses if uses is not None else []

    def set_ponypath(self, ponypath):
        stdlib = None
        # normalize to a list of path
        if ponypath is not None:
            if isinstance(ponypath, str):
                ponypath = [ponypath]
        else:
            ponypath = []

        # check if the stdlib is in the ponypath
        for path in ponypath:
            try:
                dirs = os.listdir(path)
                # check for a couple of known packages
                if "builtin" in dirs:
                    if "builtin_test" in dirs:
                        if "capsicum" in dirs:
                            stdlib = path
                            break
            except OSError:
                continue

        # if stdlib wasn't found, try to find it ourselves.
        if stdlib is None:
            try:
                ponypath = [find_pony_stdlib_path()] + ponypath
            except FileNotFoundError:
                pass

        if self.path is not None:
            self.ponypath.append(os.path.dirname(path))
        self.ponypath = ponypath
        self.stdlib_path = stdlib


def complete(src, pos, path=None, ponypath=None):
    """
    Generate suggestions based on current source and position
    """
    p = get_parser()
    module = p.parse(src, pos)
    loader = Loader()
    start, sugs = p.complete
    return [s for s in sugs if sugs.startswith(start)]

