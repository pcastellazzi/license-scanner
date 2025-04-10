#!/usr/bin/env -S uv run

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "diskcache==5.6.3",
#   "httpx==0.28.1",
#   "packaging==24.2",
#   "pydantic==2.11.2",
# ]
# ///

"""
Recursively download the metadata of the top 100 most downloaded packages from
PyPI and save it in the `tests/samples` directory.

Each file is named after the package name and contains its metadata in JSON
format.

A cache folder, `.cache`, is created in the current working directory. Each
entry contains the full response from the PyPI JSON API, in case we need to
change our internal representation of the data.

Usage:

```bash
$ ./scripts/generate-test-data.py
```

alternatively, you can run it with `uv`:

```bash
$ uv run ./scripts/generate-test-data.py
```

This script is meant to be run from the root of the repository.
"""

import contextlib
import pathlib
import typing
from collections.abc import Callable, Generator

import diskcache
import httpx
from packaging.requirements import InvalidRequirement, Requirement
from pydantic import AliasGenerator, AliasPath, BaseModel, ConfigDict, ValidationError

PYPI_STATS = "https://pypi.org/stats/"
PYPI_PACKAGE_METADATA = "https://pypi.org/pypi/%s/json"


class Stats(BaseModel):
    """
    Top packages from PyPI stats.
    Reference: <https://docs.pypi.org/api/stats/>.
    """

    model_config = ConfigDict(strict=True)
    top_packages: dict[str, dict[str, int]]
    total_packages_size: int


class PackageMetadata(BaseModel):
    """
    Some package metadata from PyPI.

    This is a simplified version of the metadata available and only includes
    the fields that are relevant for the tests.

    Reference: <https://docs.pypi.org/api/json/>.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda field: AliasPath("info", field)
        ),
        strict=False,
    )

    classifiers: list[str]
    license: str | None
    license_expression: str | None
    name: str
    requires_dist: list[str] | None
    version: str


@contextlib.contextmanager
def http_client() -> Generator[Callable[[str], str]]:
    cache = diskcache.Cache(pathlib.Path.cwd() / ".cache")
    client = httpx.Client()
    client.follow_redirects = False
    client.headers["Accept"] = "application/json"
    client.timeout = 10  # connect/read/write/pool

    def http_get(url: str) -> str:
        if url not in cache:
            response = client.get(url)
            response.raise_for_status()
            cache[url] = response.text
        return typing.cast("str", cache[url])

    with cache, client:
        yield http_get


def main() -> None:
    metadata_dir = pathlib.Path.cwd() / "tests" / "samples"
    metadata_dir.mkdir(exist_ok=True, parents=True)

    visited: set[str] = set()

    def save_package_metadata(http_get: Callable[[str], str], package: str) -> None:
        if package in visited:
            return

        httpdata = http_get(PYPI_PACKAGE_METADATA % package)
        metadata = PackageMetadata.model_validate_json(httpdata)

        package_json = metadata.model_dump_json(indent=4)
        package_file = metadata_dir / f"{package}.json"
        package_file.write_text(package_json)

        visited.add(package)

        # We don't try to parse requirements correctly, just to ignore
        # development dependencies to keep the whole list managable.
        for requirement in metadata.requires_dist or []:
            try:
                if not (r := Requirement(requirement)).marker:
                    save_package_metadata(http_get, r.name)
            except InvalidRequirement:
                pass

    with http_client() as http_get:
        stats = Stats.model_validate_json(http_get(PYPI_STATS))
        for package in stats.top_packages:
            print(package, len(visited))
            save_package_metadata(http_get, package)


if __name__ == "__main__":

    def fail(message: str) -> None:
        import sys

        print(message, file=sys.stderr, flush=True)
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        pass
    except httpx.HTTPError as exc:
        fail(f"ERROR: HTTP Error: {exc!s}.")
    except ValidationError as exc:
        fail(f"ERROR: Validation Error: {exc!s}.")
