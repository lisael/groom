from groom.parser import *
from groom.lexer import reserved
from groom.tools.completer.lexer import Lexer


from ply import yacc


# add our special token type
if "COMPLETE" not in tokens:
    tokens.append("COMPLETE")


# monkey patch PLY to get access to the parser from the error token
if not getattr(yacc.call_errorfunc, "patched", False):
    old_call_error = yacc.call_errorfunc

    def new_call_errorfunc(errorfunc, token, parser):
        token.parser = parser
        return old_call_error(errorfunc, token, parser)

    yacc.call_errorfunc = new_call_errorfunc
    yacc.call_errorfunc.patched = True


token_suggestions = {}
for k, v in reserved.items():
    token_suggestions.setdefault(v, []).append(k)


def recover(tok):
    return


def p_error(tok):
    parser = tok.parser
    if tok.type == "COMPLETE":
        expected_types = parser.action[parser.statestack[-1]]
        sugs = []
        for t in expected_types:
            try:
                sug = token_suggestions[t]
                if isinstance(sug, list):
                    sugs.extend(sug)
            except KeyError:
                pass
        parser.complete = (tok.value[:tok.completepos], sugs)
    return recover(tok)


class _Parser(object):
    def __init__(self, *args, **kwargs):
        self._parser = yacc.yacc(*args, **kwargs)
        self.complete = None

    def parse(self, src, pos, **kwargs):
        self.complete = None
        result = self._parser.parse(src, lexer=Lexer(pos), **kwargs)
        if hasattr(self._parser, "complete"):
            self.complete = self._parser.complete
            del self._parser.complete
        return result


_completer_parser_cache = {}


def get_parser(*args, **kwargs):
    p = _completer_parser_cache.setdefault(
            args + tuple(kwargs.items()),
            _Parser(*args, **kwargs))
    return p
