from groom.tools.completer import complete


def test_complete():
    src = '''"""Docstring"""
use "collections"

act'''
    assert complete(src, len(src)) == ["actor"]
