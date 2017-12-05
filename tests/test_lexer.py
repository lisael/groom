import os

from groom.lexer import lex


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
    lexer = lex("coucou")
    t = lexer.token()
    assert(t == Token("ID", 'coucou', 1, 0))
