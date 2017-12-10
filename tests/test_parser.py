from groom.lexer import Lexer
from groom.parser import Parser


def test_module_parsing():
    tree = Parser().parse('''"""docstring..."""
use "plop"
use "plip"

type hop
''', lexer=Lexer(), debug=True)
    expected = {
        'class_defs': [
            {'docstring': None, 'id': 'hop', 'node_type': 'type'}
        ],
        'docstring': '"""docstring..."""',
        'name': None,
        'node_type': 'module',
        'uses': [
            {'name': '"plop"', 'node_type': 'use', 'packages': '"plop"'},
            {'name': '"plip"', 'node_type': 'use', 'packages': '"plip"'}
        ]
    }
    assert(tree.as_dict() == expected)


def test_module_parsing_no_docstring():
    tree = Parser().parse('''
use "plop"
use "plip"

type hop
''', lexer=Lexer(), debug=True)
    expected = {
        'class_defs': [
            {'docstring': None, 'id': 'hop', 'node_type': 'type'}
        ],
        'docstring': None,
        'name': None,
        'node_type': 'module',
        'uses': [
            {'name': '"plop"', 'node_type': 'use', 'packages': '"plop"'},
            {'name': '"plip"', 'node_type': 'use', 'packages': '"plip"'}
        ]
    }
    assert(tree.as_dict() == expected)
