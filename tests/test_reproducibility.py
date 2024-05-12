import hashlib
import os
import shutil
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
"""


expected_sdist_hash = "2334f998fdc8ed7726f1b383ee8ba6b9b0e562773466ff511a6b77af6ce2a16b"
expected_wheel_hash = "3d0505345d640e69471db33208d4bb0e343c8efc489f59907d1f9a5c57413b8e"


def sha256sum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def in_srctree(tmp_path):
    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(prev)


@pytest.fixture
def srctree_modern(in_srctree):
    in_srctree.joinpath("README.md").write_text(example_readme)
    in_srctree.joinpath("pyproject.toml").write_text(example_pyproject)
    in_srctree.joinpath("mypkg").mkdir()
    in_srctree.joinpath("mypkg").joinpath("__init__.py").write_text("")
    mod1 = in_srctree / "mypkg" / "mod1.py"
    mod2 = in_srctree / "mypkg" / "mod2.py"
    mod1.write_text("")
    mod2.write_text("")
    mod1.chmod(0o644)
    mod2.chmod(0o666)
    shutil.copy(backend, in_srctree)
    yield in_srctree


def test_sdist_reproducibility(srctree_modern):
    sdist = setuptools_reproducible.build_sdist(str(srctree_modern))
    assert sha256sum(srctree_modern / sdist) == expected_sdist_hash


def test_wheel_reproducibility(srctree_modern):
    wheel = setuptools_reproducible.build_wheel(str(srctree_modern))
    assert sha256sum(srctree_modern / wheel) == expected_wheel_hash
