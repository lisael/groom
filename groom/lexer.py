"""
pony lexer

WIP!!!

This lexes the whole pony standard library... but the correctness is still
to be proven

TODO:
    - nested commnents (/* /* */ */)
      Did not search about recursive lexer rules...
    - error handling (define t_error)


"""
from io import IOBase

from ply.lex import TOKEN, LexError
from ply.lex import lex as plylex


reserved = {
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "end": "END",
    "ifdef": "IFDEF",
    "iftype": "IFTYPE",
    "match": "MATCH",
    "while": "WHILE",
    "do": "DO",
    "repeat": "REPEAT",
    "until": "UNTIL",
    "for": "FOR",
    "in": "IN",
    "with": "WITH",
    "try": "TRY",
    "recover": "RECOVER",
    'consume': "CONSUME",
    "use": "USE",
    "interface": "CLASS_DECL",
    "trait": "CLASS_DECL",
    "primitive": "CLASS_DECL",
    "struct": "CLASS_DECL",
    "class": "CLASS_DECL",
    "actor": "CLASS_DECL",
    "fun": "METH_DECL",
    "be": "METH_DECL",
    "new": "METH_DECL",
    "type": "CLASS_DECL",
    "is": "IS",
    "var": "VAR",
    "let": "LET",
    "embed": "EMBED",
    "return": "RETURN",
    "break": "BREAK",
    "continue": "CONTINUE",
    "error": "ERROR",
    "compile_intrinsic": "COMPILE_INTRINSIC",
    "compile_error": "COMPILE_ERROR",
    "isnt": "ISNT",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "xor": "XOR",
    "elseif": "ELSEIF",
    "addressof": "ADDRESSOF",
    "digestof": "DIGESTOF",
    "this": "THIS",
    "as": "AS",
    "object": "OBJECT",
    "where": "WHERE",
    "iso": "CAP",
    "trn": "CAP",
    "ref": "CAP",
    "val": "CAP",
    "box": "CAP",
    "tag": "CAP",
    "true": "TRUE",
    "false": "FALSE",
}

tokens = [
    "STRING",
    "WS",
    "GENCAP",
    "ID",
    "LINECOMMENT",
    "NESTEDCOMMENT",
    "BIG_ARROW",
    "SMALL_ARROW",
    "INT",
    "FLOAT",
    "BACKSLASH",
    "PLUS",
    "IS_SUBTYPE",
    "MINUS",
    "MINUS_NEW",
    "LPAREN",
    "LPAREN_NEW",
    "LSQUARE",
    "LSQUARE_NEW",
    "MINUS_TILDE",
    "MINUS_TILDE_NEW",
] + list(set(reserved.values()))

literals = ":()[]{}=.!@|,;^?<>~*/%#&"
HEX = r'[0-9a-zA-Z]'
HEX_ESC = f"(\\\\x{HEX}{{2}})"
UNICODE_ESC = f"(\\\\u{HEX}{{4}})"
UNICODE2_ESC = f"(\\\\U{HEX}{{6}})"
ESC = (r'((\\(a|b|e|f|n|r|t|v|\\|0))|(\\t) '
       + f'{HEX_ESC}|{UNICODE_ESC}|{UNICODE2_ESC})')
SINGLE_STRING_CHARS = r'((\\")|' + ESC + '|[^"])*'
TRIPLE_STRING_CHARS = r'(' + ESC + '|[^"]|("(?="""))|("(?!"")))*'
TRIPLE_STRING = r'("""' + TRIPLE_STRING_CHARS + r'""")'
SINGLE_STRING = r'("' + SINGLE_STRING_CHARS + '")'
STRING = f"{TRIPLE_STRING} | {SINGLE_STRING}"

CHAR_CHAR = r"((\\')|[^\\']|" + ESC + ")"

LETTER = r'[a-zA-Z]'
DIGIT = r'[0-9]'

ID = f"({LETTER}|_) ({LETTER}|{DIGIT}|_|')*"

NEWLINE = r'(\n(\r|\s)*)'
WS = f"({ NEWLINE }) | \\s+"

NESTEDCOMMENT = r'/\* ( [^*] | \*(?!/) )* \*/'
t_LINECOMMENT = r'//[^\n]+'

LPAREN_NEW = f'( {NEWLINE} \\( )'
LPAREN = r'\('
LSQUARE_NEW = f'( {NEWLINE} \\[ )'
LSQUARE = r'\['
MINUS_NEW = f' {NEWLINE} -'
MINUS = '-'
MINUS_TILDE = '-~'
MINUS_TILDE_NEW = f' {NEWLINE} -~'

t_BIG_ARROW = r'=>'
SMALL_ARROW = r'->'
t_BACKSLASH = r'\\'
t_PLUS = r'\+'
t_IS_SUBTYPE = '<:'

EXP = f'(e|E)(\\+|-)?({DIGIT}|_)+'
FLOAT = f'{DIGIT}({DIGIT}|_)*(\.{DIGIT}({DIGIT}|_)*)?({EXP})?'

DEC_INT = f"({DIGIT}({DIGIT}|_)*(?![.eE]))"
HEX_INT = f"(0x[0-9a-fA-F_]+)"
BIN_INT = f"(0b[01_]+)"
CHAR_INT = f"('{CHAR_CHAR}')"
INT = f"{CHAR_INT}|{BIN_INT}|{HEX_INT}|{DEC_INT}"

t_GENCAP = "(\\#{})".format(")|(\\#".join(["read", "send", "share", "alias", "any"]))


@TOKEN(STRING)
def t_STRING(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(NESTEDCOMMENT)
def t_NESTEDCOMMENT(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(INT)
def t_INT(t):
    return t


@TOKEN(FLOAT)
def t_FLOAT(t):
    return t


@TOKEN(LPAREN_NEW)
def t_LPAREN_NEW(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(LPAREN)
def t_LPAREN(t):
    return t


@TOKEN(LSQUARE_NEW)
def t_LSQUARE_NEW(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(LSQUARE)
def t_LSQUARE(t):
    return t


@TOKEN(SMALL_ARROW)
def t_SMALL_ARROW(t):
    return t


@TOKEN(MINUS_TILDE_NEW)
def t_MINUS_TILDE_NEW(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(MINUS_TILDE)
def t_MINUS_TILDE(t):
    return t


@TOKEN(MINUS_NEW)
def t_MINUS_NEW(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(MINUS)
def t_MINUS(t):
    return t


@TOKEN(WS)
def t_WS(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(ID)
def t_ID(t):
    t.type = reserved.get(t.value, "ID")
    return t


def t_error(t):
    raise LexError("Error at line {}: {}".format(
        t.lexer.lineno, repr(t.lexer.lexdata[t.lexer.lexpos])), "")


raw_lexer = plylex()


def lex_raw(input):
    """return a raw lexer, loaded with data"""
    if isinstance(input, IOBase):
        data = input.read()
    else:
        data = input
    clone = raw_lexer.clone()
    clone.input(data)
    return clone


class Lexer():
    def __init__(self):
        self._lexer = None

    def input(self, input):
        self._lexer = lex_raw(input)

    def token(self):
        t = self._lexer.token()
        if t is not None and t.type in (
                "WS", "NEWLINE", "LINECOMMENT", "NESTEDCOMMENT"):
            return self.token()
        return t
