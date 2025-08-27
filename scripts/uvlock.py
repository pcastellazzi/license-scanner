#!/usr/bin/env -S uv run

import json
import pathlib
import tomllib

from license_scanner.pypi import Client

ROOT_DIR = pathlib.Path(__file__).parent.parent
UVLOCK_FILE = pathlib.Path(ROOT_DIR) / "uv.lock"


def uvlock_packages() -> list[str]:
    with UVLOCK_FILE.open(mode="rb") as fd:
        return [p["name"] for p in tomllib.load(fd)["package"]]


def main() -> None:
    metadata_dir = ROOT_DIR / "tests" / "uvlock"
    metadata_dir.mkdir(exist_ok=True, parents=True)

    with Client() as pypi:

        def save_package_metadata(package: str) -> None:
            metadata = pypi.get_package(package)
            package_json = json.dumps(metadata._asdict(), indent=4)
            package_file = metadata_dir / f"{package}.json"
            package_file.write_text(package_json)

        for package in uvlock_packages():
            print(package)
            save_package_metadata(package)


if __name__ == "__main__":
    from contextlib import suppress

    with suppress(KeyboardInterrupt):
        main()
