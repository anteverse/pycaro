from pathlib import Path

from pycaro.api.files import gen_python_files


def test_gen_python_files():
    res = list(gen_python_files(
        paths=iter([Path("/path/to/root/file1.py")]),
        root=Path("/path/to/root/"),
        gitignore=None,
    ))

    assert res == []
