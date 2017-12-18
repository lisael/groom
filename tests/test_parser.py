from pprint import pprint

from groom.lexer import Lexer
from groom.parser import Parser


def parse_code(data, expected, verbose=False, **parser_opts):
    tree = Parser(**parser_opts).parse(data, lexer=Lexer(), debug=verbose)
    if verbose:
        pprint(tree.as_dict())
    assert(tree.as_dict() == expected)


def test_method():
    data = """
        new create(env: Env): String iso^ ? if true => "stuff"
    """
    expected = {
            'annotations': [],
            'body': [(('"stuff"', None), None)],
            'capability': None,
            'docstring': None,
            'guard': [(('true', None), None)],
            'id': 'create',
            'is_partial': True,
            'method_parameters': [],
            'node_type': 'new',
            'parameters': [('env', (('Env', [], None), None), None)],
            'return_type': (('String', [], ('iso', '^')), None)
    }
    parse_code(data, expected, start='method')


def test_if():
    data = """
        if true then false end
    """
    expected = {
        'annotations': [],
        'assertion': [(('true', None), None)],
        'else': None,
        'members': [(('false', None), None)],
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=True, start='if')


def test_if_else():
    data = """
        if true then false else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': [(('true', None), None)],
        'else': (None, [(('"hello"', None), None)]),
        'members': [(('false', None), None)],
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=True, start='if')


def test_if_elseif():
    data = """
        if true then "bye" elseif false then "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': [(('true', None), None)],
        'else': (None, [(('"hello"', None), None)]),
        'members': [(('false', None), None)],
        'node_type': 'if'
    }
    # parse_code(data, expected, verbose=True, start='if')


def test_module_parsing():
    """
    Test as much syntax constructs a possible

    Not a real unit test, it's more of a dev tool and
    a documentation of supported grammar
    """
    data = '''"""docstring..."""
use "plop"
use "plip"

type Hop

class \packed, something\ iso Hip[Hop]
    """class docstring"""

    let aa: String iso = "hello"
    let bb: Bool
    let cc: I32 = 40 + 2 as I32

    new create(env: Env): String iso^ ? if true =>
        true == true
        // if true then false end
        42; 44
        return "stuff"

class Simple

type Combined is (Foo|Bar)

class MultipleParams[Pif, Paf]
    new create(env: Env, stuff: String): String ?

'''
    expected = {
        'class_defs': [
            {'annotations': [],
                 'capability': None,
                 'docstring': None,
                 'id': 'Hop',
                 'is': None,
                 'members': [],
                 'node_type': 'type',
                 'type_params': []},
            {
                'node_type': 'class',
                "annotations": ["packed", "something"],
                'capability': 'iso',
                'id': 'Hip',
                'docstring': '"""class docstring"""',
                'is': None,
                'type_params': [('Hop', None, None)],
                "members": [
                    {
                        'node_type': 'letfield',
                        'id': 'aa',
                        'type': (('String', [], ('iso', None)), None),
                        'default': ('"hello"', None)
                    },
                    {
                        'node_type': 'letfield',
                        'id': 'bb',
                        'type': (('Bool', [], None), None),
                        'default': None
                    },
                    {
                        'node_type': 'letfield',
                        'id': 'cc',
                        'type': (('I32', [], None), None),
                        'default': ('40', [
                            ('+', '2', False),
                            (('I32', [], None), None)
                        ]),
                    },
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
                        'return_type': (('String', [], ('iso', '^')), None),
                        'guard': [(('true', None), None)],
                        'body': [
                            (('true', [('==', 'true', False)]), None),
                            (('42', None), None),
                            (('44', None), None),
                            ('return', [(('"stuff"', None), None)])
                        ],
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
                "is": None,
                "type_params": [],
            },
            {
                'annotations': [],
                'capability': None,
                'docstring': None,
                'id': 'Combined',
                'is': ([(('Foo', [], None), None)], None),
                'members': [],
                'node_type': 'type',
                'type_params': []
            },

            {
                'node_type': 'class',
                "annotations": [],
                'capability': None,
                'id': 'MultipleParams',
                'docstring': None,
                "is": None,
                'type_params': [('Pif', None, None), ('Paf', None, None)],
                "members": [
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
                        'parameters': [
                            ('env', (('Env', [], None), None), None),
                            ('stuff', (('String', [], None), None), None)
                        ],
                        'return_type': (('String', [], None), None),
                        'guard': None,
                        'body': None,
                    },
                ],
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
    parse_code(data, expected, verbose=False)


def test_module_parsing_no_docstring_no_use():
    data = '''
        type hop
    '''
    expected = {
        'class_defs': [
            {
                'annotations': [],
                'capability': None,
                'docstring': None,
                'id': 'hop',
                'is': None,
                'members': [],
                'node_type': 'type',
                'type_params': []
            }
        ],
        'docstring': None,
        'name': None,
        'node_type': 'module',
        'uses': []
    }
    parse_code(data, expected, verbose=True)


def test_module_only_docstring():
    data = '''
"""
Only
a docstring
"""
    '''
    expected = {
        'class_defs': [],
        'docstring': '"""\nOnly\na docstring\n"""',
        'name': None,
        'node_type': 'module',
        'uses': []
    }
    parse_code(data, expected)
