"""Wellmanifest governance gate runtime — ``wellman``.

Distributes the deterministic governance checker as an installable package
instead of vendoring 187KB+ scripts into every adopting repository.

Usage::

    python -m wellman check --root /path/to/repo
    wellman check --root /path/to/repo
"""
from importlib.metadata import version as _version

try:
    __version__ = _version("wellman")
except Exception:
    __version__ = "0.0.0-dev"
