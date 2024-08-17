# -*- coding: utf-8 -*-
from importlib import metadata

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'os-vol'
    __version__ = metadata.version(dist_name)
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = 'unknown'
finally:
    del metadata.version, metadata.PackageNotFoundError
