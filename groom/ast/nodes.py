class Annotated(object):
    pass


class Node(object):
    def __init__(self, **kwargs):
        if isinstance(self, Annotated):
            annotations = kwargs.pop("annotation")
            self.annotations = annotations if annotations else []
        if len(kwargs):
            raise(ValueError("Unkown params {}".format(list(kwargs.keys()))))

    def as_dict(self):
        d = dict(node_type=self.node_type)
        if hasattr(self, "annotations"):
            d["annotations"] = self.annotations
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


class UseNode(Node):
    node_type = "use"

    def __init__(self, alias, package, condition, **kwargs):
        self.alias = alias
        self.package = package
        self.condition = condition
        super(UseNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(UseNode, self).as_dict(),
                alias=self.alias,
                package=self.package,
                condition=self.condition,
                )


class ClassNodeBase(DocNode, Annotated):

    def __init__(self, id=None, members=None, capability=None,
                 type_params=None, is_=None, **kwargs):
        self.id = id
        self.members = members if members else []
        self.capability = capability
        self.is_ = is_
        self.type_params = type_params
        super(ClassNodeBase, self).__init__(**kwargs)

    def as_dict(self):
        d = dict(
            super(ClassNodeBase, self).as_dict(),
            id=self.id,
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

    def as_dict(self):
        return dict(
                super(TypeNode, self).as_dict(),
                id=self.id,
                )


class FieldNode(Node):

    def __init__(self, id, type, default=None):
        self.id = id
        self.type = type
        self.default = default

    def as_dict(self):
        return dict(
                super(FieldNode, self).as_dict(),
                id=self.id,
                type=self.type,
                default=self.default
                )


class VarFieldNode(FieldNode):
    node_type = "varfield"


class LetFieldNode(FieldNode):
    node_type = "letfield"


class EmbedFieldNode(FieldNode):
    node_type = "embedfield"


class MethodNode(DocNode, Annotated):

    def __init__(self, capability, id, method_parameters, parameters,
                 return_type, is_partial, guard, body, **kwargs):
        self.capability = capability
        self.id = id
        self.method_parameters = method_parameters
        self.parameters = parameters
        self.return_type = return_type
        self.is_partial = is_partial
        self.parameters = parameters
        self.guard = guard
        self.body = body
        super(MethodNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(MethodNode, self).as_dict(),
                capability=self.capability,
                id=self.id,
                method_parameters=self.method_parameters,
                parameters=self.parameters,
                return_type=self.return_type,
                is_partial=self.is_partial,
                guard=self.guard,
                body=self.body,
                )


class NewMethod(MethodNode):
    node_type = "new"


class FunMethod(MethodNode):
    node_type = "new"


class BeMethod(MethodNode):
    node_type = "new"


class IfNode(ElseNode, Annotated):
    node_type = "if"

    def __init__(self, assertion, members, **kwargs):
        self.assertion = assertion
        self.members = members
        super(IfNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(IfNode, self).as_dict(),
            members=self.members,
            assertion=self.assertion
        )


class ElseifNode(IfNode):
    node_type = "elseif"


class IfdefNode(ElseNode, Annotated):
    node_type = "ifdef"

    def __init__(self, assertion, members, **kwargs):
        self.assertion = assertion
        self.members = members
        super(IfdefNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
            super(IfdefNode, self).as_dict(),
            members=self.members,
            assertion=self.assertion
        )


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
