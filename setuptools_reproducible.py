import os
import stat
import tarfile
from contextlib import contextmanager
from types import SimpleNamespace

from setuptools.build_meta import *
from setuptools.build_meta import build_sdist as build_sdist_orig
from setuptools.build_meta import build_wheel as build_wheel_orig


class FixedMode:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if instance.isdir():
            return stat.S_IFMT(instance._mode) | 0o755
        elif instance.isreg():
            return stat.S_IFMT(instance._mode) | 0o644
        else:
            return instance._mode

    def __set__(self, instance, value):
        instance._mode = value


class FixedAttr:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.value() if callable(self.value) else self.value

    def __set__(self, instance, value):
        pass


class TarInfoNew(tarfile.TarInfo):
    mode = FixedMode()
    mtime = FixedAttr(lambda: float(os.environ["SOURCE_DATE_EPOCH"]))
    uid = FixedAttr(0)
    gid = FixedAttr(0)
    uname = FixedAttr("")
    gname = FixedAttr("")


@contextmanager
def monkey():
    tarfile_time_orig = tarfile.time
    tarinfo_orig = tarfile.TarFile.tarinfo
    source_date_epoch_orig = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch_orig is None:
        os.environ["SOURCE_DATE_EPOCH"] = "0"  # 1970-01-01 00:00:00 UTC
    tarfile.TarFile.tarinfo = TarInfoNew
    tarfile.time = SimpleNamespace(time=lambda: float(os.environ["SOURCE_DATE_EPOCH"]))
    try:
        yield
    finally:
        tarfile.time = tarfile_time_orig
        tarfile.TarFile.tarinfo = tarinfo_orig
        if source_date_epoch_orig is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)


def build_sdist(sdist_directory, config_settings=None):
    with monkey():
        return build_sdist_orig(sdist_directory, config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    with monkey():
        return build_wheel_orig(wheel_directory, config_settings, metadata_directory)
