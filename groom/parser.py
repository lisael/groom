import ply.yacc as yacc
from groom.lexer import tokens  # noqa needed by yacc.yacc
from groom import ast


def p_module(p):
    """
    module : STRING uses class_defs
    module : uses class_defs
    """
    if len(p) == 4:
        p[0] = ast.ModuleNode(docstring=p[1], uses=p[2], class_defs=p[3])
    else:
        p[0] = ast.ModuleNode(uses=p[1], class_defs=p[2])


def p_empty(p):
    """
    empty :
    """
    p[0] = None


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
    use : USE used useif
    """
    if isinstance(p[2][1], list):
        # ffi. TODO
        pass
    else:
        p[0] = ast.UseNode(
                alias=p[2][0],
                package=p[2][1],
                condition=p[3]
                )


def p_useif(p):
    """
    useif : IF infix
          | empty
    """
    p[0] = p[2] if len(p) == 3 else None


def p_used(p):
    """
    used : used_id STRING
         | used_id use_ffi
    """
    p[0] = (p[1], p[2])


def p_used_id(p):
    """
    used_id : ID '='
            | empty
    """
    p[0] = p[1]


def p_use_ffi(p):
    """
    use_ffi : '@' id_or_string typeargs LPAREN params ')' maybe_partial
    """
    p[0] = (p[2], p[3], p[5], p[7])


def p_typeargs(p):
    """
    typeargs : '[' typearglist ']'
    """
    p[0] = p[2]


def p_typearglist(p):
    """
    typearglist : typearg
                | typearg ',' typearglist
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_id_or_string(p):
    """
    id_or_string : ID
                 | STRING
    """
    p[0] = p[1]


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
    """
    p[0] = (p[1], p[2], p[3], p[4][0], p[4][1])


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
               |
    """
    if len(p) == 1:
        p[0] = []
    else:
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


def p_pattern(p):
    """
    pattern : ID
            | literal
    """
    # TODO
    p[0] = p[1]


def p_term(p):
    """
    term : if
         | ifdef
         | iftype
         | match
         | while
         | repeat
         | for
         | with
         | try
         | recover
         | consume
         | pattern
    """
    # TODO
    p[0] = p[1]


def p_if(p):
    """
    if : IF annotatedrawseq THEN rawseq if_else END
    """
    p[0] = ast.IfNode(
            annotation=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5])


def p_if_else(p):
    """
    if_else : elseif
            | else
    """
    p[0] = p[1]


def p_elseif(p):
    """
    elseif : ELSEIF annotatedrawseq THEN rawseq if_else
    """
    p[0] = ast.ElseifNode(
            annotation=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5])


def p_ifdef(p):
    """
    ifdef : IFDEF annotation infix THEN rawseq ifdef_else END
    """
    p[0] = ast.IfdefNode(
            annotation=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6]
    )


def p_ifdef_else(p):
    """
    ifdef_else : else
               | elseifdef
    """
    p[0] = p[1]


def p_elseifdef(p):
    """
    elseifdef : ELSEIF annotation infix THEN rawseq ifdef_else
    """
    p[0] = ast.ElseifdefNode(
            annotation=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6]
    )


def p_type_assertion(p):
    """
    type_assertion : type IS_SUBTYPE type
    """
    p[0] = ast.TypeAssertionNode(
                  child_type=p[1],
                  parent_type=p[3]
    )


def p_iftype(p):
    """
    iftype : IFTYPE annotation type_assertion THEN rawseq iftype_else END
    """
    p[0] = ast.IftypeNode(
            annotation=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6]
    )


def p_iftype_else(p):
    """
    iftype_else : else
                | elseiftype
    """
    p[0] = p[1]


def p_elseiftype(p):
    """
    elseiftype : ELSEIF annotation type_assertion THEN rawseq iftype_else
    """
    p[0] = ast.ElseifTypeNode(
            annotation=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6]
    )


def p_match(p):
    """
    match : MATCH annotation rawseq caseexpr_list else END
    """
    p[0] = ast.MatchNode(
            annotation=p[2],
            matchseq=p[3],
            cases=p[4],
            else_=p[5]
    )


def p_caseexpr_list(p):
    """
    caseexpr_list : caseexpr caseexpr_list
                  | caseexpr
                  |
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_maybe_pattern(p):
    """
    maybe_pattern : pattern
                  |
    """
    p[0] = p[1] if len(p) == 2 else None


def p_match_action(p):
    """
    match_action : BIG_ARROW rawseq
    """
    p[0] = p[2]


def p_caseexpr(p):
    """
    caseexpr : '|' annotation maybe_pattern guard match_action
    """
    p[0] = ast.CaseNode(
            annotation=p[2],
            pattern=p[3],
            guard=p[4],
            action=p[5]
    )


def p_while(p):
    """
    while : WHILE annotatedrawseq DO rawseq else END
    """
    p[0] = ast.WhileNode(
            annotation=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5])


def p_repeat(p):
    """
    repeat : REPEAT rawseq UNTIL annotatedrawseq else END
    """
    p[0] = ast.RepeatNode(
            annotation=p[4][0],
            assertion=p[4][1],
            members=p[2],
            else_=p[5])


def p_then(p):
    """
    then : THEN annotatedrawseq
         |
    """
    p[0] = p[2] if len(p) == 3 else None


def p_for(p):
    """
    for : FOR annotation idseq IN rawseq DO rawseq else END
    """
    p[0] = ast.ForNode(
            annotation=p[2],
            ids=p[3],
            sequence=p[5],
            members=p[7],
            else_=p[8]
    )


def _flatten_idseq(seq):
    result = []
    for item in seq:
        if isinstance(item, list):
            if len(item) > 1:
                item = _flatten_idseq(item)
                result.append(item)
            else:
                result.append(item[0])
        else:
            result.append(item)
    return result


def p_idseq(p):
    """
    idseq : ID
          | LPAREN idseq_list ')'
    """
    idseq = [p[1]] if len(p) == 2 else p[2]
    p[0] = _flatten_idseq(idseq)


def p_idseq_list(p):
    """
    idseq_list : idseq
               | idseq ',' idseq_list
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_with(p):
    """
    with : WITH annotation with_elem_list DO rawseq else END
    """
    p[0] = ast.WithNode(
            annotation=p[2],
            elems=p[3],
            members=p[5],
            else_=p[6]
    )


def p_with_elem_list(p):
    """
    with_elem_list : with_elem ',' with_elem_list
                   | with_elem
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_with_elem(p):
    """
    with_elem : idseq '=' rawseq
    """
    p[0] = (p[1], p[3])


def p_else_then(p):
    """
    else_then : else then
    """
    p[0] = (p[1], p[2])


def p_try(p):
    """
    try : TRY annotation rawseq else_then END
    """
    p[0] = ast.TryNode(
        annotation=p[2],
        members=p[3],
        else_=p[4][0],
        then=p[4][1]
    )


def p_recover(p):
    """
    recover : RECOVER annotation cap rawseq END
    """
    p[0] = ast.RecoverNode(
            annotation=p[2],
            capability=p[3],
            members=p[4])


def p_else(p):
    """
    else : ELSE annotatedrawseq
         |
    """
    p[0] = p[2] if len(p) == 3 else None


def p_consume(p):
    """
    consume : CONSUME cap term
    """
    p[0] = ast.ConsumeNode(capability=p[2], term=p[3])


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
    """
    p[0] = (p[1], p[2])


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
    """
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
    yacc.yacc()  # pragma: no cover
