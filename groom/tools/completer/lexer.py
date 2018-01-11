from groom.lexer import lex_raw


class Lexer:
    def __init__(self, pos, *args, **kwargs):
        self._lexer = None
        self.pos = pos
        self.passed = False

    def input(self, input):
        self._lexer = lex_raw(input)

    def token(self):
        tok = self._lexer.token()
        if tok is not None:
            tokend = tok.lexpos + len(tok.value)
            if not self.passed and tokend >= self.pos:
                tok.real_type = tok.type
                tok.type = "COMPLETE"
                tok.completepos = len(tok.value) - (tokend - self.pos)
            elif tok.type in ("WS", "NEWLINE", "LINECOMMENT", "NESTEDCOMMENT"):
                return self.token()
        return tok
