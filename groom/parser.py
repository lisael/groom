import ply.yacc as yacc
from groom.lexer import tokens  # noqa needed by yacc.yacc
from groom.ast import nodes


# Known missing constructs and bugs
#    - lambda
#    - lambdatype
#    - # postfix (???)
#    - empty match case

def p_module(p):
    """
    module : docstring uses class_defs
    """
    if len(p) == 4:
        p[0] = nodes.ModuleNode(docstring=p[1], uses=p[2], class_defs=p[3])
    else:
        p[0] = nodes.ModuleNode(uses=p[1], class_defs=p[2])


# def p_error(p):
#     import ipdb; ppp=p; ipdb.set_trace()


def p_anyparen(p):
    """
    anylparen : LPAREN
              | LPAREN_NEW
    """


def p_anysquare(p):
    """
    anysquare : LSQUARE
              | LSQUARE_NEW
    """


def p_empty(p):
    """
    empty :
    """
    p[0] = None


def p_id(p):
    """
    id : ID
    """
    p[0] = nodes.IdNode(id=p[1])


def p_uses(p):
    """
    uses : use uses
         | use
         |
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
    if isinstance(p[2][1], nodes.FFIDeclNode):
        p[0] = nodes.UseNode(
                id=p[2][0],
                ffidecl=p[2][1],
                guard=p[3]
                )
    else:
        p[0] = nodes.UseNode(
                id=p[2][0],
                package=p[2][1],
                guard=p[3]
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
    used_id : id '='
            | empty
    """
    p[0] = p[1]


def p_use_ffi(p):
    """
    use_ffi : '@' id_or_string typeargs params maybe_partial
    """
    p[0] = nodes.FFIDeclNode(id=p[2], typeargs=p[3], params=p[4], partial=p[5])


def p_typeargs(p):
    """
    typeargs : LSQUARE typearglist ']'
    """
    p[0] = nodes.TypeArgs(typeargs=p[2])


def p_maybe_typeargs(p):
    """
    maybe_typeargs : typeargs
                   | empty
    """
    p[0] = p[1]


def p_typearglist(p):
    """
    typearglist : typearg
                | typearg ',' typearglist
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_id_or_string(p):
    """
    id_or_string : id
                 | string
    """
    p[0] = p[1]


def p_class_defs(p):
    """
    class_defs : class_def class_defs
               | class_def
               |
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
        | empty
    """
    p[0] = p[1]


def p_typeparams(p):
    """
    typeparams : LSQUARE typeparams_list ']'
    """
    p[0] = nodes.TypeParamsNode(members=p[2])


def p_typeparams_list(p):
    """
    typeparams_list : typeparam ',' typeparams_list
                    | typeparam
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_typeparam(p):
    """
    typeparam : typed_id
              | typed_id '=' typearg
    """
    if len(p) == 2:
        p[0] = nodes.TypeParamNode(id=p[1][0], type=p[1][1])
    else:
        p[0] = nodes.TypeParamNode(id=p[1][0], type=p[1][1], typearg=p[3])


def p_typearg(p):
    """
    typearg : type
            | literal
            | '#' postfix
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_true(p):
    """
    true : TRUE
    """
    p[0] = nodes.TrueNode(p[1])


def p_false(p):
    """
    false : FALSE
    """
    p[0] = nodes.FalseNode(p[1])


def p_int(p):
    """
    int : INT
    """
    p[0] = nodes.IntNode(p[1])


def p_float(p):
    """
    float : FLOAT
    """
    p[0] = nodes.FloatNode(p[1])


def p_string(p):
    """
    string : STRING
    """
    p[0] = nodes.StringNode(p[1])


def p_literal(p):
    """
    literal : true
            | false
            | int
            | float
            | string
    """
    p[0] = p[1]


def p_typed_id(p):
    """
    typed_id : id
             | id ':' type
    """
    if len(p) == 2:
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[2])


def p_type(p):
    """
    type : atomtype
         | atomtype SMALL_ARROW type
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = nodes.ArrowNode(origin=p[1], trarget=p[3])


def p_atomtype(p):
    """
    atomtype : THIS
             | CAP
             | combined_types
             | nominal
    """
    # TODO
    # atomtype : lambdatype
    # atomtype : barelambdatype
    p[0] = p[1]


def p_nominal(p):
    """
    nominal : namespaced typecap
    """
    p[0] = nodes.Nominal(
        package=p[1][0],
        id=p[1][1],
        typeargs=p[1][2],
        cap=p[2][0],
        cap_modifier=p[2][1],
    )


def p_typecap(p):
    """
    typecap : CAP cap_modifier
            | GENCAP cap_modifier
            | CAP
            | GENCAP
            | empty
    """
    if len(p) == 2:
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[2])


def p_cap_modifier(p):
    """
    cap_modifier : '^'
                 | '!'
    """
    p[0] = p[1]


def p_namespaced(p):
    """
    namespaced : id '.' typeargs_id
               | typeargs_id
    """
    if len(p) == 2:
        p[0] = (None,) + p[1]
    else:
        p[0] = (p[1],) + p[3]


def p_typeargs_id(p):
    """
    typeargs_id : id typeargs
                | id
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], [])


def p_combined_types(p):
    """
    combined_types : anylparen infixtype tupletype ')'
                   | anylparen infixtype ')'
    """
    if len(p) == 5:
        p[0] = nodes.TupleTypeNode(members=[p[2]] + p[3])
    else:
        p[0] = nodes.TupleTypeNode(members=[p[2]])


def p_tupletype(p):
    """
    tupletype : ',' infixtype tupletype
              | ',' infixtype
    """
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = [p[2]]


def p_infixtype(p):
    """
    infixtype : type
              | type '&' infixtype
              | type '|' infixtype
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        # TODO
        p[0] = p[1]


def p_parametrised_id(p):
    """
    parametrised_id : id typeparams
                    | id
    """
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], [])


def p_provides(p):
    """
    provides : IS type
             |
    """
    p[0] =  None if len(p) == 1 else p[2]


def p_class_decl(p):
    """
    class_decl : CLASS_DECL annotations cap parametrised_id provides
    """
    p[0] = (p[1], p[2], p[3], p[4][0], p[4][1], p[5])


def p_docstring(p):
    """
    docstring : string
              | empty
    """
    p[0] = p[1]


class_nodes = {
    "type": nodes.TypeNode,
    "class": nodes.ClassNode,
    "primitive": nodes.PrimitiveNode,
    "actor": nodes.ActorNode,
    "interface": nodes.InterfaceNode,
    "struct": nodes.StructNode,
    "trait": nodes.TraitNode,
}


def p_class_def(p):
    """
    class_def : class_decl docstring members
              | class_decl docstring
    """
    members = [] if len(p) == 3 else p[3]
    p[0] = class_nodes[p[1][0]](
            annotations=p[1][1],
            cap=p[1][2],
            id=p[1][3],
            type_params=p[1][4],
            provides=p[1][5],
            docstring=p[2], members=members)


def p_annotations(p):
    r"""
    annotations : BACKSLASH id_list BACKSLASH
                |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[2]


def p_id_list(p):
    """
    id_list : id ',' id_list
            | id
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_members(p):
    """
    members : fields methods
            | methods
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_fields(p):
    """
    fields : field fields
           | field
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


field_classes = {
        "var": nodes.VarFieldNode,
        "let": nodes.LetFieldNode,
        "embed": nodes.EmbedFieldNode
        }


def p_field(p):
    """
    field : varkw id ':' type '=' infix
          | varkw id ':' type
    """
    # p[0] = p[1]
    if len(p) == 7:
        p[0] = field_classes[p[1]](id=p[2], type=p[4], default=p[6])
    else:
        p[0] = field_classes[p[1]](id=p[2], type=p[4])


def p_varkw(p):
    """
    varkw : LET
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
        result = p[1]
        for op in p[2]:
            result = op(result)
        p[0] = result
    else:
        p[0] = p[1]


def p_nextinfix(p):
    """
    nextinfix : nextterm op_list
              | nextterm
    """
    p_infix(p)


def p_op_list(p):
    """
    op_list : op op_list
            | op
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


class OperatorFactory(object):
    def __init__(self, operator, term, partial=False):
        self.operator = operator
        self.term = term
        self.partial = partial

    def __call__(self, first):
        if self.operator == "as":
            return nodes.AsNode(term=first, type=self.term)
        elif self.operator == "=":
            return nodes.AssignNode(first=first, second=self.term)
        else:
            return nodes.BinOpNode(operator=self.operator, first=first,
                                   second=self.term, is_partial=self.partial)


def p_op(p):
    """
    op : AS type
       | binop
       | isop
    """
    # TODO
    if len(p) == 3:
        p[0] = OperatorFactory("as", p[2])
    else:
        p[0] = p[1]


def p_mabetyped(p):
    """
    maybe_typed : ':' type
                |
    """
    p[0] = p[2] if len(p) == 3 else None


vardecl_classes = {
        "var": nodes.VarNode,
        "let": nodes.LetNode,
        }


def p_vardecl(p):
    """
    vardecl : varkw id maybe_typed
    """
    p[0] = vardecl_classes[p[1]](id=p[2], type=p[3])


def p_pattern(p):
    """
    pattern : vardecl
            | parampattern
    """
    p[0] = p[1]


def p_nextpattern(p):
    """
    nextpattern : vardecl
                | nextparampattern
    """
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
    p[0] = p[1] if isinstance(p[1], nodes.Node) else nodes.ReferenceNode(id=p[1])


def p_nextterm(p):
    """
    nextterm : if
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
             | nextpattern
    """
    # TODO
    p_term(p)


def p_if(p):
    """
    if : IF annotatedrawseq THEN rawseq if_else END
    """
    p[0] = nodes.IfNode(
            annotations=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5][1],
            else_annotations=p[5][0])


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
    p[0] = (None, nodes.IfNode(
            annotations=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5][1],
            else_annotations=p[5][0]))


def p_ifdef(p):
    """
    ifdef : IFDEF annotations infix THEN rawseq ifdef_else END
    """
    p[0] = nodes.IfdefNode(
            annotations=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0]
    )


def p_ifdef_else(p):
    """
    ifdef_else : else
               | elseifdef
    """
    p[0] = p[1]


def p_elseifdef(p):
    """
    elseifdef : ELSEIF annotations infix THEN rawseq ifdef_else
    """
    p[0] = (None, nodes.IfdefNode(
            annotations=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0]))


def p_type_assertion(p):
    """
    type_assertion : type IS_SUBTYPE type
    """
    p[0] = nodes.TypeAssertionNode(
                  child_type=p[1],
                  parent_type=p[3]
    )


def p_iftype(p):
    """
    iftype : IFTYPE annotations type_assertion THEN rawseq iftype_else END
    """
    p[0] = nodes.IftypeNode(
            annotations=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0],
    )


def p_iftype_else(p):
    """
    iftype_else : else
                | elseiftype
    """
    p[0] = p[1]


def p_elseiftype(p):
    """
    elseiftype : ELSEIF annotations type_assertion THEN rawseq iftype_else
    """
    p[0] = (None, nodes.IftypeNode(
            annotations=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0],
    ))


def p_match(p):
    """
    match : MATCH annotations rawseq caseexpr_list else END
    """
    p[0] = nodes.MatchNode(
            annotations=p[2],
            seq=p[3],
            cases=p[4],
            else_=p[5][1],
            else_annotations=p[5][0]
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
    caseexpr : '|' annotations maybe_pattern guard match_action
    """
    p[0] = nodes.CaseNode(
            annotations=p[2],
            pattern=p[3],
            guard=p[4],
            action=p[5]
    )


def p_while(p):
    """
    while : WHILE annotatedrawseq DO rawseq else END
    """
    p[0] = nodes.WhileNode(
            annotations=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5][1],
            else_annotations=p[5][0])


def p_repeat(p):
    """
    repeat : REPEAT rawseq UNTIL annotatedrawseq else END
    """
    p[0] = nodes.RepeatNode(
            annotations=p[4][0],
            assertion=p[4][1],
            members=p[2],
            else_=p[5][1],
            else_annotations=p[5][0])


def p_then(p):
    """
    then : THEN annotatedrawseq
         |
    """
    p[0] = p[2] if len(p) == 3 else (None, None)


def p_for(p):
    """
    for : FOR annotations idseq IN rawseq DO rawseq else END
    """
    p[0] = nodes.ForNode(
            annotations=p[2],
            ids=p[3],
            sequence=p[5],
            members=p[7],
            else_=p[8][1],
            else_annotations=p[8][0]
    )


def _flatten_idseq(seq):
    result = []
    for item in seq:
        if isinstance(item, nodes.TupleNode):
            if len(item.members) > 1:
                item = _flatten_idseq(item.members)
                result.append(item)
            else:
                result.append(item.members[0])
        else:
            result.append(item)
    return nodes.TupleNode(members=result)


def p_idseq(p):
    """
    idseq : id
          | anylparen idseq_list ')'
    """
    idseq = [nodes.LetNode(id=p[1])] if len(p) == 2 else p[2]
    p[0] = _flatten_idseq(idseq)


def p_idseq_list(p):
    """
    idseq_list : idseq
               | idseq ',' idseq_list
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_with(p):
    """
    with : WITH annotations withelem_list DO rawseq else END
    """
    p[0] = nodes.WithNode(
            annotations=p[2],
            elems=nodes.SeqNode(seq=p[3]),
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0]
    )


def p_withelem_list(p):
    """
    withelem_list : withelem ',' withelem_list
                  | withelem
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_withelem(p):
    """
    withelem : idseq '=' rawseq
    """
    members = p[1].members
    idseq = p[1]
    if len(members) == 1 and isinstance(members[0], nodes.LetNode):
        idseq = members[0]
    p[0] = nodes.SeqNode(seq=[idseq, p[3]])


def p_else_then(p):
    """
    else_then : else then
    """
    p[0] = (p[1], p[2])


def p_try(p):
    """
    try : TRY annotations rawseq else_then END
    """
    p[0] = nodes.TryNode(
        annotations=p[2],
        members=p[3],
        else_=p[4][0][1],
        else_annotations=p[4][0][0],
        then=p[4][1][1],
        then_annotations=p[4][1][0],
    )


def p_recover(p):
    """
    recover : RECOVER annotations cap rawseq END
    """
    p[0] = nodes.RecoverNode(
            annotations=p[2],
            cap=p[3],
            members=p[4])


def p_else(p):
    """
    else : ELSE annotatedrawseq
         |
    """
    p[0] = p[2] if len(p) == 3 else (None, None)


def p_consume(p):
    """
    consume : CONSUME cap term
    """
    p[0] = nodes.ConsumeNode(cap=p[2], term=p[3])


def p_isop(p):
    """
    isop : IS term
         | ISNT term
    """
    p[0] = OperatorFactory(p[1], p[2])


def p_binop(p):
    """
    binop : binop_op term
          | binop_op '?' term
          | '=' infix
    """
    if len(p) == 3:
        p[0] = OperatorFactory(p[1], p[2], False)
    else:
        p[0] = OperatorFactory(p[1], p[3], True)


def p_binop_op(p):
    """
    binop_op : AND
             | OR
             | XOR
             | PLUS
             | MINUS
             |  '*'
             |  '/'
             |  '%'
             |  '+' '~'
             |  MINUS_TILDE
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
    "new": nodes.NewMethod,
    "fun": nodes.FunMethod,
    "be": nodes.BeMethod
}


def p_meth_decl(p):
    """
    meth_decl : METH_DECL annotations
    """
    p[0] = (p[1], p[2])


def p_method(p):
    """
    method : meth_decl meth_cap parametrised_id params meth_type  maybe_partial docstring guard body
    """
    p[0] = method_kinds[p[1][0]](annotations=p[1][1],
                                 capability=p[2], id=p[3][0],
                                 typeparams=p[3][1],
                                 params=p[4],
                                 return_type=p[5],
                                 is_partial=p[6],
                                 docstring=p[7],
                                 guard=p[8],
                                 body=p[9])


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
                  | empty
    """
    p[0] = p[1] == '?'


def p_meth_type(p):
    """
    meth_type : ':' type
              |
    """
    p[0] = p[2] if len(p) == 3 else None


def p_params(p):
    """
    params : anylparen param_list ')'
           | anylparen ')'
    """
    p[0] = nodes.ParamsNode(params=p[2]) if len(p) == 4 else nodes.ParamsNode(params=[])


def p_param(p):
    """
    param : param_1
          | param_1 '=' infix
          | '.' '.' '.'
    """
    if p[1] == ".":
        p[0] = nodes.ElipsisNode()
        return
    default = p[3] if len(p) == 4 else None
    id = p[1][0]
    if isinstance(id, nodes.ReferenceNode):
        id = id.id
    p[0] = nodes.ParamNode(id=id, type=p[1][1], default=default)


def p_param_1(p):
    """
    param_1 : parampattern
            | parampattern ':' type
    """
    type = p[3] if len(p) == 4 else None
    p[0] = (p[1], type)


def p_parampattern(p):
    """
    parampattern : parampatternprefix parampattern
                 | postfix
    """
    p[0] = p[1](pattern=p[2]) if len(p) == 3 else p[1]


def p_nextparampattern(p):
    """
    nextparampattern : nextparampatternprefix parampattern
                     | nextpostfix
    """
    p_parampattern(p)


pattern_prefix_node_constructor = {
    'not': nodes.NotNode,
    'addressof': nodes.AddressofNode,
    '-': nodes.NegNode,
    '-~': nodes.NegUnsafeNode,
    'digestof': nodes.DigestOfNode
}


def p_parampatternprefix(p):
    """
    parampatternprefix : NOT
                       | ADDRESSOF
                       | MINUS
                       | MINUS_TILDE
                       | MINUS_NEW
                       | MINUS_TILDE_NEW
                       | DIGESTOF
    """
    p[0] = pattern_prefix_node_constructor[p[1].strip()]


def p_nextparampatternprefix(p):
    """
    nextparampatternprefix : NOT
                           | ADDRESSOF
                           | MINUS_NEW
                           | MINUS_TILDE_NEW
                           | DIGESTOF
    """
    p[0] = pattern_prefix_node_constructor[p[1].strip()]


atomsuffix_classes = {
    '.': nodes.DotNode,
    'call': nodes.CallNode,
}


def p_postfix(p):
    """
    postfix : atom atomsuffix_list
    """
    result = p[1]
    if isinstance(result, nodes.IdNode):
        result = nodes.ReferenceNode(id=result)
    for s in p[2]:
        if s[0] == '.':
            result = nodes.DotNode(first=result, second=s[1])
        elif s[0] == 'call':
            result = nodes.CallNode(fun=result, positionalargs=s[1],
                                    namedargs=s[2], is_partial=s[3])
        elif s[0] == 'qualify':
            result = nodes.QualifyNode(type=result, args=s[1])
    p[0] = result


def p_nextpostfix(p):
    """
    nextpostfix : nextatom atomsuffix_list
    """
    p_postfix(p)


def p_atomsuffix_list(p):
    """
    atomsuffix_list : atomsuffix
                    | atomsuffix atomsuffix_list
                    |
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_atomsuffix(p):
    """
    atomsuffix : dot
               | tilde
               | chain
               | atom_typeargs
               | call
    """
    p[0] = p[1]


def p_atom_typeargs(p):
    """
    atom_typeargs : typeargs
    """
    p[0] = ("qualify", p[1])


def p_dot(p):
    """
    dot : '.' id
    """
    p[0] = (p[1], p[2])


def p_tilde(p):
    """
    tilde : '~' id
    """
    p[0] = (p[1], p[2])


def p_chain(p):
    """
    chain : '.' '>' id
    """
    p[0] = ('.>', p[3])


def p_call(p):
    """
    call : LPAREN  positional named ')' maybe_partial
    """
    p[0] = ('call', nodes.PositionalArgsNode(args=p[2]),
            nodes.NamedArgsNode(args=p[3]), p[5])


def p_positional(p):
    """
    positional : rawseq
               | rawseq ',' positional
               |
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = []


def p_named(p):
    """
    named : WHERE namedarglist
          |
    """
    p[0] = p[2] if len(p) == 3 else []


def p_namedarglist(p):
    """
    namedarglist : namedarg
                 | namedarg ',' namedarglist
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_namedarg(p):
    """
    namedarg : id '=' rawseq
    """
    p[0] = nodes.NamedArgNode(id=p[1], value=p[3])


def p_this(p):
    """
    this : THIS
    """
    p[0] = nodes.ThisNode()


def p_object(p):
    """
    object : OBJECT annotations cap provides members END
    """
    p[0] = nodes.ObjectNode(annotations=p[2],
                            cap=p[3],
                            provides=p[4],
                            members=p[5])


def p_atom(p):
    """
    atom : id
         | this
         | literal
         | tuple
         | array
         | object
         | fficall
    """
    p[0] = p[1]


def p_nextatom(p):
    """
    nextatom : id
             | this
             | literal
             | nexttuple
             | nextarray
             | object
             | fficall
    """
    p[0] = p[1]


def p_array(p):
    """
    array : anysquare arraytype rawseq ']'
    """
    p[0] = nodes.ArrayNode(type=p[2], members=p[3])


def p_nextarray(p):
    """
    nextarray : LSQUARE_NEW arraytype rawseq ']'
    """
    p_array(p)


def p_arraytype(p):
    """
    arraytype : AS type ':'
              | empty
    """
    p[0] = None if len(p) == 2 else p[2]


def p_fficall(p):
    """
    fficall : '@' id_or_string maybe_typeargs anylparen positional named ')' maybe_partial
    """
    p[0] = nodes.FFICallNode(id=p[2],
                             typeargs=p[3],
                             positional=p[5],
                             named=p[6],
                             partial=p[8])


def p_tuple(p):
    """
    tuple : anylparen rawseq tupletail ')'
    """
    p[0] = nodes.TupleNode(members=[p[2]] + p[3])


def p_nexttuple(p):
    """
    nexttuple : LPAREN_NEW rawseq tupletail ')'
    """
    p_tuple(p)


def p_tupletail(p):
    """
    tupletail : empty
              | ',' rawseq tupletail
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]


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
    if isinstance(p[1], list):
        p[0] = nodes.SeqNode(seq=p[1])
    else:
        p[0] = nodes.SeqNode(seq=[p[1]])


def p_annotatedrawseq(p):
    """
    annotatedrawseq : annotations rawseq
    """
    p[0] = (p[1], p[2])


def p_exprseq(p):
    """
    exprseq : infix
            | infix semiexpr
            | infix nosemi
    """
    next_ = [] if len(p) == 2 else p[2]
    if not isinstance(next_, list):
        next_ = [next_]
    p[0] = [p[1]] + next_


def p_nextexprseq(p):
    """
    nextexprseq : nextinfix
                | nextinfix semiexpr
                | nextinfix nosemi
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


def p_jump(p):
    """
    jump : jump_statement empty
         | jump_statement rawseq
    """
    p[0] = p[1](seq=p[2])


def p_jump_statement(p):
    """
    jump_statement : return
                   | break
                   | continue
                   | pony_error
                   | compile_intrinsic
                   | compile_error
    """
    p[0] = p[1]


def p_return(p):
    """
    return : RETURN
    """
    p[0] = nodes.ReturnNode


def p_break(p):
    """
    break : BREAK
    """
    p[0] = nodes.BreakNode


def p_continue(p):
    """
    continue : CONTINUE
    """
    p[0] = nodes.ContinueNode


def p_pony_error(p):
    """
    pony_error : ERROR
    """
    p[0] = nodes.ErrorNode


def p_compile_intrinsic(p):
    """
    compile_intrinsic : COMPILE_INTRINSIC
    """
    p[0] = nodes.CompileIntrinsicNode


def p_compile_error(p):
    """
    compile_error : COMPILE_ERROR
    """
    p[0] = nodes.CompileErrorNode


# _parser = yacc.yacc()


class Parser(object):
    def __init__(self, *args, **kwargs):
        self._parser = yacc.yacc(*args, **kwargs)

    def parse(self, *args, **kwargs):
        return self._parser.parse(*args, **kwargs)


if __name__ == "__main__":
    yacc.yacc()  # pragma: no cover
