from groom.lexer import lex_raw
from groom.parser import *

from ply import yacc


class CompleteLexer:
    def __init__(self, pos, *args, **kwargs):
        self._lexer = None
        self.pos = pos

    def input(self, input):
        self._lexer = lex_raw(input)

    def token(self):
        tok = self._lexer.token()
        if tok is not None:
            if tok.type in ("WS", "NEWLINE", "LINECOMMENT", "NESTEDCOMMENT"):
                return self.token()
            tokend = tok.lexpos + len(tok.value)
            if tokend >= self.pos:
                tok.real_type = tok.type
                tok.type = "COMPLETE"
                tok.completepos = len(tok.value) - (tokend - self.pos)
        return tok


tokens.append("COMPLETE")


if not getattr(yacc.call_errorfunc, "patched", False):
    old_call_error = yacc.call_errorfunc

    def new_call_errorfunc(errorfunc, token, parser):
        token.parser = parser
        return old_call_error(errorfunc, token, parser)

    yacc.call_errorfunc = new_call_errorfunc
    yacc.call_errorfunc.patched = True


def p_error(tok):
    import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    p = yacc.yacc()

    src = '''"""Docstring"""
use "collections"

act'''

    p.parse(src, lexer=CompleteLexer(len(src)))
