class Annotated(object):
    """
    Marker class for annotated nodes
    """
    pass


class Id(object):
    """
    Marker class for nodes with an id
    """
    pass


class Node(object):
    """
    AST node base class
    """

    def __init__(self, **kwargs):
        if isinstance(self, Annotated):
            annotations = kwargs.pop("annotation")
            self.annotations = annotations if annotations else []
        if isinstance(self, Id):
            self.id = kwargs.pop("id")
        if len(kwargs):
            raise(ValueError("Unkown params {}".format(list(kwargs.keys()))))

    def as_dict(self):
        d = dict(node_type=self.node_type)
        if hasattr(self, "annotations"):
            d["annotations"] = self.annotations
        if hasattr(self, "id"):
            d["id"] = self.id
        return d


class DocNode(Node):
    """a Node that holds a docstring"""
    def __init__(self, docstring=None, **kwargs):
        self.docstring = docstring
        super(DocNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(DocNode, self).as_dict(),
                docstring=self.docstring
                )


class ElseNode(Node):
    def __init__(self, else_, **kwargs):
        self.else_ = else_
        super(ElseNode, self).__init__(**kwargs)

    def as_dict(self):
        d = dict(
            super(ElseNode, self).as_dict(),
        )
        if isinstance(self.else_, Node):
            d["else"] = self.else_.as_dict()
        else:
            d["else"] = self.else_
        return d


class ModuleNode(DocNode):
    node_type = "module"

    def __init__(self, name=None, uses=None, class_defs=None, **kwargs):
        self.name = name
        self.uses = uses if uses else []
        self.class_defs = class_defs if class_defs else []
        super(ModuleNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(ModuleNode, self).as_dict(),
                name=self.name,
                uses=[u.as_dict() for u in self.uses],
                class_defs=[c.as_dict() for c in self.class_defs]
                )


class NodeMeta(type):

    def __new__(cls, name, bases, attrs):
        attrs.setdefault("node_attributes", [])
        for base in bases:
            if hasattr(base, "node_attributes"):
                attrs["node_attributes"] += base.node_attributes
        return type.__new__(cls, name, bases, attrs)


def _maybe_as_dict(obj):
    if isinstance(obj, Node):
        return obj.as_dict()
    elif isinstance(obj, list):
        return [_maybe_as_dict(i) for i in obj]
    return obj


class NodeBase(Node, metaclass=NodeMeta):
    def __init__(self, **kwargs):
        for attrname in self.node_attributes:
            setattr(self, attrname, kwargs.pop(attrname, None))

    def as_dict(self):
        result = dict(node_type=self.node_type)
        for attrname in self.node_attributes:
            attr = getattr(self, attrname)
            result[attrname] = _maybe_as_dict(attr)
        return result


class UseNode(NodeBase):
    node_type = "use"
    node_attributes = ["id", "package", "ffidecl", "guard"]


class FFIDeclNode(NodeBase):
    node_type = "ffidecl"
    node_attributes = ["id", "typeargs", "params", "partial"]


class TypeArgs(NodeBase):
    node_type = "typeargs"
    node_attributes = ["typeargs"]


class Nominal(NodeBase):
    node_type = "nominal"
    node_attributes = ["package", "id", "typeargs", "cap", "cap_modifier"]


class ArrowNode(NodeBase):
    node_type = "->"
    node_attributes = ["origin", "target"]


class SeqNode(Node):
    node_type = "seq"

    def __init__(self, seq, **kwargs):
        self.seq = seq
        super(SeqNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(SeqNode, self).as_dict(),
                seq=[s.as_dict() for s in self.seq],
                )


class ClassNodeBase(DocNode, Annotated, Id):

    def __init__(self, members=None, capability=None,
                 type_params=None, is_=None, **kwargs):
        self.members = members if members else []
        self.capability = capability
        self.is_ = is_
        self.type_params = type_params
        super(ClassNodeBase, self).__init__(**kwargs)

    def as_dict(self):
        d = dict(
            super(ClassNodeBase, self).as_dict(),
            capability=self.capability,
            members=[m.as_dict() for m in self.members],
            type_params=self.type_params,
        )
        d["is"] = self.is_
        return d


class ClassNode(ClassNodeBase):
    node_type = "class"


class TypeNode(ClassNodeBase):
    node_type = "type"

    def __init__(self, **kwargs):
        if kwargs.get("members"):
            raise SyntaxError("type class definition doesn't accept members")
        if kwargs.get("annotation"):
            raise SyntaxError("type class definition doesn't accept annotations")
        super(TypeNode, self).__init__(**kwargs)


class FieldNode(Node, Id):

    def __init__(self, type, default=None):
        self.type = type
        self.default = default

    def as_dict(self):
        return dict(
                super(FieldNode, self).as_dict(),
                type=self.type,
                default=self.default
                )


class VarFieldNode(FieldNode):
    node_type = "fvar"


class LetFieldNode(FieldNode):
    node_type = "flet"


class EmbedFieldNode(FieldNode):
    node_type = "fembed"


class MethodNode(NodeBase):
    node_attributes = ["docstring", "annotations", "id", "capability",
            "typeparams", "params", "return_type", "is_partial", "guard",
            "body"]


class NewMethod(MethodNode):
    node_type = "new"


class FunMethod(MethodNode):
    node_type = "fun"


class BeMethod(MethodNode):
    node_type = "be"


class PatternModifierNode(Node):
    def __init__(self, pattern=None, **kwargs):
        self.pattern = pattern
        super(PatternModifierNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(PatternModifierNode, self).as_dict(),
            pattern=self.pattern,
        )


class NotNode(PatternModifierNode):
    node_type = "not"


class AddressofNode(PatternModifierNode):
    node_type = "addressof"


class DigestOfNode(PatternModifierNode):
    node_type = "digestof"


class NegNode(PatternModifierNode):
    node_type = "neg"


class NegUnsafeNode(PatternModifierNode):
    node_type = "neg_unsafe"


class LiteralNode(Node):
    def __init__(self, value, **kwargs):
        self.value = value
        super(LiteralNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(LiteralNode, self).as_dict(),
            value=self.value,
        )


class TrueNode(LiteralNode):
    node_type = "true"


class FalseNode(LiteralNode):
    node_type = "false"


class IntNode(LiteralNode):
    node_type = "int"


class FloatNode(LiteralNode):
    node_type = "float"


class StringNode(LiteralNode):
    node_type = "string"


class ReferenceNode(Node, Id):
    node_type = "reference"


class ParamNode(NodeBase):
    node_type = "param"
    node_attributes = ["id", "type", "default"]


class ParamsNode(Node):
    node_type = "params"

    def __init__(self, params, **kwargs):
        self.params = params
        super(ParamsNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(ParamsNode, self).as_dict(),
            params=[a.as_dict() for a in self.params],
        )


class ThisNode(Node):
    node_type = "this"


class IfNode(NodeBase):
    node_type = "if"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class DotNode(Node):
    node_type = '.'

    def __init__(self, first, second, **kwargs):
        self.first = first
        self.second = second
        super(DotNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(DotNode, self).as_dict(),
            first=self.first.as_dict(),
            second=self.second
        )


class CallNode(Node):
    node_type = "call"

    def __init__(self, fun, positionalargs, namedargs, is_partial, **kwargs):
        self.fun = fun
        self.positionalargs = positionalargs
        self.namedargs = namedargs
        self.is_partial = is_partial
        super(CallNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(CallNode, self).as_dict(),
            fun=self.fun.as_dict(),
            positionalargs=self.positionalargs.as_dict(),
            namedargs=self.namedargs.as_dict(),
            is_partial=self.is_partial,
        )


class PositionalArgsNode(Node):
    node_type = "positionalargs"

    def __init__(self, args, **kwargs):
        self.args = args
        super(PositionalArgsNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(PositionalArgsNode, self).as_dict(),
            args=[a.as_dict() for a in self.args],
        )


class NamedArgsNode(Node):
    node_type = "namedargs"

    def __init__(self, args, **kwargs):
        self.args = args
        super(NamedArgsNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(NamedArgsNode, self).as_dict(),
            args=[a.as_dict() for a in self.args],
        )


class NamedArgNode(Node, Id):
    node_type = "namedarg"

    def __init__(self, value, **kwargs):
        self.value = value
        super(NamedArgNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(NamedArgNode, self).as_dict(),
            value=self.value.as_dict(),
        )


class IfdefNode(NodeBase):
    node_type = "ifdef"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class ElseifdefNode(IfNode):
    node_type = "elseifdef"


class IftypeNode(ElseNode, Annotated):
    node_type = "iftype"

    def __init__(self, assertion, members, **kwargs):
        self.assertion = assertion
        self.members = members
        super(IftypeNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(IftypeNode, self).as_dict(),
            # members=[m.as_dict() for m in self.members],
            members=self.members,
            assertion=self.assertion.as_dict()
        )


class ElseifTypeNode(IftypeNode):
    node_type = "elseiftype"


class TypeAssertionNode(Node):
    node_type = "type_assertion"

    def __init__(self, child_type, parent_type, **kwargs):
        self.child_type = child_type
        self.parent_type = parent_type
        super(TypeAssertionNode).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(TypeAssertionNode, self).as_dict(),
                child_type=self.child_type,
                parent_type=self.parent_type,
        )


class MatchNode(ElseNode, Annotated):
    node_type = "match"

    def __init__(self, matchseq, cases, **kwargs):
        self.matchseq = matchseq
        self.cases = cases
        super(MatchNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(MatchNode, self).as_dict(),
            matchseq=self.matchseq,
            cases=[c.as_dict() for c in self.cases]
        )


class CaseNode(Node, Annotated):
    node_type = "case"

    def __init__(self, pattern, guard, action, **kwargs):
        self.pattern = pattern
        self.guard = guard
        self.action = action

    def as_dict(self):
        return dict(
            super(CaseNode, self).as_dict(),
            pattern=self.pattern,
            action=self.action,
            guard=self.guard
        )



class WhileNode(ElseNode, Annotated):
    node_type = "while"

    def __init__(self, assertion, members, **kwargs):
        self.assertion = assertion
        self.members = members
        super(WhileNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(WhileNode, self).as_dict(),
            members=self.members,
            assertion=self.assertion
        )


class RepeatNode(ElseNode, Annotated):
    node_type = "repeat"

    def __init__(self, assertion, members, **kwargs):
        self.assertion = assertion
        self.members = members
        super(RepeatNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(RepeatNode, self).as_dict(),
            members=self.members,
            assertion=self.assertion
        )


class ForNode(ElseNode, Annotated):
    node_type = "for"

    def __init__(self, ids, sequence, members, **kwargs):
        self.ids = ids
        self.sequence = sequence
        self.members = members
        super(ForNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(ForNode, self).as_dict(),
            ids=self.ids,
            sequence=self.sequence,
            members=self.members
        )


class WithNode(ElseNode, Annotated):
    node_type = "with"

    def __init__(self, elems, members, **kwargs):
        self.elems=elems
        self.members = members
        super(WithNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(WithNode, self).as_dict(),
            elems=self.elems,
            members=self.members
        )


class TryNode(ElseNode, Annotated):
    node_type = "try"

    def __init__(self, members, then, **kwargs):
        self.members = members
        self.then = then
        super(TryNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(TryNode, self).as_dict(),
            members=self.members,
            then=self.then
        )


class RecoverNode(Node, Annotated):
    node_type = "recover"

    def __init__(self, capability, members, **kwargs):
        self.capability = capability
        self.members = members
        super(RecoverNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(RecoverNode, self).as_dict(),
            capability=self.capability,
            members=self.members
        )


class ConsumeNode(Node):
    node_type = "consume"

    def __init__(self, capability, term, **kwargs):
        self.capability = capability
        self.term = term
        super(ConsumeNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(ConsumeNode, self).as_dict(),
            term=self.term,
            capability=self.capability
        )


class InfixFactory(object):
    def __init__(self, operator_class, **kwargs):
        self.cls = operator_class
        self.kwargs = kwargs

    def __call__(self, term):
        return self.cls(term=term, **self.kwargs)


class InfixNode(Node):
    def __init__(self, term, **kwargs):
        self.term = term

    def as_dict(self):
        return dict(
            super(InfixNode, self).as_dict(),
            term=self.term,
        )


class AsNode(InfixNode):
    node_type = "as"
    def __init__(self, type, **kwargs):
        self.type = type
        super(AsNode, self).__init_(**kwargs)

    def as_dict(self):
        return dict(
            super(AsNode, self).as_dict(),
            type=self.term,
        )

