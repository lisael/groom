from groom.ast.nodes import (DocNode, ModuleNode, UseNode, TypeNode)  # noqa


def build_class(decl=None, id=None, members=None, docstring=None):
    if decl == "type":
        if members:
            raise SyntaxError()
        return TypeNode(id=id, docstring=docstring)
    else:
        raise SyntaxError()
