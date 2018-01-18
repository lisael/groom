import os
from pprint import pprint
from unittest import skipIf

from groom.lexer import Lexer
from groom.parser import Parser
from groom.ast import nodes
from groom.utils import find_pony_stdlib_path


parsers_cache = {}


def parse_code(data, **parser_opts):
    "parse the code and check that the generated pony code is the same."
    cache_key = tuple(parser_opts.items())
    parser = parsers_cache.setdefault(
        cache_key,
        Parser(**parser_opts)
        )
    expected = parser.parse(data, lexer=Lexer())
    generated = expected.as_pony()
    print(expected.pretty_pony())
    result = parser.parse(generated, lexer=Lexer())
    assert(result.as_dict() == expected.as_dict())


def test_call():
    data = """
        env.out.print("hello world")
    """
    parse_code(data, start='term')


def test_call_full():
    data = """
        foo("hello world", 42 where pos=3)
    """
    parse_code(data, start='term')


def test_if():
    data = """
        if \likely\ true then false end
    """
    parse_code(data, start='if')


def test_if_else():
    data = """
        if true then false else "hello" end
    """
    parse_code(data, start='if')


def test_uniontype():
    data = '''
    type BackpressureAuth is (AmbientAuth | ApplyReleaseBackpressureAuth)
    '''
    parse_code(data, start="class_def")


@skipIf(os.environ.get("SHORT_TESTS", 0), "perform short tests")
def test_parse_stdlib():
    path = find_pony_stdlib_path()
    for root, _, files in os.walk(path):
        for ponysrc in [f for f in files if f.endswith(".pony")]:
            with open(os.path.join(root, ponysrc)) as src:
                print(os.path.join(root, ponysrc))
                data = src.read()
                parse_code(data)
