import ply.yacc as yacc
from groom.lexer import Lexer
from groom.lexer import tokens  # noqa needed by yacc.yacc
from groom import ast
from groom.ast import build_class


def p_module(p):
    """
    module : STRING uses class_defs
    module : uses class_defs
    """
    if len(p) == 4:
        p[0] = ast.ModuleNode(docstring=p[1], uses=p[2], class_defs=p[3])
    else:
        p[0] = ast.ModuleNode(uses=p[1], class_defs=p[2])


def p_uses(p):
    """
    uses : use uses
    uses : use
    uses :
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_use(p):
    """
    use : USE STRING
    use : ID '=' STRING
    """
    p[0] = ast.UseNode(p[2], p[2])


def p_class_defs(p):
    """
    class_defs : class_def class_defs
    class_defs : class_def
    class_defs :
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_class_def(p):
    """
    class_def : CLASS_DECL ID members
    class_def : CLASS_DECL ID
    """
    if len(p) == 4:
        p[0] = build_class(decl=p[1], id=p[2], members=p[3])
    elif len(p) == 3:
        p[0] = build_class(decl=p[1], id=p[2])


def p_members(p):
    """
    members : fields methods
    """
    p[0] = (p[1], p[2])


def p_fields(p):
    """
    fields : field fields
    fields : field
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_field(p):
    """
    field : LET
    """
    p[0] = p[1]


def p_methods(p):
    """
    methods : method methods
    methods : method
    methods :
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_method(p):
    """
    method : METH_DECL
    """
    p[0] = p[1]


_parser = yacc.yacc()


class Parser(object):
    def __init__(self):
        self._parser = _parser

    def parse(self, *args, **kwargs):
        return self._parser.parse(*args, **kwargs)
