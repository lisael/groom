import os
from unittest import skipIf

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

    def __repr__(self):
        return "TestToken({},'{}',{},{})".format(
            self.type, self.value, self.lineno, self.pos)


def check_token(data, expected_type):
    lexer = lex_raw(data)
    t = lexer.token()
    assert(t == Token(expected_type, data, 1, 0))


def test_lex():
    check_token("coucou", "ID")


def test_float():
    check_token("1.23", "FLOAT")


def test_int():
    check_token("2", "INT")


def test_lparen():
    check_token("(", "LPAREN")


def test_lparen_new():
    check_token("""
    (""", 'LPAREN_NEW')


def test_lsquare():
    check_token("[", "LSQUARE")


def test_lsquare_new():
    check_token("""
    [""", 'LSQUARE_NEW')


def test_minus():
    check_token("-", "MINUS")


def test_minus_new():
    check_token("""
    -""", 'MINUS_NEW')


def test_minus_tilde():
    check_token("-~", "MINUS_TILDE")


def test_minus_tilde_new():
    check_token("""
    -~""", 'MINUS_TILDE_NEW')


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

  new create
    (env: Env) =>
    env.out.print("Hello, world! \xab \UABCDE0")
'''


def test_module():
    lexer = lex_raw(pony_module)
    [t for t in lexer]


@skipIf(os.environ.get("SHORT_TESTS", 0), "perform short tests")
def test_lex_stdlib():
    path = find_pony_stdlib_path()
    for root, dirs, files in os.walk(path):
        for ponysrc in [f for f in files if f.endswith(".pony")]:
            with open(os.path.join(root, ponysrc)) as src:
                print(os.path.join(root, ponysrc))
                [t for t in lex_raw(src)]
