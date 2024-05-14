import hashlib
import os
import shutil
from contextlib import contextmanager
from pathlib import Path

import pytest

import setuptools_reproducible


backend = Path(__file__).parent.parent / "setuptools_reproducible.py"


example_readme = """\
this is the first line of the README.md file
this is the second line of the README.md file — and it has non-ascii in it
"""

example_pyproject = """\
[build-system]
requires = ["setuptools-reproducible"]
build-backend = "setuptools_reproducible"
backend-path = ["."]

[project]
name = "mypkg"
version = "0.1"
readme = "README.md"

[tool.setuptools]
packages = ["mypkg"]
"""


def sha256sum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def srctrees(tmp_path):
    for src in "src1", "src2":
        path = tmp_path / src
        path.mkdir()
        path.joinpath("README.md").write_text(example_readme, encoding="utf8")
        path.joinpath("pyproject.toml").write_text(example_pyproject, encoding="utf8")
        path.joinpath("mypkg").mkdir()
        path.joinpath("mypkg").joinpath("__init__.py").write_text("", encoding="utf8")
        mod1 = path / "mypkg" / "mod1.py"
        mod2 = path / "mypkg" / "mod2.py"
        mod1.write_text("")
        mod2.write_text("")
        shutil.copy(backend, path)
    # we now have identical source trees in src1, src2.
    # let's fudge one of their modes and times...
    mod1.chmod(0o644)
    mod2.chmod(0o666)
    st = mod2.stat()
    os.utime(mod2, (st.st_atime - 60, st.st_mtime - 70))
    yield tmp_path.joinpath("src1"), tmp_path.joinpath("src2")


@contextmanager
def working_directory(path):
    """Change working directory and restore the previous on exit"""
    prev_dir = os.getcwd()
    os.chdir(str(path))
    try:
        yield str(path)
    finally:
        os.chdir(prev_dir)


def test_sdist_reproducibility(srctrees):
    path1, path2 = srctrees
    with working_directory(path1) as d:
        path1 /= setuptools_reproducible.build_sdist(d)
    with working_directory(path2) as d:
        path2 /= setuptools_reproducible.build_sdist(d)
    assert path1 != path2
    assert path1.name == path2.name == "mypkg-0.1.tar.gz"
    assert sha256sum(path1) == sha256sum(path2)


def test_wheel_reproducibility(srctrees):
    path1, path2 = srctrees
    with working_directory(path1) as d:
        path1 /= setuptools_reproducible.build_wheel(d)
    with working_directory(path2) as d:
        path2 /= setuptools_reproducible.build_wheel(d)
    assert path1 != path2
    assert path1.name == path2.name == "mypkg-0.1-py3-none-any.whl"
    assert sha256sum(path1) == sha256sum(path2)
