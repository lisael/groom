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
    elif obj is None:
        return None
    elif isinstance(obj, (str, bool)):
        return obj
    else:
        # import ipdb; ipdb.set_trace()
        raise ValueError(obj)


class Node(metaclass=NodeMeta):
    """
    AST node base class
    """
    def __init__(self, **kwargs):
        for attrname in self.node_attributes:
            setattr(self, attrname, kwargs.pop(attrname, None))

    def as_dict(self):
        result = dict(node_type=self.node_type)
        for attrname in self.node_attributes:
            attr = getattr(self, attrname)
            result[attrname] = _maybe_as_dict(attr)
        return result


class ModuleNode(Node):
    node_type = "module"
    node_attributes = ["docstring", "name", "uses", "class_defs"]


class AssignNode(Node):
    node_type = "="
    node_attributes = ["first", "second"]


class JumpNode(Node):
    node_attributes = ["seq"]


class ReturnNode(JumpNode):
    node_type = "return"


class BreakNode(JumpNode):
    node_type = "break"


class ContinueNode(JumpNode):
    node_type = "continue"


class ErrorNode(JumpNode):
    node_type = "error"


class CompileIntrinsicNode(JumpNode):
    node_type = "compile_intrinsic"


class CompileErrorNode(JumpNode):
    node_type = "compile_error"


class UseNode(Node):
    node_type = "use"
    node_attributes = ["id", "package", "ffidecl", "guard"]


class FFIDeclNode(Node):
    node_type = "ffidecl"
    node_attributes = ["id", "typeargs", "params", "partial"]


class TypeParamsNode(Node):
    node_type = "typeparams"
    node_attributes = ["members"]


class TypeParamNode(Node):
    node_type = "typeparam"
    node_attributes = ["id", "type", "typearg"]


class TypeArgs(Node):
    node_type = "typeargs"
    node_attributes = ["typeargs"]


class Nominal(Node):
    node_type = "nominal"
    node_attributes = ["package", "id", "typeargs", "cap", "cap_modifier"]


class ArrowNode(Node):
    node_type = "->"
    node_attributes = ["origin", "target"]


class SeqNode(Node):
    node_type = "seq"
    node_attributes = ["seq"]


class ClassNodeBase(Node):
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


class InterfaceNode(ClassNodeBase):
    node_type = "interface"


class StructNode(ClassNodeBase):
    node_type = "struct"


class TraitNode(ClassNodeBase):
    node_type = "trait"


class TupleTypeNode(Node):
    node_type = "tupletype"
    node_attributes = ["members"]


class ProvidesNode(Node):
    node_type = "provides"
    node_attributes = ["type"]


class DeclNode(Node):
    node_attributes = ["id", "type"]


class VarNode(DeclNode):
    node_type = "var"


class LetNode(DeclNode):
    node_type = "let"


class FieldNode(Node):
    node_attributes = ["id", "type", "default"]


class VarFieldNode(FieldNode):
    node_type = "fvar"


class LetFieldNode(FieldNode):
    node_type = "flet"


class EmbedFieldNode(FieldNode):
    node_type = "fembed"


class MethodNode(Node):
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


class ReferenceNode(Node):
    node_type = "reference"
    node_attributes = ["id"]


class ParamNode(Node):
    node_type = "param"
    node_attributes = ["id", "type", "default"]


class ParamsNode(Node):
    node_type = "params"
    node_attributes = ["params"]


class ThisNode(Node):
    node_type = "this"


class IfNode(Node):
    node_type = "if"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class DotNode(Node):
    node_type = '.'
    node_attributes = ["first", "second"]


class CallNode(Node):
    node_type = "call"
    node_attributes = ["fun", "positionalargs", "namedargs", "is_partial"]


class QualifyNode(Node):
    node_type = "qualify"
    node_attributes = ["type", "args"]


class PositionalArgsNode(Node):
    node_type = "positionalargs"
    node_attributes = ["args"]


class NamedArgsNode(Node):
    node_type = "namedargs"
    node_attributes = ["args"]


class NamedArgNode(Node):
    node_type = "namedarg"
    node_attributes = ["id", "value"]


class IfdefNode(Node):
    node_type = "ifdef"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class IftypeNode(Node):
    node_type = "iftype"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]


class TypeAssertionNode(Node):
    node_type = "type_assertion"
    node_attributes = ["child_type", "parent_type"]


class MatchNode(Node):
    node_type = "match"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "seq", "cases"]


class CaseNode(Node):
    node_type = "case"
    node_attributes = ["annotations", "pattern", "guard", "action"]


class WhileNode(Node):
    node_type = "while"
    node_attributes = ["else_", "annotations", "assertion", "members",
                       "else_annotations"]


class RepeatNode(Node):
    node_type = "repeat"
    node_attributes = ["else_", "annotations", "assertion", "members",
                       "else_annotations"]


class ForNode(Node):
    node_type = "for"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "ids", "sequence", "members"]


class WithNode(Node):
    node_type = "with"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "elems", "members"]


class TryNode(Node):
    node_type = "try"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "then", "then_annotations", "members"]


class TupleNode(Node):
    node_type = "tuple"
    node_attributes = ["members"]


class ArrayNode(Node):
    node_type = "array"
    node_attributes = ["type", "members"]


class FFICallNode(Node):
    node_type = "fficall"
    node_attributes = ["id", "typeargs", "positional", "named", "partial"]


class RecoverNode(Node):
    node_type = "recover"
    node_attributes = ["annotations", "cap", "members"]


class ElipsisNode(Node):
    node_type = "..."


class ObjectNode(Node):
    node_type = "object"
    node_attributes = ["annotations", "cap", "provides", "members"]


class ConsumeNode(Node):
    node_type = "consume"
    node_attributes = ["cap", "term"]


class IdNode(Node):
    node_type = "id"
    node_attributes = ["id"]


class AsNode(Node):
    node_type = "as"
    node_attributes = ["term", "type"]


class BinOpNode(Node):
    node_attributes = ["operator", "first", "second", "is_partial"]

    @property
    def node_type(self):
        return self.operator
