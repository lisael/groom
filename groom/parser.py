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
        p[0] = [p[2]] + p[3]
    else:
        p[0] = [p[2]]


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
                 | CLASS_DECL cap parametrised_id
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


class_nodes = {
    "type": ast.TypeNode,
    "class": ast.ClassNode
}


def p_class_def(p):
    """
    class_def : class_decl docstring members
    class_def : class_decl docstring
    """
    members = [] if len(p) == 3 else p[3]
    p[0] = class_nodes[p[1][0]](
            annotation=p[1][1],
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
    members : methods
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_fields(p):
    """
    fields : field fields
    fields : field
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


field_classes = {
        "var": ast.VarFieldNode,
        "let": ast.LetFieldNode,
        "embed": ast.EmbedFieldNode
        }


def p_field(p):
    """
    field : field_decl ID ':' type '=' infix
    field : field_decl ID ':' type
    """
    # p[0] = p[1]
    if len(p) == 7:
        p[0] = field_classes[p[1]](id=p[2], type=p[4], default=p[6])
    else:
        p[0] = field_classes[p[1]](id=p[2], type=p[4])


def p_field_decl(p):
    """
    field_decl : LET
               | VAR
               | EMBED
    """
    p[0] = p[1]


def p_infix(p):
    """
    infix : term op_list
          | term
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], None)


def p_nextinfix(p):
    """
    nextinfix : nextterm op_list
              | nextterm
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], None)


def p_op_list(p):
    """
    op_list : op op_list
            | op
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_op(p):
    """
    op : AS type
       | binop
       | isop
    """
    # TODO
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_term(p):
    """
    term : ID
         | literal
         | if
    """
    # TODO
    p[0] = p[1]


def p_if(p):
    """
    if : IF annotatedrawseq THEN rawseq END
       | IF annotatedrawseq THEN rawseq else END
    """
    else_ = p[5] if len(p) == 7 else None
    p[0] = (p[2], p[4], else_)


def p_else(p):
    """
    else : elseif
         | ELSE annotatedrawseq
    """


def p_elsif(p):
    """
    elseif : ELSIF annotatedrawseq THEN rawseq END
           | ELSIF annotatedrawseq THEN rawseq else END
    """


def p_nextterm(p):
    """
    nextterm : ID
             | literal
    """
    # TODO
    p[0] = p[1]


def p_isop(p):
    """
    isop : IS term
         | ISNT term
    """
    # TODO
    p[0] = (p[1], p[2])


def p_binop(p):
    """
    binop : binop_op term
          | binop_op '?' term
    """
    # TODO binop node ??
    if len(p) == 3:
        p[0] = (p[1], p[2], False)
    else:
        p[0] = (p[1], p[3], True)


def p_binop_op(p):
    """
    binop_op : AND
             | OR
             | XOR
             | PLUS
             |  '-'
             |  '*'
             |  '/'
             |  '%'
             |  '+' '~'
             |  '-' '~'
             |  '*' '~'
             |  '/' '~'
             |  '%' '~'
             |  '<' '<'
             |  '>' '>'
             |  '<' '<' '~'
             |  '>' '>' '~'
             |  '=' '='
             |  '!' '='
             |  '<'
             |  '<' '='
             |  '>' '='
             |  '>'
             |  '=' '=' '~'
             |  '!' '=' '~'
             |  '<' '~'
             |  '<' '=' '~'
             |  '>' '=' '~'
             |  '>' '~'
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3]


def p_methods(p):
    """
    methods : method methods
            | method
            |
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_meth_cap(p):
    """
    meth_cap : '@'
             | CAP
             |
    """
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = p[1]


method_kinds = {
    "new": ast.NewMethod,
    "fun": ast.FunMethod,
    "be": ast.BeMethod
}


def p_meth_decl(p):
    """
    meth_decl : METH_DECL annotation
              | METH_DECL
    """
    p[0] = (p[1], p[2]) if len(p) == 3 else (p[1], None)


def p_method(p):
    """
    method : meth_decl meth_cap parametrised_id params meth_type maybe_partial guard body
    """
    p[0] = method_kinds[p[1][0]](annotation=p[1][1],
                                 capability=p[2], id=p[3][0],
                                 method_parameters=p[3][1],
                                 parameters=p[4],
                                 return_type=p[5],
                                 is_partial=p[6],
                                 guard=p[7],
                                 body=p[8])


def p_body(p):
    """
    body : BIG_ARROW rawseq
         |
    """
    p[0] = None if len(p) == 1 else p[2]


def p_guard(p):
    """
    guard : IF rawseq
          |
    """
    p[0] = None if len(p) == 1 else p[2]


def p_maybe_partial(p):
    """
    maybe_partial : '?'
                  |
    """
    p[0] = len(p) == 2


def p_meth_type(p):
    """
    meth_type : ':' type
              |
    """
    p[0] = p[2] if len(p) == 3 else None


def p_params(p):
    """
    params : LPAREN param_list ')'
           | LPAREN ')'
    """
    p[0] = p[2] if len(p) == 4 else []


def p_param(p):
    """
    param : param_1
          | param_1 '=' infix
    """
    infix = p[3] if len(p) == 4 else None
    p[0] = (p[1][0], p[1][1], infix)


def p_param_1(p):
    """
    param_1 : parampattern
            | parampattern ':' type
    """
    tp = p[3] if len(p) == 4 else None
    p[0] = (p[1], tp)


def p_parampattern(p):
    """
    parampattern : ID
    """
    # TODO: see parampattern in antlr...
    p[0] = p[1]


def p_param_list(p):
    """
    param_list : param ',' param_list
               | param
    """
    p[0] = [p[1]] + p[3] if len(p) == 4 else [p[1]]


def p_rawseq(p):
    """
    rawseq : exprseq
           | jump
    """
    p[0] = p[1]


def p_annotatedrawseq(p):
    """
    annotatedrawseq : annotation rawseq
                    | rawseq
    """
    if len(p) == 2:
        p[0] = (None, p[1])
    else:
        p[0] = (p[1], p[2])


def p_exprseq(p):
    """
    exprseq : assignment
            | assignment semiexpr
            | assignment nosemi
    """
    next_ = [] if len(p) == 2 else p[2]
    p[0] = [p[1]] + next_


def p_nextexprseq(p):
    """
    nextexprseq : nextassignment
                | nextassignment semiexpr
                | nextassignment nosemi
    """
    p_exprseq(p)


def p_semiexpr(p):
    """
    semiexpr : ';' exprseq
             | ';' jump
    """
    p[0] = p[2]


def p_nosemi(p):
    """
    nosemi : nextexprseq
           | jump
    """
    p[0] = p[1]


def p_assignment(p):
    """
    assignment : infix
               | infix '=' assignment
    """
    assignment = None if len(p) == 2 else p[3]
    p[0] = (p[1], assignment)


def p_nextassignment(p):
    """
    nextassignment : nextinfix
                   | nextinfix '=' assignment
    """
    p_assignment(p)


def p_jump(p):
    """
    jump : jump_statement
         | jump_statement rawseq
    """
    seq = None if len(p) == 2 else p[2]
    p[0] = [(p[1], seq)]


def p_jump_statement(p):
    """
    jump_statement : RETURN
                   | BREAK
                   | CONTINUE
                   | ERROR
                   | COMPILE_INTRINSIC
                   | COMPILE_ERROR
    """
    p[0] = p[1]


# _parser = yacc.yacc()


class Parser(object):
    def __init__(self, *args, **kwargs):
        self._parser = yacc.yacc(*args, **kwargs)

    def parse(self, *args, **kwargs):
        return self._parser.parse(*args, **kwargs)


if __name__ == "__main__":
    yacc.yacc()
