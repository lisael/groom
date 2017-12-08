import ply.yacc as yacc
from groom.lexer import _lexer, tokens


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

    def __init__(self, name=None, uses=None, **kwargs):
        self.name = name
        self.uses = uses if uses else []
        super(ModuleNode, self).__init__(**kwargs)

    def as_dict(self):
        return dict(
                super(ModuleNode, self).as_dict(),
                name=self.name,
                uses=self.uses
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
                uses=self.uses
                )


def p_module(p):
    """
    module : STRING uses
    module : uses
    """
    if len(p) == 4:
        p[0] = ModuleNode(docstring=p[1], uses=p[2])
    else:
        p[0] = ModuleNode(uses=p[1])


def p_uses(p):
    """
    uses : use uses
    uses : use
    uses :
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_use(p):
    """
    use : USE STRING
    """
    p[0] = UseNode(p[1], p[1])


parser = yacc.yacc()

tree = parser.parse('''"""docstring..."""use "plop"''', lexer=_lexer)

print(tree.as_dict())
