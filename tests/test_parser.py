from groom.lexer import Lexer
from groom.parser import Parser


def test_module_parsing():
    """
    Test as much syntax constructs a possible

    Not a real unit test, it's more of a dev tool and
    a documentation of supported grammar
    """
    tree = Parser().parse('''"""docstring..."""
use "plop"
use "plip"

type Hop

class \packed\ iso Hip[Hop]
    """class docstring"""

    let aa: String = "hello"

    new create(env: Env): String ?

class Simple

type Combined is (Foo|Bar)

class MultipleParams[Pif, Paf]

''', lexer=Lexer(), debug=True)
    expected = {
        'class_defs': [
            {'docstring': None, 'id': 'Hop', 'node_type': 'type'},
            {
                'node_type': 'class',
                "annotations": ["packed"],
                'capability': 'iso',
                'id': 'Hip',
                'docstring': '"""class docstring"""',
                "members": [
                    {
                        'node_type': 'letfield',
                        'id': 'aa',
                        'type': (('String', [], None), None),
                        'default': ('"hello"', None)},
                    {
                        'annotations': [],
                        'capability': None,
                        'docstring': None,
                        'id': 'create',
                        'is_partial': True,
                        'method_parameters': [],
                        'node_type': 'new',
                        # parameters and return_type are messy at the momment. they
                        # need their own nodes...
                        'parameters': [('env',
                                       (('Env', [], None), None),
                                       None)],
                        'return_type': (('String', [], None), None)
                    },
                ],
            },
            {
                'node_type': 'class',
                "annotations": [],
                'capability': None,
                'id': 'Simple',
                'docstring': None,
                "members": [],
            },
            {'docstring': None, 'id': 'Combined', 'node_type': 'type'},
            {
                'node_type': 'class',
                "annotations": [],
                'capability': None,
                'id': 'MultipleParams',
                'docstring': None,
                "members": [],
            },
        ],
        'docstring': '"""docstring..."""',
        'name': None,
        'node_type': 'module',
        'uses': [
            {'name': '"plop"', 'node_type': 'use', 'packages': '"plop"'},
            {'name': '"plip"', 'node_type': 'use', 'packages': '"plip"'}
        ]
    }
    from pprint import pprint
    pprint(tree.as_dict())
    assert(tree.as_dict() == expected)


def test_module_parsing_no_docstring_no_use():
    tree = Parser().parse('''
type hop
''', lexer=Lexer())
    expected = {
        'class_defs': [
            {'docstring': None, 'id': 'hop', 'node_type': 'type'}
        ],
        'docstring': None,
        'name': None,
        'node_type': 'module',
        'uses': []
    }
    assert(tree.as_dict() == expected)


def test_module_only_docstring():
    tree = Parser().parse('''"""Only
docstring
"""
''', lexer=Lexer())
    expected = {
        'class_defs': [],
        'docstring': '"""Only\ndocstring\n"""',
        'name': None,
        'node_type': 'module',
        'uses': []
    }
    assert(tree.as_dict() == expected)
