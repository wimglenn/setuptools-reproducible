# setuptools-reproducible

This is a [PEP 517 Build backend][1] enabling [reproducible builds][2] with [setuptools][3].

Setuptools can create reproducible wheel archives (.whl) by setting [`SOURCE_DATE_EPOCH`][4] at build time, but setting the env var is insufficient for creating reproducible sdists (.tar.gz).

setuptools-reproducible wraps the hooks [`build_sdist`][5] and [`build_wheel`][6] with some modifications to make reproducible builds by default:

- In the build environment, `SOURCE_DATE_EPOCH=0` will be used if it wasn't already configured.
- Tarfile modes are set to 0o644 for regular files and 0o755 for directories.
- The uid/gid of archive members are set to 0, and the username/groupname are set to empty string.
- Gzip header values set to source date epoch.

With these modifications, a source tree with the same content should result in a built package with the same checksum.


### Usage:

The backend functions identically to upstream setuptools.
The only thing a user needs to change is to specify the build system in `pyproject.toml`:

```
[build-system]
requires = ["setuptools-reproducible"]
build-backend = "setuptools_reproducible"
```

Setting `SOURCE_DATE_EPOCH` is unnecessary, unless you want to override the default value of `0` i.e. _1970-01-01 00:00:00 UTC_.


#### Acknowledgements:

This implementation was inspired by a helpful comment from [Lisandro Dalcin][7] in [setuptools issue #2133][8], and also used some ideas from the project [repro-tarfile][9].

[1]: https://peps.python.org/pep-0517/#build-backend-interface
[2]: https://reproducible-builds.org/
[3]: https://setuptools.pypa.io/en/latest/
[4]: https://reproducible-builds.org/docs/source-date-epoch/
[5]: https://peps.python.org/pep-0517/#build-sdist
[6]: https://peps.python.org/pep-0517/#build-wheel
[7]: https://github.com/dalcinl
[8]: https://github.com/pypa/setuptools/issues/2133#issuecomment-1691158410
[9]: https://github.com/drivendataorg/repro-tarfile/
