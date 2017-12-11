from groom.ast.nodes import (DocNode, ModuleNode, UseNode,  # noqa
                             TypeNode, ClassNode)  # noqa


def build_class(**kwargs):
    if kwargs["decl"] == "type":
        if kwargs.get("members"):
            raise SyntaxError("type class definition doesn't accept members")
        if kwargs.get("annotation"):
            raise SyntaxError("type class definition doesn't accept annotations")
        return TypeNode(**kwargs)
    elif kwargs["decl"] == "class":
        return ClassNode(**kwargs)
    else:
        raise SyntaxError()
