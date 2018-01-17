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


def pretty_pony(data):
    indent = 0
    lines = data.splitlines()
    result = []
    for line in lines:
        if len(line) and line[0] == '\x08':
            indent += 1
            line = line[1:]
        if len(line) and line[0] == '\x15':
            indent -= 1
            line = line[1:]
        result.append("%s%s" % ("  " * indent, line))
    return "\n".join(result)


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

    def pretty_pony(self):
        if hasattr(self, "_as_pony"):
            return pretty_pony(self._as_pony())
        return self.as_pony()

    def as_pony(self):
        return self._as_pony().replace("\x08", "").replace("\x15", "")


class ModuleNode(Node):
    node_type = "module"
    node_attributes = ["docstring", "name", "uses", "class_defs"]

    def _as_pony(self):
        docstring = self.docstring._as_pony() if self.docstring else ""
        uses = "\n".join([u._as_pony() for u in self.uses])
        class_defs = "\n\n".join([c._as_pony() for c in self.class_defs])
        return "%s%s\n\n%s" % (docstring, uses, class_defs)


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

    def _as_pony(self):
        quard = " " + self.guard._as_pony() if self.guard else ""
        if not self.ffidecl:
            if self.id:
                return "%s = %s%s" % (self.id._as_pony(), self.package, guard)
        return "TODO"


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

    def _as_pony(self):
        package = "%s." % self.package._as_pony() if self.package else ""
        args = self.typeargs._as_pony() if self.typeargs else ""
        cap = " %s%s" % (self.cap, self.cap_modifier) if self.cap else ""
        return "%s%s%s%s" % (package, self.id._as_pony(), args, cap)


class ArrowNode(Node):
    node_type = "->"
    node_attributes = ["origin", "target"]


class SeqNode(Node):
    node_type = "seq"
    node_attributes = ["seq"]

    def _as_pony(self):
        return "\n".join([s._as_pony() for s in self.seq])


class ClassNodeBase(Node):
    node_attributes = ["docstring", "annotations", "id",
                       "members", "cap", "provides", "type_params"]

    def _as_pony(self):
        decl = self.node_type
        annotations = pony_annotations(self.annotations)
        members = "\n".join([m._as_pony() for m in self.members])
        cap = " " + self.cap._as_pony() if self.cap else ""
        provides = " " + self.provides._as_pony() if self.provides else ""
        params = self.type_params._as_pony() if self.type_params else ""
        return "%s%s%s %s%s%s" % (decl, annotations, cap, self.id._as_pony(), params, provides)


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

    def _as_pony(self):
        return "(%s)" % ", ".join([m._as_pony() for m in self.members])


class ProvidesNode(Node):
    node_type = "provides"
    node_attributes = ["type"]

    def _as_pony(self):
        return "is " + self.type._as_pony()


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

    def _as_pony(self):
        decl = self.node_type
        annotations = pony_annotations(self.annotations)
        cap = " " + self.capability if self.capability else ""
        typeparams = self.typeparams._as_pony() if self.typeparams else ""
        params = self.params._as_pony()
        return_type = ": " + self.return_type._as_pony if self.return_type else ""
        is_partial = "?" if self.is_partial else ""
        guard = self.guard._as_pony() if self.guard else ""
        body = "=>\n\x08" + self.body._as_pony() + "\n\x15" if self.body else ""
        return "%s%s %s%s%s%s%s%s%s" % (decl, annotations, cap, typeparams, params, return_type, is_partial, guard, body)



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

    def _as_pony(self):
        return self.value


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

    def _as_pony(self):
        return self.id._as_pony()


class ParamNode(Node):
    node_type = "param"
    node_attributes = ["id", "type", "default"]

    def _as_pony(self):
        default = "=%s" % self.default._as_pony() if self.default else ""
        return "%s: %s%s" % (self.id._as_pony(), self.type._as_pony(), default)


class ParamsNode(Node):
    node_type = "params"
    node_attributes = ["params"]

    def _as_pony(self):
        return "(%s)" % ", ".join([p._as_pony() for p in self.params])


class ThisNode(Node):
    node_type = "this"


def pony_annotations(lst):
    if not lst:
        return ""
    return " \\%s\\" % ", ".join([i._as_pony() for i in lst])

class IfNode(Node):
    node_type = "if"
    node_attributes = ["annotations", "else_", "else_annotations",
                       "assertion", "members"]

    def _as_pony(self):
        if self.else_:
            else_ = "\n\x15else{}\n\x08{}".format(
                pony_annotations(self.else_annotations),
                self.else_._as_pony()
                )
        else:
            else_ = ""
        return "if{} {} then\n\x08{}{}\n\x15end".format(
            pony_annotations(self.annotations),
            self.assertion._as_pony(),
            self.members._as_pony(),
            else_
            )


class DotNode(Node):
    node_type = '.'
    node_attributes = ["first", "second"]

    def _as_pony(self):
        return "%s.%s" % (self.first._as_pony(), self.second._as_pony())


class CallNode(Node):
    node_type = "call"
    node_attributes = ["fun", "positionalargs", "namedargs", "is_partial"]

    def _as_pony(self):
        fun = self.fun._as_pony()
        pos = self.positionalargs._as_pony()
        named = self.namedargs._as_pony()
        is_partial = "?" if self.is_partial else ""
        return "{}({}){}".format(fun, " where ".join(list(filter(bool, [pos, named]))), is_partial)


class QualifyNode(Node):
    node_type = "qualify"
    node_attributes = ["type", "args"]


class PositionalArgsNode(Node):
    node_type = "positionalargs"
    node_attributes = ["args"]

    def _as_pony(self):
        return ", ".join([a._as_pony() for a in self.args])


class NamedArgsNode(Node):
    node_type = "namedargs"
    node_attributes = ["args"]

    def _as_pony(self):
        return ", ".join([a._as_pony() for a in self.args])


class NamedArgNode(Node):
    node_type = "namedarg"
    node_attributes = ["id", "value"]

    def _as_pony(self):
        return "%s=%s" % (self.id._as_pony(), self.value._as_pony())


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


class LambdaNode(Node):
    node_type = "lambda"
    node_attributes = ["annotations", "cap2", "id", "typeparams", "params",
                       "lambdacaptures", "type", "is_partial", "body", "cap"]


class BareLambdaNode(Node):
    node_type = "barelambda"
    node_attributes = ["annotations", "cap2", "id", "typeparams", "params",
                       "lambdacaptures", "type", "is_partial", "body", "cap"]


class LambdaCaptures(Node):
    node_type = "lambdacaptures"
    node_attributes = ["members"]


class LambdaCapture(Node):
    node_type = "lambdacapture"
    node_attributes = ["id", "type", "value"]


class FFICallNode(Node):
    node_type = "fficall"
    node_attributes = ["id", "typeargs", "positional", "named", "partial"]

    def _as_pony(self):
        return "TODOFFI"


class LambdaType(Node):
    node_type = "lambdatype"
    node_attributes = ["cap2", "id", "typeparams", "params", "return_type",
                       "is_partial", "cap", "cap_modifier"]


class BareLambdaType(Node):
    node_type = "barelambdatype"
    node_attributes = ["cap2", "id", "typeparams", "params", "return_type",
                       "is_partial", "cap", "cap_modifier"]


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

    def _as_pony(self):
        return self.id


class AsNode(Node):
    node_type = "as"
    node_attributes = ["term", "type"]


class BinOpNode(Node):
    node_attributes = ["operator", "first", "second", "is_partial"]

    @property
    def node_type(self):
        return self.operator
