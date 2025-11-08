"""VIRA Iteration 1 prototype package."""

from importlib import metadata


def get_version() -> str:
    """Return the installed package version."""

    try:
        return metadata.version("vira")
    except metadata.PackageNotFoundError:
        return "0.0.0"

