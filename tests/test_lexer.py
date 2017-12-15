import os

from groom.lexer import lex_raw
from groom.utils import find_pony_stdlib_path


HERE = os.path.dirname(os.path.realpath(__file__))


class Token(object):
    def __init__(self, type, value, lineno, pos):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.pos = pos

    def __eq__(self, other):
        return (self.type == other.type
                and self.value == other.value
                and self.lineno == other.lineno
                and self.pos == other.lexpos)


def test_lex():
    lexer = lex_raw("coucou")
    t = lexer.token()
    assert(t == Token("ID", 'coucou', 1, 0))


pony_module = r'''
"""module docstring..."""
use "my_pkg"
use localname = "my_other_pkg"

// one line comment.

/* three
lines *
comment */

/* a comment
// with embeded
*/

actor Main
  let my_int: I64 = 2
  let my_second_int: U32 = -2_000
  let my_hex: I64 = 0xDEADB33F
  let my_char: U8 = 'b'
  let my_other_char: U8 = '\b'
  let my_float: F64 = 4.2
  let my_float': F64 = 3e12
  let my_float'': F64 = -5.4E-9

  new create(env: Env) =>
    env.out.print("Hello, world! \xab \UABCDE0")
'''


def test_module():
    lexer = lex_raw(pony_module)
    [t for t in lexer]


def test_lex_stdlib():
    path = find_pony_stdlib_path()
    for root, dirs, files in os.walk(path):
        for ponysrc in [f for f in files if f.endswith(".pony")]:
            with open(os.path.join(root, ponysrc)) as src:
                print(os.path.join(root, ponysrc))
                [t for t in lex_raw(src)]
