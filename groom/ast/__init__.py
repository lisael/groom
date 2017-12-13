from groom.ast.nodes import (DocNode, ModuleNode, UseNode,
                             TypeNode, ClassNode, FieldNode,
                             VarFieldNode, LetFieldNode, EmbedFieldNode,
                             NewMethod, FunMethod, BeMethod)  # noqa


def build_class(**kwargs):
    # TODO: add interface, struct...
    decl = kwargs.pop('decl')
    if decl == "type":
        if kwargs.pop("members"):
            raise SyntaxError("type class definition doesn't accept members")
        if kwargs.pop("annotation"):
            raise SyntaxError("type class definition doesn't accept annotations")
        return TypeNode(**kwargs)
    elif decl == "class":
        return ClassNode(**kwargs)
    else:
        raise SyntaxError()
