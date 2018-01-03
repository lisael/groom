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


class ClassNodeBase(NodeBase):
    node_attributes = ["docstring", "annotations", "id",
                       "members", "cap", "provides", "type_params"]


class ClassNode(ClassNodeBase):
    node_type = "class"


class TypeNode(ClassNodeBase):
    node_type = "type"


class PrimitiveNode(ClassNodeBase):
    node_type = "primitive"


class ActorNode(ClassNodeBase):
    node_type = "actor"


class TupleTypeNode(NodeBase):
    node_type = "tupletype"
    node_attributes = ["members"]


class ProvidesNode(NodeBase):
    node_type = "provides"
    node_attributes = ["type"]


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


class PatternModifierNode(NodeBase):
    node_attributes = ["pattern"]


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


class ReferenceNode(NodeBase):
    node_type = "reference"
    node_attributes = ["id"]


class ParamNode(NodeBase):
    node_type = "param"
    node_attributes = ["id", "type", "default"]


class ParamsNode(NodeBase):
    node_type = "params"
    node_attributes = ["params"]


class ThisNode(NodeBase):
    node_type = "this"


class IfNode(NodeBase):
    node_type = "if"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class DotNode(NodeBase):
    node_type = '.'
    node_attributes = ["first", "second"]

    def __init__(self, first, second, **kwargs):
        self.first = first
        self.second = second
        # super(DotNode, self).__init__(**kwargs)


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


class PositionalArgsNode(NodeBase):
    node_type = "positionalargs"
    node_attributes = ["args"]


class NamedArgsNode(NodeBase):
    node_type = "namedargs"
    node_attributes = ["args"]


class NamedArgNode(NodeBase):
    node_type = "namedarg"
    node_attributes = ["id", "value"]


class IfdefNode(NodeBase):
    node_type = "ifdef"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class IftypeNode(NodeBase):
    node_type = "iftype"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class TypeAssertionNode(NodeBase):
    node_type = "type_assertion"
    node_attributes = ["child_type", "parent_type"]


class MatchNode(NodeBase):
    node_type = "match"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "seq", "cases"]


class CaseNode(NodeBase):
    node_type = "case"
    node_attributes = ["annotations", "pattern", "guard", "action"]


class WhileNode(NodeBase):
    node_type = "while"
    node_attributes = ["else_", "annotations", "assertion", "members",
                       "else_annotations"]


class RepeatNode(NodeBase):
    node_type = "repeat"
    node_attributes = ["else_", "annotations", "assertion", "members",
                       "else_annotations"]


class ForNode(NodeBase):
    node_type = "for"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "ids", "sequence", "members"]


class WithNode(NodeBase):
    node_type = "with"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "elems", "members"]


class TryNode(NodeBase):
    node_type = "try"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "then", "then_annotations", "members"]


class TupleNode(NodeBase):
    node_type = "tuple"
    node_attributes = ["members"]


class RecoverNode(NodeBase):
    node_type = "recover"
    node_attributes = ["annotations", "cap", "members"]


class ConsumeNode(NodeBase):
    node_type = "consume"
    node_attributes = ["cap", "term"]


class LetNode(NodeBase):
    node_type = "let"
    node_attributes = ["id", "value"]


class IdNode(NodeBase):
    node_type = "id"
    node_attributes = ["id"]


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


class AsNode(NodeBase):
    node_type = "as"
    node_attributes = ["term", "type"]


class BinOpNode(NodeBase):
    node_attributes = ["operator", "first", "second", "is_partial"]

    @property
    def node_type(self):
        return self.operator
