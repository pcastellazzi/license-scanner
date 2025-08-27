#!/usr/bin/env -S uv run

"""
Recursively download the metadata of the top 100 most downloaded packages from
PyPI and save it in the `tests/samples` directory.

Each file is named after the package name and contains its metadata in JSON
format.

Usage:

```bash
$ ./scripts/generate-test-data.py
```

Alternatively, you can run it with `uv`:

```bash
$ uv run ./scripts/generate-test-data.py
```

This script is meant to be run from the root of the repository.
"""

from json import dumps as jsondumps
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement

from license_scanner.pypi import Client

ROOT_DIR = Path(__file__).parent.parent


def main() -> None:
    metadata_dir = ROOT_DIR / "tests" / "top100"
    metadata_dir.mkdir(exist_ok=True, parents=True)

    visited: set[str] = set()

    with Client() as pypi:

        def save_package_metadata(package: str) -> None:
            if package in visited:
                return

            metadata = pypi.get_package(package)
            package_json = jsondumps(metadata._asdict(), indent=4)
            package_file = metadata_dir / f"{package}.json"
            package_file.write_text(package_json)

            visited.add(package)

            # We don't try to parse requirements correctly, just to ignore
            # development dependencies to keep the whole list managable.
            for requirement in metadata.requires_dist or []:
                try:
                    if not (r := Requirement(requirement)).marker:
                        save_package_metadata(r.name)
                except InvalidRequirement:
                    pass

        stats = pypi.get_stats()
        for package in stats.top_packages:
            print(package, len(visited))
            save_package_metadata(package)


if __name__ == "__main__":
    from contextlib import suppress

    with suppress(KeyboardInterrupt):
        main()
