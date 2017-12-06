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
    "counsme": "COUNSME",
    "fun": "FUN",
    "be": "BE",
    "new": "NEW",
    "use": "USE",
    "type": "TYPE",
    "interface": "INTERFACE",
    "trait": "TRAIT",
    "primitive": "PRIMITIVE",
    "struct": "STRUCT",
    "class": "CLASS",
    "actor": "ACTOR",
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
    "elsif": "ELSIF",
    "addressof": "ADDRESSOF",
    "digestof": "DIGESTOF",
    "this": "THIS",
    "as": "AS",
    "object": "OBJECT",
    "where": "WHERE",
    "iso": "ISO",
    "trn": "TRN",
    "ref": "REF",
    "val": "VAL",
    "box": "BOX",
    "tag": "TAG",
    "true": "TRUE",
    "false": "FALSE",
}

tokens = [
    "STRING",
    "NEWLINE",
    "WS",
    "ID",
    "LINECOMMENT",
    "NESTEDCOMMENT",
    "LPAREN",
    "BIG_ARROW",
    "INT",
    "FLOAT",
] + list(reserved.values())

literals = ":()[]{}=.-!@|,;^?<>~+*/%#&"
HEX = r'[0-9a-zA-Z]'
HEX_ESC = f"(\\\\x{HEX}{{2}})"
UNICODE_ESC = f"(\\\\u{HEX}{{4}})"
UNICODE2_ESC = f"(\\\\U{HEX}{{6}})"
ESC = r'((\\(a|b|e|f|n|r|t|v|\\|0))|(\\t) ' + f'{HEX_ESC}|{UNICODE_ESC}|{UNICODE2_ESC})'
SINGLE_STRING_CHARS = r'((\\")|' + ESC + '|[^"])*'
TRIPLE_STRING_CHARS = r'('+ ESC + '|[^"]|("(?="""))|("(?!"")))*'
TRIPLE_STRING = r'("""' + TRIPLE_STRING_CHARS + r'""")'
SINGLE_STRING = r'("' + SINGLE_STRING_CHARS + '")'
STRING = f"{TRIPLE_STRING} | {SINGLE_STRING}"

CHAR_CHAR = r"((\\')|[^\\']|" + ESC + ")"

LETTER = r'[a-zA-Z]'
DIGIT = r'[0-9]'

ID = f"({LETTER}|_) ({LETTER}|{DIGIT}|_|')*"

NEWLINE = r'(\n(\r|\s)*)+'
WS = f"({ NEWLINE }) | \\s+"

NESTEDCOMMENT = r'/\* ( [^*] | \*(?!/) )* \*/'
t_LINECOMMENT = r'//[^\n]+'

LPAREN = r'\( | ( {NEWLINE} \( )'
t_BIG_ARROW = r'=>'

EXP = f'(e|E)(\\+|-)?({DIGIT}|_)+'
FLOAT = f'{DIGIT}({DIGIT}|_)*(\.{DIGIT}({DIGIT}|_)*)?({EXP})?'
print(STRING.__repr__())

DEC_INT = f"( {DIGIT} ( {DIGIT} | _ )* )"
HEX_INT = f"(0x[0-9a-zA-Z_]+)"
BIN_INT = f"(0b[01_]+)"
CHAR_INT = f"'{CHAR_CHAR}'"
INT = f"{CHAR_INT} | {BIN_INT} | {HEX_INT} | {DEC_INT}"


@TOKEN(STRING)
def t_STRING(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(NESTEDCOMMENT)
def t_NESTEDCOMMENT(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(FLOAT)
def t_FLOAT(t):
    return t


@TOKEN(INT)
def t_INT(t):
    return t


@TOKEN(LPAREN)
def t_LPAREN(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(WS)
def t_WS(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(NEWLINE)
def t_NEWLINE(t):
    t.lexer.lineno += t.value.count("\n")
    return t


@TOKEN(ID)
def t_ID(t):
    t.type = reserved.get(t.value, "ID")
    return t


def t_error(t):
    import ipdb; ipdb.set_trace()
    raise LexError("Error at line {}: {}".format(t.lexer.lineno, repr(t.lexer.lexdata[t.lexer.lexpos])), "")


_lexer = plylex()


from io import IOBase


def lex(input):
    if isinstance(input, IOBase):
        data = input.read()
    else:
        data = input
    clone = _lexer.clone()
    clone.input(data)
    return clone
