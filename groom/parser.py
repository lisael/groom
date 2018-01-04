import ply.yacc as yacc
from groom.lexer import tokens  # noqa needed by yacc.yacc
from groom import ast
from groom.ast import nodes


def p_module(p):
    """
    module : STRING uses class_defs
           | uses class_defs
    """
    if len(p) == 4:
        p[0] = ast.ModuleNode(docstring=p[1], uses=p[2], class_defs=p[3])
    else:
        p[0] = ast.ModuleNode(uses=p[1], class_defs=p[2])


def p_anyparen(p):
    """
    anylparen : LPAREN
              | LPAREN_NEW
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
    if isinstance(p[2][1], ast.FFIDeclNode):
        p[0] = ast.UseNode(
                id=p[2][0],
                ffidecl=p[2][1],
                guard=p[3]
                )
    else:
        p[0] = ast.UseNode(
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
    p[0] = ast.FFIDeclNode(id=p[2], typeargs=p[3], params=p[4], partial=p[5])


def p_typeargs(p):
    """
    typeargs : '[' typearglist ']'
    """
    p[0] = nodes.TypeArgs(typeargs=p[2])


def p_typearglist(p):
    """
    typearglist : typearg
                | typearg ',' typearglist
    """
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]


def p_id_or_string(p):
    """
    id_or_string : id
                 | STRING
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
    typeparams : '[' typeparams_list ']'
    """
    p[0] = p[2]


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
    typeparam : typed_id '=' typearg
    """
    if len(p) == 2:
        p[0] = (p[1][0], p[1][1], None)
    else:
        p[0] = (p[1][0], p[1][1], p[3])


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
    p[0] = ast.TrueNode(p[1])


def p_false(p):
    """
    false : FALSE
    """
    p[0] = ast.FalseNode(p[1])


def p_int(p):
    """
    int : INT
    """
    p[0] = ast.IntNode(p[1])


def p_float(p):
    """
    float : FLOAT
    """
    p[0] = ast.FloatNode(p[1])


def p_string(p):
    """
    string : STRING
    """
    p[0] = ast.StringNode(p[1])


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


def p_class_decl(p):
    """
    class_decl : class_decl_1 IS type
               | class_decl_1
    """
    if len(p) == 2:
        p[0] = p[1] + (None,)
    else:
        p[0] = p[1] + (nodes.ProvidesNode(type=p[3]),)


def p_class_decl_1(p):
    """
    class_decl_1 : CLASS_DECL annotation cap parametrised_id
    """
    p[0] = (p[1], p[2], p[3], p[4][0], p[4][1])


def p_docstring(p):
    """
    docstring : STRING
              | empty
    """
    p[0] = p[1]


class_nodes = {
    "type": ast.TypeNode,
    "class": ast.ClassNode,
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
        "var": ast.VarFieldNode,
        "let": ast.LetFieldNode,
        "embed": ast.EmbedFieldNode
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


def p_vardecl(p):
    """
    vardecl : varkw id maybe_typed
    """
    p[0] = (p[1], p[2], p[3])


def p_pattern(p):
    """
    pattern : vardecl
            | parampattern
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
    p[0] = p[1] if isinstance(p[1], ast.Node) else ast.ReferenceNode(id=p[1])


def p_if(p):
    """
    if : IF annotatedrawseq THEN rawseq if_else END
    """
    p[0] = ast.IfNode(
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
    p[0] = (None, ast.IfNode(
            annotations=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5][1],
            else_annotations=p[5][0]))


def p_ifdef(p):
    """
    ifdef : IFDEF annotation infix THEN rawseq ifdef_else END
    """
    p[0] = ast.IfdefNode(
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
    elseifdef : ELSEIF annotation infix THEN rawseq ifdef_else
    """
    p[0] = (None, ast.IfdefNode(
            annotations=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0]))


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
    elseiftype : ELSEIF annotation type_assertion THEN rawseq iftype_else
    """
    p[0] = (None, ast.IftypeNode(
            annotations=p[2],
            assertion=p[3],
            members=p[5],
            else_=p[6][1],
            else_annotations=p[6][0],
    ))


def p_match(p):
    """
    match : MATCH annotation rawseq caseexpr_list else END
    """
    p[0] = ast.MatchNode(
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
    caseexpr : '|' annotation maybe_pattern guard match_action
    """
    p[0] = ast.CaseNode(
            annotations=p[2],
            pattern=p[3],
            guard=p[4],
            action=p[5]
    )


def p_while(p):
    """
    while : WHILE annotatedrawseq DO rawseq else END
    """
    p[0] = ast.WhileNode(
            annotations=p[2][0],
            assertion=p[2][1],
            members=p[4],
            else_=p[5][1],
            else_annotations=p[5][0])


def p_repeat(p):
    """
    repeat : REPEAT rawseq UNTIL annotatedrawseq else END
    """
    p[0] = ast.RepeatNode(
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
    for : FOR annotation idseq IN rawseq DO rawseq else END
    """
    p[0] = ast.ForNode(
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
    with : WITH annotation withelem_list DO rawseq else END
    """
    p[0] = ast.WithNode(
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
    try : TRY annotation rawseq else_then END
    """
    p[0] = ast.TryNode(
        annotations=p[2],
        members=p[3],
        else_=p[4][0][1],
        else_annotations=p[4][0][0],
        then=p[4][1][1],
        then_annotations=p[4][1][0],
    )


def p_recover(p):
    """
    recover : RECOVER annotation cap rawseq END
    """
    p[0] = ast.RecoverNode(
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
    p[0] = ast.ConsumeNode(cap=p[2], term=p[3])


def p_nextterm(p):
    """
    nextterm : id
             | literal
    """
    # TODO
    p[0] = p[1]


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
    p[0] = method_kinds[p[1][0]](annotations=p[1][1],
                                 capability=p[2], id=p[3][0],
                                 typeparams=p[3][1],
                                 params=p[4],
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
    params : anylparen param_list ')'
           | anylparen ')'
    """
    p[0] = ast.ParamsNode(params=p[2]) if len(p) == 4 else ast.ParamsNode(params=[])


def p_param(p):
    """
    param : param_1
          | param_1 '=' infix
    """
    default = p[3] if len(p) == 4 else None
    id = p[1][0]
    if isinstance(id, nodes.ReferenceNode):
        id = id.id
    p[0] = ast.ParamNode(id=id, type=p[1][1], default=default)


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


pattern_prefix_node_constructor = {
    'not': ast.NotNode,
    'addressof': ast.AddressofNode,
    '-': ast.NegNode,
    '-~': ast.NegUnsafeNode,
    'digestof': ast.DigestOfNode
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


atomsuffix_classes = {
    '.': ast.DotNode,
    'call': ast.CallNode,
}


def p_postfix(p):
    """
    postfix : atom atomsuffix_list
    """
    result = p[1]
    if isinstance(result, nodes.IdNode):
        result = ast.ReferenceNode(id=result)
    for s in p[2]:
        if s[0] == '.':
            result = nodes.DotNode(first=result, second=s[1])
        elif s[0] == 'call':
            result = nodes.CallNode(fun=result, positionalargs=s[1],
                                    namedargs=s[2], is_partial=s[3])
        elif s[0] == 'qualify':
            result = nodes.QualifyNode(type=result, args=s[1])
    p[0] = result


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
    p[0] = ('call', ast.PositionalArgsNode(args=p[2]),
            ast.NamedArgsNode(args=p[3]), p[5])


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
    p[0] = ast.NamedArgNode(id=p[1], value=p[3])


def p_this(p):
    """
    this : THIS
    """
    p[0] = ast.ThisNode()


def p_atom(p):
    """
    atom : id
         | this
         | literal
    """
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
    if isinstance(p[1], list):
        p[0] = ast.SeqNode(p[1])
    else:
        p[0] = ast.SeqNode([p[1]])


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
    if len(p) == 4:
        p[0] = (p[1], p[3])
    else:
        p[0] = p[1]


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
