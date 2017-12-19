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

    def __init__(self, name, pkg):
        self.name = name
        self.package = pkg
        super(UseNode, self).__init__()

    def as_dict(self):
        return dict(
                super(UseNode, self).as_dict(),
                name=self.name,
                packages=self.package
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


class IfNode(Node, Annotated):
    node_type = "if"

    def __init__(self, assertion, members, else_, **kwargs):
        self.assertion = assertion
        self.members = members
        self.else_ = else_
        super(IfNode, self).__init__(**kwargs)

    def as_dict(self):
        d = dict(
            super(IfNode, self).as_dict(),
            # members=[m.as_dict() for m in self.members],
            members=self.members,
            assertion=self.assertion
        )
        if isinstance(self.else_, Node):
            d["else"] = self.else_.as_dict()
        else:
            d["else"] = self.else_
        return d


class ElseifNode(IfNode):
    node_type = "elseif"


class WhileNode(Node, Annotated):
    node_type = "while"

    def __init__(self, assertion, members, else_, **kwargs):
        self.assertion = assertion
        self.members = members
        self.else_ = else_
        super(WhileNode, self).__init__(**kwargs)

    def as_dict(self):
        d = dict(
            super(WhileNode, self).as_dict(),
            # members=[m.as_dict() for m in self.members],
            members=self.members,
            assertion=self.assertion
        )
        d["else"] = self.else_
        return d
