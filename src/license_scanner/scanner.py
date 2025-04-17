import sys
from typing import TYPE_CHECKING

from license_scanner import PackageLicenses

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class ScanError(Exception):
    pass


def scan_directory(base: "Path") -> "Iterator[PackageLicenses]":
    import json

    for jsonfile in base.glob("*.json"):
        try:
            with jsonfile.open(mode="rb") as fd:
                jsondata = json.load(fd)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            message = f"Can't read {jsonfile}. {exc}"
            raise ScanError(message) from None

        try:
            yield PackageLicenses(
                name=jsondata.get("name", ""),
                version=jsondata.get("version", ""),
                license=jsondata.get("license", None),
                license_expression=jsondata.get("license_expression", None),
                classifiers=jsondata.get("classifiers", []),
            )
        except AttributeError as exc:
            message = f"Invalid format {jsonfile}. {exc}"
            raise ScanError(message) from None


if sys.version_info >= (3, 12):

    def scan_distributions() -> "Iterator[PackageLicenses]":
        import importlib.metadata

        # Distribution.metadata is an email.message.Message instance.
        # __getitem__ was fixed in 3.12 and a get() was added, we use it
        for dist in importlib.metadata.distributions():
            yield PackageLicenses(
                name=dist.name,
                version=dist.version,
                license=dist.metadata.get("License", None),
                license_expression=dist.metadata.get("License-Expression", None),
                classifiers=dist.metadata.get_all("Classifier", []),
            )

else:

    def scan_distributions() -> "Iterator[PackageLicenses]":
        import importlib.metadata

        # Distribution.metadata is an email.message.Message instance.
        # __getitem__ returns None instead of raising KeyError
        for dist in importlib.metadata.distributions():
            yield PackageLicenses(
                name=dist.name,
                version=dist.version,
                license=dist.metadata["License"],
                license_expression=dist.metadata["License-Expression"],
                classifiers=dist.metadata.get_all("Classifier", []),
            )
