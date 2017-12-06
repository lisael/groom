import os
from groom.utils import find_pony_stdlib_path
from groom.lexer import lex


def test_find_pony_stdlib_path():
    path = find_pony_stdlib_path()
    for root, dirs, files in os.walk(path):
        for ponysrc in [f for f in files if f.endswith(".pony")]:
            with open(os.path.join(root, ponysrc)) as src:
                [t for t in lex(src)]
