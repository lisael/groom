from pprint import pprint

from groom.lexer import Lexer
from groom.parser import Parser
from groom import ast


def parse_code(data, expected, verbose=False, **parser_opts):
    tree = Parser(**parser_opts).parse(data, lexer=Lexer(), debug=verbose)
    result = tree.as_dict() if isinstance(tree, ast.Node) else tree
    if verbose:
        pprint(result)
    assert(result == expected)


VERBOSE = True


def test_call():
    data = """
        env.out.print("hello world")
    """
    expected = {
        'fun': {
            'first': {
                'first': {
                    'id': 'env', 'node_type': 'reference'
                },
                'node_type': '.',
                'second': 'out'
            },
            'node_type': '.',
            'second': 'print'
        },
        'is_partial': False,
        'namedargs': {
            'args': [

            ], 'node_type': 'namedargs'
        },
        'node_type': 'call',
        'positionalargs': {
            'args': [
                {
                    'node_type': 'seq',
                    'seq': [
                        {
                            'node_type': 'string',
                            'value': '"hello world"'
                        }
                    ]
                }
            ],
            'node_type': 'positionalargs'
        }
    }
    parse_code(data, expected, verbose=VERBOSE, start='term')


def test_call_full():
    data = """
        foo("hello world", 42 where pos=3)
    """
    expected = {
        'fun': {
            'id': 'foo', 'node_type': 'reference'
        },
        'is_partial': False,
        'namedargs': {
            'args': [
                {
                    'id': 'pos',
                    'node_type': 'namedarg',
                    'value': {
                        'node_type': 'seq',
                        'seq': [
                                 {
                                     'node_type': 'int',
                                     'value': '3'
                                 }
                        ]
                    }
                }
            ],
            'node_type': 'namedargs'
        },
        'node_type': 'call',
        'positionalargs': {
            'args': [
                {
                    'node_type': 'seq',
                    'seq': [
                        {
                            'node_type': 'string',
                            'value': '"hello world"'
                        }
                    ]
                },
                {
                    'node_type': 'seq',
                    'seq': [
                        {
                            'node_type': 'int', 'value': '42'
                        }
                    ]
                }
            ],
            'node_type': 'positionalargs'
        }
    }

    parse_code(data, expected, verbose=VERBOSE, start='term')


def test_use():
    # these boots are made for walking.
    data = """
        use myboots = "boots" if windows
    """
    expected = {
        'alias': 'myboots',
        'guard': {'id': 'windows', 'node_type': 'reference'},
        'node_type': 'use',
        'package': '"boots"'
    }
    parse_code(data, expected, verbose=VERBOSE, start='use')


def test_use_ffi():
    data = """
        use mypkg = @ffipkg[I32](fd: I32) if windows
    """
    expected = {
        'alias': 'mypkg',
        'guard': {'id': 'windows', 'node_type': 'reference'},
        'node_type': 'use',
        'package': ('ffipkg',
                    [(('I32', [], None), None)],
                    [('fd', (('I32', [], None), None), None)],
                    False)
    }
    parse_code(data, expected, verbose=VERBOSE, start='use')


def test_method():
    data = """
        new create(env: Env): String iso^ ? if true => "stuff"
    """
    expected = {
        'annotations': [],
        'body': {
            'node_type': 'seq',
            'seq': [{'node_type': 'string', 'value': '"stuff"'}]},
        'capability': None,
        'docstring': None,
        'guard': {
            'node_type': 'seq', 'seq': [{'node_type': 'true', 'value': 'true'}]},
        'id': 'create',
        'is_partial': True,
        'node_type': 'new',
        'params': [('env', (('Env', [], None), None), None)],
        'return_type': (('String', [], ('iso', '^')), None),
        'typeparams': []
    }
    parse_code(data, expected, verbose=VERBOSE, start='method')


def test_if():
    data = """
        if \likely\ true then false end
    """
    expected = {
        'annotations': ['likely'],
        'assertion': {
            'node_type': 'seq',
            'seq': [
                {'node_type': 'true', 'value': 'true'}
            ]
        },
        'else': None,
        'members': {
            'node_type': 'seq',
            'seq': [
                {'node_type': 'false', 'value': 'false'}
            ]
        },
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=VERBOSE, start='if')


def test_if_else():
    data = """
        if true then false else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': [((('true', []), None), None)],
        'else': ([], [((('"hello"', []), None), None)]),
        'members': [((('false', []), None), None)],
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=VERBOSE, start='if')


def test_if_elseif():
    data = """
        if true then
            "bye"
        elseif false then
            "hello"
        end
    """
    expected = {
        'annotations': [],
        'assertion': [((('true', []), None), None)],
        'else': {
            'annotations': [],
            'assertion': [((('false', []), None), None)],
            'else': None,
            'members': [((('"hello"', []), None), None)],
            'node_type': 'elseif'
        },
        'members': [((('"bye"', []), None), None)],
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=VERBOSE, start='if')


def test_ifdef():
    data = """
        ifdef os_haiku then false else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': (('os_haiku', []), None),
        'else': ([], [((('"hello"', []), None), None)]),
        'members': [((('false', []), None), None)],
        'node_type': 'ifdef'
    }
    parse_code(data, expected, verbose=VERBOSE, start='ifdef')


def test_ifdef_elseifdef():
    data = """
        ifdef os_haiku then
            "lol"
        elseif os_hurd then
            "dont do drugs"
        else
            "dunno"
        end
    """
    expected = {
        'annotations': [],
        'assertion': (('os_haiku', []), None),
        'else': {
            'annotations': [],
            'assertion': (('os_hurd', []), None),
            'else': ([], [((('"dunno"', []), None), None)]),
            'members': [((('"dont do drugs"', []), None), None)],
            'node_type': 'elseifdef'
        },
        'members': [((('"lol"', []), None), None)],
        'node_type': 'ifdef'
    }
    parse_code(data, expected, verbose=VERBOSE, start='ifdef')


def test_while():
    data = """
        while true do stuff end
    """
    expected = {
        'annotations': [],
        'assertion': [((('true', []), None), None)],
        # 'else': (None, [((('"hello"', []), None), None)]),
        'else': None,
        'members': [((('stuff', []), None), None)],
        'node_type': 'while'
    }
    parse_code(data, expected, verbose=VERBOSE, start='while')


def test_iftype():
    data = """
        iftype A <: U128 then
            true
        else
            false
        end
    """
    expected = {
        'annotations': [],
        'assertion': {
            'child_type': (('A', [], None), None),
            'node_type': 'type_assertion',
            'parent_type': (('U128', [], None), None)
        },
        'else': ([], [((('false', []), None), None)]),
        'members': [((('true', []), None), None)],
        'node_type': 'iftype'
    }
    parse_code(data, expected, verbose=VERBOSE, start='iftype')


def test_iftype_elseiftype():
    data = """
        iftype A <: U128 then
            true
        elseif A <: U64 then
            false
        end
    """
    expected = {
        'annotations': [],
        'assertion': {
            'child_type': (('A', [], None), None),
            'node_type': 'type_assertion',
            'parent_type': (('U128', [], None), None)
        },
        'else': {
            'annotations': [],
            'assertion': {
                'child_type': (('A', [], None), None),
                'node_type': 'type_assertion',
                'parent_type': (('U64', [], None), None)
            },
            'else': None,
            'members': [((('false', []), None), None)],
            'node_type': 'elseiftype'
        },
        'members': [((('true', []), None), None)],
        'node_type': 'iftype'
    }
    parse_code(data, expected, verbose=VERBOSE, start='iftype')


def test_match():
    data = """
        match stuf
        | foo => do_foo
        | bar => do_bar
        end
    """
    expected = {
        'annotations': [],
        'cases': [
            {
                'action': [((('do_foo', []), None), None)],
                'guard': None,
                'node_type': 'case',
                'pattern': ('foo', [])
            },
            {
                'action': [((('do_bar', []), None), None)],
                'guard': None,
                'node_type': 'case',
                'pattern': ('bar', [])
            }
        ],
        'else': None,
        'matchseq': [((('stuf', []), None), None)],
        'node_type': 'match'
    }
    parse_code(data, expected, verbose=VERBOSE, start='match')


def test_empty_match():
    data = """
        match stuf
        end
    """
    expected = {
        'annotations': [],
        'cases': [],
        'else': None,
        'matchseq': [((('stuf', []), None), None)],
        'node_type': 'match'
    }
    parse_code(data, expected, verbose=VERBOSE, start='match')


def test_while_else():
    data = """
        while true do stuff else bar end
    """
    expected = {
        'annotations': [],
        'assertion': [((('true', []), None), None)],
        'else': ([], [((('bar', []), None), None)]),
        'members': [((('stuff', []), None), None)],
        'node_type': 'while'
    }
    parse_code(data, expected, verbose=VERBOSE, start='while')


def test_repeat():
    data = """
        repeat stuff until true end
    """
    expected = {
        'annotations': [],
        'assertion': [((('true', []), None), None)],
        # 'else': (None, [((('"hello"', []), None), None)]),
        'else': None,
        'members': [((('stuff', []), None), None)],
        'node_type': 'repeat'
    }
    parse_code(data, expected, verbose=VERBOSE, start='repeat')


def test_repeat_else():
    data = """
        repeat stuff until true else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': [((('true', []), None), None)],
        'else': ([], [((('"hello"', []), None), None)]),
        'members': [((('stuff', []), None), None)],
        'node_type': 'repeat'
    }
    parse_code(data, expected, verbose=VERBOSE, start='repeat')


def test_idseq():
    data = """
        a
    """
    expected = ['a']
    parse_code(data, expected, verbose=VERBOSE, start='idseq')

    data = """
        (a, b)
    """
    expected = ['a', 'b']
    parse_code(data, expected, verbose=VERBOSE, start='idseq')

    data = """
        (a, (b, c), d)
    """
    expected = ['a', ['b', 'c'], 'd']
    parse_code(data, expected, verbose=VERBOSE, start='idseq')

    data = """
        (a, ((b, c), d, (e, f)), g)
    """
    expected = ['a', [['b', 'c'], 'd', ['e', 'f']], 'g']
    parse_code(data, expected, verbose=VERBOSE, start='idseq')


def test_for():
    data = """
        for (i, (n, _)) in pairs do
            stuff
        else
            foo
        end
    """
    expected = {
        'annotations': [],
        'else': ([], [((('foo', []), None), None)]),
        'ids': ['i', ['n', '_']],
        'members': [((('stuff', []), None), None)],
        'node_type': 'for',
        'sequence': [((('pairs', []), None), None)]
    }
    parse_code(data, expected, verbose=VERBOSE, start='for')


def test_with():
    data = """
        with file = myfile do
            stuff
        else
            other
        end
    """
    expected = {
        'annotations': [],
        'elems': [(['file'], [((('myfile', []), None), None)])],
        'else': ([], [((('other', []), None), None)]),
        'members': [((('stuff', []), None), None)],
        'node_type': 'with'
    }
    parse_code(data, expected, verbose=VERBOSE, start='with')


def test_try():
    data = """
        try 1 +? 2 end
    """
    expected = {
        'annotations': [],
        'else': None,
        'then': None,
        'members': [((('1', []), [('+', ('2', []), True)]), None)],
        'node_type': 'try'
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_try_else():
    data = """
        try 1 +? 2 else hop end
    """
    expected = {
        'annotations': [],
        'else':  ([], [((('hop', []), None), None)]),
        'then': None,
        'members': [((('1', []), [('+', ('2', []), True)]), None)],
        'node_type': 'try'
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_try_then():
    data = """
        try 1 +? 2 then 42 end
    """
    expected = {
        'annotations': [],
        'else': None,
        'then': ([], [((('42', []), None), None)]),
        'members': [((('1', []), [('+', ('2', []), True)]), None)],
        'node_type': 'try'
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_try_then_else():
    data = """
        try 1 +? 2 else hop then 42 end
    """
    expected = {
        'annotations': [],
        'else':  ([], [((('hop', []), None), None)]),
        'then': ([], [((('42', []), None), None)]),
        'members': [((('1', []), [('+', ('2', []), True)]), None)],
        'node_type': 'try'
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_recover():
    data = """
        recover iso stuff end
    """
    expected = {
        'node_type': 'recover',
        'capability': 'iso',
        'annotations': [],
        'members': [((('stuff', []), None), None)],
    }
    parse_code(data, expected, verbose=VERBOSE, start='recover')


def test_consume():
    data = """
        consume stuff
    """
    expected = {
        'node_type': 'consume',
        'capability': None,
        'term': ('stuff', [])
    }
    parse_code(data, expected, verbose=VERBOSE, start='consume')


def test_tupletype():
    data = """
        type Point is (I32, I32)
    """
    expected = {
        'annotations': [],
        'capability': None,
        'docstring': None,
        'id': 'Point',
        'is': ([(('I32', [], None), None), (('I32', [], None), None)], None),
        'members': [],
        'node_type': 'type',
        'type_params': []
    }
    parse_code(data, expected, verbose=VERBOSE, start='class_def')


def test_unary_minus():
    data = """
        -2
    """
    expected = {
        "node_type": "neg",
        "pattern": ('2', [])
    }
    parse_code(data, expected, verbose=VERBOSE, start='pattern')


def test_full_module():
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

    new val create(env: Env): String iso^ ? if true =>
        let dd: Bool
        true == true
        // if true then false end
        42 +? 2; 44
        43
        return "stuff"

class Simple

type Combined is (Foo|Bar)

class MultipleParams[Pif, Paf]
    new create(env: Env, stuff: String): String ?
    fun foo()

'''
    expected = {
        'class_defs': [
            {
                'annotations': [],
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
                        'node_type': 'flet',
                        'id': 'aa',
                        'type': (('String', [], ('iso', None)), None),
                        'default': (('"hello"', []), None)
                    },
                    {
                        'node_type': 'flet',
                        'id': 'bb',
                        'type': (('Bool', [], None), None),
                        'default': None
                    },
                    {
                        'node_type': 'flet',
                        'id': 'cc',
                        'type': (('I32', [], None), None),
                        'default': (('40', []), [
                            ('+', ('2', []), False),
                            (('I32', [], None), None)
                        ]),
                    },
                    {
                        'annotations': [],
                        'capability': 'val',
                        'docstring': None,
                        'id': 'create',
                        'is_partial': True,
                        'typeparams': [],
                        'node_type': 'new',
                        # parameters and return_type are messy at the momment.
                        # they need their own nodes...
                        'params': [(('env', []),
                                        (('Env', [], None), None),
                                        None)],
                        'return_type': (('String', [], ('iso', '^')), None),
                        'guard': [((('true', []), None), None)],
                        'body': [
                            ((('let', 'dd', (('Bool', [], None), None)), None), None),
                            ((('true', []), [('==', ('true', []), False)]), None),
                            (('42', [('+', ('2', []), True)]), None),
                            ((('44', []), None), None),
                            (('43', None), None),
                            ('return', [((('"stuff"', []),  None), None)])
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
                        'typeparams': [],
                        'node_type': 'new',
                        # parameters and return_type are messy at the momment.
                        # they need their own nodes...
                        'params': [
                            (('env', []), (('Env', [], None), None), None),
                            (('stuff', []), (('String', [], None), None), None)
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
            {
                'alias': None,
                'condition': None,
                'node_type': 'use',
                'package': '"plop"'
            },
            {
                'alias': None,
                'condition': None,
                'node_type': 'use',
                'package': '"plip"'
            }
        ]
    }
    parse_code(data, expected, verbose=VERBOSE)


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
    parse_code(data, expected, verbose=VERBOSE)


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
