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


def p_cap(p):
    """
    cap : CAP
    cap :
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None


def p_typeparams(p):
    """
    typeparams : '[' typeparams_list ']'
    """
    p[0] = p[2]


def p_typeparams_list(p):
    """
    typeparams_list : typeparam ',' typeparams_list
    typeparams_list : typeparam
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_typeparam(p):
    """
    typeparam : typed_id
    typeparam : typed_id '=' typearg
    """
    if len(p) == 2:
        p[0] = (p[1][0], p[1][1], None)
    else:
        p[0] = (p[1][0], p[1][1], p[3])


def p_typearg(p):
    """
    typearg : type
    typearg : literal
    """
    # TODO typearg : '#' postfix
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_literal(p):
    """
    literal : TRUE
    literal : FALSE
    literal : INT
    literal : FLOAT
    literal : STRING
    """
    p[0] = p[1]


def p_typed_id(p):
    """
    typed_id : ID
    typed_id : ID ':' type
    """
    if len(p) == 2:
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[2])


def p_type(p):
    """
    type : atomtype
    type : atomtype SMALL_ARROW type
    """
    if len(p) == 2:
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[3])


def p_atomtype(p):
    """
    atomtype : THIS
    atomtype : CAP
    atomtype : combined_types
    atomtype : nominal
    """
    # TODO
    # atomtype : lambdatype
    # atomtype : barelambdatype
    p[0] = p[1]


def p_nominal(p):
    """
    nominal : dotted typecap
    nominal : dotted
    """
    if len(p) == 2:
        p[0] = p[1] + (None,)
    else:
        p[0] = p[1] + (p[2],)


def p_typecap(p):
    """
    typecap : CAP cap_modifier
    typecap : GENCAP cap_modifier
    typecap : CAP
    typecap : GENCAP
    """
    if len(p) == 2:
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[2])


def p_cap_modifier(p):
    """
    cap_modifier : '^'
    cap_modifier : '!'
    """
    p[0] = p[1]


def p_dotted(p):
    """
    dotted : ID '.' parametrised_id
    dotted : parametrised_id
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = (p[1],) + p[3]


def p_combined_types(p):
    """
    combined_types : LPAREN infixtype tupletype ')'
    combined_types : LPAREN infixtype ')'
    """
    if len(p) == 5:
        p[0] = [p[3]] + p[4]
    else:
        p[0] = [p[3]]


def p_tupletype(p):
    """
    tupletype : ',' infixtype tupletype
    tupletype : ',' infixtype
    """
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = [p[2]]


def p_infixtype(p):
    """
    infixtype : type
    infixtype : type '&' infixtype
    infixtype : type '|' infixtype
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        # TODO
        p[0] = p[1]


def p_parametrised_id(p):
    """
    parametrised_id : ID typeparams
    parametrised_id : ID
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], [])


def p_class_decl(p):
    """
    class_decl : class_decl_1 IS type
    class_decl : class_decl_1
    """
    if len(p) == 2:
        p[0] = p[1] + (None,)
    else:
        p[0] = p[1] + (p[3],)


def p_class_decl_1(p):
    """
    class_decl_1 : CLASS_DECL annotation cap parametrised_id
    class_decl_1 : CLASS_DECL cap parametrised_id
    """
    if len(p) == 5:
        p[0] = (p[1], p[2], p[3], p[4][0], p[4][1])
    else:
        p[0] = (p[1], [], p[2], p[3][0], p[3][1])


def p_docstring(p):
    """
    docstring : STRING
    docstring :
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None


def p_class_def(p):
    """
    class_def : class_decl docstring members
    class_def : class_decl docstring
    """
    if len(p) == 4:
        members = p[3]
    elif len(p) == 3:
        members = []
    p[0] = build_class(
            decl=p[1][0], annotation=p[1][1],
            capability=p[1][2], id=p[1][3],
            type_params=p[1][4], is_=p[1][5],
            docstring=p[2], members=members)


def p_annotation(p):
    r"""
    annotation : BACKSLASH id_list BACKSLASH
    """
    p[0] = p[2]


def p_id_list(p):
    """
    id_list : ID ',' id_list
    id_list : ID
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


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
