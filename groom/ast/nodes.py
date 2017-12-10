
__all__ = ["DocNode", "ModuleNode", "UseNode", "TypeNode"]


class Node(object):
    def as_dict(self):
        return dict(node_type=self.node_type)


class DocNode(Node):
    """a Node that holds a docstring"""
    def __init__(self, docstring=None, **kwargs):
        self.docstring = docstring

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


class TypeNode(DocNode):
    node_type = "type"

    def __init__(self, id, **kwargs):
        self.id = id
        super(TypeNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(TypeNode, self).as_dict(),
                id=self.id,
                )
