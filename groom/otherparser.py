from groom.lexer import Lexer
from groom.parser import *

from ply import yacc

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

act

'''

    p.parse(src, lexer=Lexer())
