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


def scan_distributions() -> "Iterator[PackageLicenses]":
    import importlib.metadata

    # Distribution.metadata is an email.message.Message instance.
    # It returns None instead of raising KeyError
    for distribution in importlib.metadata.distributions():
        yield PackageLicenses(
            name=distribution.name,
            version=distribution.version,
            license=distribution.metadata["License"],
            license_expression=distribution.metadata["License-Expression"],
            classifiers=distribution.metadata.get_all("Classifier", []),
        )
