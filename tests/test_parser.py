from pprint import pprint

from groom.lexer import Lexer
from groom.parser import Parser
from groom import ast
from unittest import skip


def parse_code(data, expected, verbose=False, **parser_opts):
    tree = Parser(**parser_opts).parse(data, lexer=Lexer(), debug=verbose)
    result = tree.as_dict() if isinstance(tree, ast.Node) else tree
    if verbose:
        pprint(result)
    assert(result == expected)


VERBOSE = True


def test_ffidecl():
    data = """
        @ffifunc[I32](fd: I32)?
    """
    expected = {
        'id': {'id': 'ffifunc', 'node_type': 'id'},
        'node_type': 'ffidecl',
        'params': {'node_type': 'params',
                   'params': [{'default': None,
                               'node_type': 'param',
                               'id': {'id': 'fd', 'node_type': 'id'},
                               'type': {'cap': None,
                                        'cap_modifier': None,
                                        'id': {'id': 'I32', 'node_type': 'id'},
                                        'node_type': 'nominal',
                                        'package': None,
                                        'typeargs': []}}]},
        'partial': True,
        'typeargs': {'node_type': 'typeargs',
                     'typeargs': [{'cap': None,
                                   'cap_modifier': None,
                                   'id': {'id': 'I32', 'node_type': 'id'},
                                   'node_type': 'nominal',
                                   'package': None,
                                   'typeargs': []}]}}
    parse_code(data, expected, verbose=VERBOSE, start="use_ffi")


def test_call():
    data = """
        env.out.print("hello world")
    """
    expected = {
        'fun': {
            'first': {
                'first': {
                    'id': {'id': 'env', 'node_type': 'id'},
                    'node_type': 'reference'
                },
                'node_type': '.',
                'second': {'id': 'out', 'node_type': 'id'}
            },
            'node_type': '.',
            'second': {'id': 'print', 'node_type': 'id'}
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
            'id': {'id': 'foo', 'node_type': 'id'},
            'node_type': 'reference'
        },
        'is_partial': False,
        'namedargs': {
            'args': [
                {
                    'id': {'id': 'pos', 'node_type': 'id'},
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
    data = """
        use myboots = "boots" if windows
    """
    expected = {
        'ffidecl': None,
        'id': {'id': 'myboots', 'node_type': 'id'},
        'guard': {'id': {'id': 'windows', 'node_type': 'id'},
		  'node_type': 'reference'},
        'node_type': 'use',
        'package': '"boots"'
    }
    parse_code(data, expected, verbose=VERBOSE, start='use')


def test_use_ffi():
    data = """
        use mypkg = @ffipkg[I64](fd: I32) if windows
    """
    expected = {
        'ffidecl': {'id': {'id': 'ffipkg', 'node_type': 'id'},
                    'node_type': 'ffidecl',
                    'params': {'node_type': 'params',
                               'params': [{'default': None,
                                           'node_type': 'param',
                                           'id': {'id': 'fd', 'node_type': 'id'},
                                           'type': {'cap': None,
                                                    'cap_modifier': None,
                                                    'id': {'id': 'I32', 'node_type': 'id'},
                                                    'node_type': 'nominal',
                                                    'package': None,
                                                    'typeargs': []}}]},
                    'partial': False,
                    'typeargs': {'node_type': 'typeargs',
                                 'typeargs': [{'cap': None,
                                               'cap_modifier': None,
                                               'id': {'id': 'I64', 'node_type': 'id'},
                                               'node_type': 'nominal',
                                               'package': None,
                                               'typeargs': []}]}},
        'guard': {'id': {'id': 'windows', 'node_type': 'id'},
                  'node_type': 'reference'},
        'id': {'id': 'mypkg', 'node_type': 'id'},
        'node_type': 'use',
        'package': None
    }
    parse_code(data, expected, verbose=VERBOSE, start='use')


def test_method():
    data = """
        new create(env: Env): String iso^ ? if true => "stuff"
    """
    expected = {
        'annotations': [],
        'body': {'node_type': 'seq',
                 'seq': [{'node_type': 'string', 'value': '"stuff"'}]},
        'capability': None,
        'docstring': None,
        'guard': {'node_type': 'seq',
                  'seq': [{'node_type': 'true', 'value': 'true'}]},
        'id': {'id': 'create', 'node_type': 'id'},
        'is_partial': True,
        'node_type': 'new',
        'params': {'node_type': 'params',
                   'params': [{'default': None,
                               'id': {'id': 'env', 'node_type': 'id'},
                               'node_type': 'param',
                               'type': {'cap': None,
                                        'cap_modifier': None,
                                        'id': {'id': 'Env', 'node_type': 'id'},
                                        'node_type': 'nominal',
                                        'package': None,
                                        'typeargs': []}}]},
        'return_type': {'cap': 'iso',
                        'cap_modifier': '^',
                        'id': {'id': 'String', 'node_type': 'id'},
                        'node_type': 'nominal',
                        'package': None,
                        'typeargs': []},
        'typeparams': []
    }
    parse_code(data, expected, verbose=VERBOSE, start='method')


def test_if():
    data = """
        if \likely\ true then false end
    """
    expected = {
        'annotations': [{'id': 'likely', 'node_type': 'id'}],
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': None,
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'false', 'value': 'false'}]},
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=VERBOSE, start='if')


def test_if_else():
    data = """
        if true then false else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': {'node_type': 'seq',
                  'seq': [{'node_type': 'string', 'value': '"hello"'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'false', 'value': 'false'}]},
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
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': {'annotations': [],
                  'assertion': {'node_type': 'seq',
                                'seq': [{'node_type': 'false', 'value': 'false'}]},
                  'else_': None,
                  'else_annotations': None,
                  'members': {'node_type': 'seq',
                              'seq': [{'node_type': 'string', 'value': '"hello"'}]},
                  'node_type': 'if'},
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'string', 'value': '"bye"'}]},
        'node_type': 'if'
    }
    parse_code(data, expected, verbose=VERBOSE, start='if')


def test_ifdef():
    data = """
        ifdef os_haiku then false else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': {'id': {'id': 'os_haiku', 'node_type': 'id'},
                      'node_type': 'reference'},
        'else_': {'node_type': 'seq',
                  'seq': [{'node_type': 'string', 'value': '"hello"'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'false', 'value': 'false'}]},
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
        'assertion': {'id': {'id': 'os_haiku', 'node_type': 'id'},
                      'node_type': 'reference'},
        'else_': {'annotations': [],
                  'assertion': {'id': {'id': 'os_hurd', 'node_type': 'id'},
                                'node_type': 'reference'},
                  'else_': {'node_type': 'seq',
                            'seq': [
                                {'node_type': 'string', 'value': '"dunno"'}
                            ]},
                  'else_annotations': [],
                  'members': {'node_type': 'seq',
                              'seq': [{'node_type': 'string',
                                       'value': '"dont do drugs"'}]},
                  'node_type': 'ifdef'},
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'string', 'value': '"lol"'}]},
        'node_type': 'ifdef'
    }
    parse_code(data, expected, verbose=VERBOSE, start='ifdef')


def test_while():
    data = """
        while true do stuff end
    """
    expected = {
        'annotations': [],
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': None,
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
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
        'assertion': {'child_type': {'cap': None,
                                     'cap_modifier': None,
                                     'id': {'id': 'A', 'node_type': 'id'},
                                     'node_type': 'nominal',
                                     'package': None,
                                     'typeargs': []},
                      'node_type': 'type_assertion',
                      'parent_type': {'cap': None,
                                      'cap_modifier': None,
                                      'id': {'id': 'U128', 'node_type': 'id'},
                                      'node_type': 'nominal',
                                      'package': None,
                                      'typeargs': []}},
        'else_': {'node_type': 'seq',
                  'seq': [{'node_type': 'false', 'value': 'false'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'true', 'value': 'true'}]},
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
        'assertion': {'child_type': {'cap': None,
                                     'cap_modifier': None,
                                     'id': {'id': 'A', 'node_type': 'id'},
                                     'node_type': 'nominal',
                                     'package': None,
                                     'typeargs': []},
                      'node_type': 'type_assertion',
                      'parent_type': {'cap': None,
                                      'cap_modifier': None,
                                      'id': {'id': 'U128', 'node_type': 'id'},
                                      'node_type': 'nominal',
                                      'package': None,
                                      'typeargs': []}},
        'else_': {'annotations': [],
                  'assertion': {'child_type': {'cap': None,
                                               'cap_modifier': None,
                                               'id': {'id': 'A', 'node_type': 'id'},
                                               'node_type': 'nominal',
                                               'package': None,
                                               'typeargs': []},
                                'node_type': 'type_assertion',
                                'parent_type': {'cap': None,
                                                'cap_modifier': None,
                                                'id': {'id': 'U64', 'node_type': 'id'},
                                                'node_type': 'nominal',
                                                'package': None,
                                                'typeargs': []}},
                  'else_': None,
                  'else_annotations': None,
                  'members': {'node_type': 'seq',
                              'seq': [{'node_type': 'false', 'value': 'false'}]},
                  'node_type': 'iftype'},
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'node_type': 'true', 'value': 'true'}]},
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
        'cases': [{'action': {'node_type': 'seq',
                              'seq': [{'id': {'id': 'do_foo', 'node_type': 'id'},
                                       'node_type': 'reference'}]},
                   'annotations': [],
                   'guard': None,
                   'node_type': 'case',
                   'pattern': {'id': {'id': 'foo', 'node_type': 'id'},
                               'node_type': 'reference'}},
                  {'action': {'node_type': 'seq',
                              'seq': [{'id': {'id': 'do_bar', 'node_type': 'id'},
                                       'node_type': 'reference'}]},
                   'annotations': [],
                   'guard': None,
                   'node_type': 'case',
                   'pattern': {'id': {'id': 'bar', 'node_type': 'id'},
                               'node_type': 'reference'}}],
        'else_': None,
        'else_annotations': None,
        'node_type': 'match',
        'seq': {'node_type': 'seq', 'seq': [{'id': {'id': 'stuf', 'node_type': 'id'},
                                             'node_type': 'reference'}]}
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
        'else_': None,
        'else_annotations': None,
        'node_type': 'match',
        'seq': {
            'node_type': 'seq',
            'seq': [{'id': {'id': 'stuf', 'node_type': 'id'},
                     'node_type': 'reference'}]
        }
    }
    parse_code(data, expected, verbose=VERBOSE, start='match')


def test_while_else():
    data = """
        while true do stuff else bar end
    """
    expected = {
        'annotations': [],
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': {'node_type': 'seq',
                  'seq': [{'id': {'id': 'bar', 'node_type': 'id'},
                           'node_type': 'reference'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
        'node_type': 'while'
    }
    parse_code(data, expected, verbose=VERBOSE, start='while')


def test_repeat():
    data = """
        repeat stuff until true end
    """
    expected = {
        'annotations': [],
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': None,
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
        'node_type': 'repeat'
    }
    parse_code(data, expected, verbose=VERBOSE, start='repeat')


def test_repeat_else():
    data = """
        repeat stuff until true else "hello" end
    """
    expected = {
        'annotations': [],
        'assertion': {'node_type': 'seq',
                      'seq': [{'node_type': 'true', 'value': 'true'}]},
        'else_': {'node_type': 'seq',
                  'seq': [{'node_type': 'string', 'value': '"hello"'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
        'node_type': 'repeat'
    }
    parse_code(data, expected, verbose=VERBOSE, start='repeat')


def test_idseq():
    data = """
        a
    """
    expected = {
        'members': [
            {'id': {'id': 'a', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
        ],
        'node_type': 'tuple'
    }
    parse_code(data, expected, verbose=VERBOSE, start='idseq')

    data = """
        (a, b)
    """
    expected = {
        'members': [
            {'id': {'id': 'a', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
            {'id': {'id': 'b', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
        ],
        'node_type': 'tuple'
    }
    parse_code(data, expected, verbose=VERBOSE, start='idseq')

    data = """
        (a, (b, c), d)
    """
    expected = ['a', ['b', 'c'], 'd']
    expected = {
        'members': [
            {'id': {'id': 'a', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
            {
                'members': [
                    {'id': {'id': 'b', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
                    {'id': {'id': 'c', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
                ],
                'node_type': 'tuple'
            },
            {'id': {'id': 'd', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
        ],
        'node_type': 'tuple'
    }
    parse_code(data, expected, verbose=VERBOSE, start='idseq')

    data = """
        (a, ((b, c), d, (e, f)), g)
    """
    expected = {
        'members': [
            {'id': {'id': 'a', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
            {
                'members': [
                    {
                        'members': [
                            {'id': {'id': 'b', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
                            {'id': {'id': 'c', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
                        ],
                        'node_type': 'tuple'
                    },
                    {'id': {'id': 'd', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
                    {
                        'members': [
                            {'id': {'id': 'e', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
                            {'id': {'id': 'f', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
                        ],
                        'node_type': 'tuple'
                    }
                ],
                'node_type': 'tuple'
            },
            {'id': {'id': 'g', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
        ],
        'node_type': 'tuple'
    }
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
        'else_': {'node_type': 'seq',
                  'seq': [{'id': {'id': 'foo', 'node_type': 'id'},
                           'node_type': 'reference'}]},
        'else_annotations': [],
        'ids': {
            'members': [
                {'id': {'id': 'i', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
                {'members': [
                    {'id': {'id': 'n', 'node_type': 'id'}, 'node_type': 'let', 'value': None},
                    {'id': {'id': '_', 'node_type': 'id'}, 'node_type': 'let', 'value': None}
                ], 'node_type': 'tuple'}],
            'node_type': 'tuple'},
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
        'node_type': 'for',
        'sequence': {'node_type': 'seq',
                     'seq': [{'id': {'id': 'pairs', 'node_type': 'id'},
                              'node_type': 'reference'}]}
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
        'elems': {'node_type': 'seq',
                  'seq': [{'node_type': 'seq',
                           'seq': [{'id': {'id': 'file', 'node_type': 'id'},
                                    'node_type': 'let',
                                    'value': None},
                                   {'node_type': 'seq',
                                    'seq': [{'id': {'id': 'myfile', 'node_type': 'id'},
                                             'node_type': 'reference'}]}]}]},
        'else_': {'node_type': 'seq',
                  'seq': [{'id': {'id': 'other', 'node_type': 'id'},
                           'node_type': 'reference'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
        'node_type': 'with'
    }
    parse_code(data, expected, verbose=VERBOSE, start='with')


def test_binary_op():
    data = """
        1 + 2
    """
    expected = {
        'first': {'node_type': 'int', 'value': '1'},
        'is_partial': False,
        'node_type': '+',
        'operator': '+',
        'second': {'node_type': 'int', 'value': '2'}
    }
    parse_code(data, expected, verbose=VERBOSE, start='infix')


def test_binary_partial_op():
    data = """
        1 +? 2
    """
    expected = {
        'first': {'node_type': 'int', 'value': '1'},
        'is_partial': True,
        'node_type': '+',
        'operator': '+',
        'second': {'node_type': 'int', 'value': '2'}
    }
    parse_code(data, expected, verbose=VERBOSE, start='infix')


def test_try():
    data = """
        try 1 +? 2 end
    """
    expected = {
        'annotations': [],
        'else_': None,
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'first': {'node_type': 'int', 'value': '1'},
                             'is_partial': True,
                             'node_type': '+',
                             'operator': '+',
                             'second': {'node_type': 'int', 'value': '2'}}]},
        'node_type': 'try',
        'then': None,
        'then_annotations': None
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_try_else():
    data = """
        try 1 +? 2 else hop end
    """
    expected = {
        'annotations': [],
        'else_': {'node_type': 'seq',
                  'seq': [{'id': {'id': 'hop', 'node_type': 'id'},
                           'node_type': 'reference'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'first': {'node_type': 'int', 'value': '1'},
                             'is_partial': True,
                             'node_type': '+',
                             'operator': '+',
                             'second': {'node_type': 'int', 'value': '2'}}]},
        'node_type': 'try',
        'then': None,
        'then_annotations': None
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_try_then():
    data = """
        try 1 +? 2 then 42 end
    """
    expected = {
        'annotations': [],
        'else_': None,
        'else_annotations': None,
        'members': {'node_type': 'seq',
                    'seq': [{'first': {'node_type': 'int', 'value': '1'},
                             'is_partial': True,
                             'node_type': '+',
                             'operator': '+',
                             'second': {'node_type': 'int', 'value': '2'}}]},
        'node_type': 'try',
        'then': {'node_type': 'seq', 'seq': [{'node_type': 'int', 'value': '42'}]},
        'then_annotations': []
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_try_then_else():
    data = """
        try 1 +? 2 else hop then 42 end
    """
    expected = {
        'annotations': [],
        'else_': {'node_type': 'seq',
                  'seq': [{'id': {'id': 'hop', 'node_type': 'id'},
                           'node_type': 'reference'}]},
        'else_annotations': [],
        'members': {'node_type': 'seq',
                    'seq': [{'first': {'node_type': 'int', 'value': '1'},
                             'is_partial': True,
                             'node_type': '+',
                             'operator': '+',
                             'second': {'node_type': 'int', 'value': '2'}}]},
        'node_type': 'try',
        'then': {'node_type': 'seq', 'seq': [{'node_type': 'int', 'value': '42'}]},
        'then_annotations': []
    }
    parse_code(data, expected, verbose=VERBOSE, start='try')


def test_recover():
    data = """
        recover iso stuff end
    """
    expected = {
        'annotations': [],
        'cap': 'iso',
        'members': {'node_type': 'seq',
                    'seq': [{'id': {'id': 'stuff', 'node_type': 'id'},
                             'node_type': 'reference'}]},
        'node_type': 'recover'
    }
    parse_code(data, expected, verbose=VERBOSE, start='recover')


def test_consume():
    data = """
        consume stuff
    """
    expected = {
        'cap': None,
        'node_type': 'consume',
        'term': {'id': {'id': 'stuff', 'node_type': 'id'}, 'node_type': 'reference'}
    }
    parse_code(data, expected, verbose=VERBOSE, start='consume')


def test_tupletype():
    data = """
        type Point is (I32, I32)
    """
    expected = {
        'annotations': [],
        'cap': None,
        'docstring': None,
        'id': {'id': 'Point', 'node_type': 'id'},
        'members': [],
        'node_type': 'type',
        'provides': {'node_type': 'provides',
                     'type': {'members': [{'cap': None,
                                           'cap_modifier': None,
                                           'id': {'id': 'I32', 'node_type': 'id'},
                                           'node_type': 'nominal',
                                           'package': None,
                                           'typeargs': []},
                                          {'cap': None,
                                           'cap_modifier': None,
                                           'id': {'id': 'I32', 'node_type': 'id'},
                                           'node_type': 'nominal',
                                           'package': None,
                                           'typeargs': []}],
                              'node_type': 'tupletype'}},
        'type_params': []
    }
    parse_code(data, expected, verbose=VERBOSE, start='class_def')


def test_unary_minus():
    data = """
        -2
    """
    expected = {
        'node_type': 'neg', 'pattern': {'node_type': 'int', 'value': '2'}}

    parse_code(data, expected, verbose=VERBOSE, start='pattern')


def test_module_parsing_no_docstring_no_use():
    data = '''
        type hop
    '''
    expected = {
        'class_defs': [{'annotations': [],
                        'cap': None,
                        'docstring': None,
                        'id': {'id': 'hop', 'node_type': 'id'},
                        'members': [],
                        'node_type': 'type',
                        'provides': None,
                        'type_params': []}],
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
