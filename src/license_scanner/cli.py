"""
Show the licenses of the installed packages on this particular environment.

If the optional --output-directory flag is present, text that looks like a
license file will be stored there. This happens when the text of a license is
embedded in the license field of a package metadata.

Licensing Rules:

- SPDX identifiers are considered valid licenses
- Trove classifiers are considered valid licenses if they are not deprecated
- Trove classifiers may be reported multiple times
- Large text (>1k) is considered a license file and stored if requested
- Large text is considered AMBIGUOUS, meaning we don't know what they are

License Sources:

- CLASSIFIER: The result of parsing a Classifier field
- EXPRESSION: The result of parsing the License-Expression field
- LICENSE: The result of parsing the License field

License States:

- AMBIGUOUS: The program does not understand the content of the fields
- DEPRECATED: A deprecated trove classifier is used
- INVALID: An invalid license expression or trove classifier
- VALID: A valid license expression or trove classifier
"""

from argparse import ArgumentError, ArgumentParser
from json import dump as jsondump
from pathlib import Path
from sys import stderr, stdout
from typing import TYPE_CHECKING

from license_scanner.scanner import ScanError, scan_directory, scan_distributions

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from typing import Self

    from license_scanner import PackageLicenses


class ApplicationError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.message = message


class Application:
    @classmethod
    def from_args(cls, argv: "Sequence[str] | None" = None) -> "Self":
        argp = ArgumentParser(prog="license-scanner", exit_on_error=False)
        argp.add_argument(
            "-i",
            "--input-directory",
            type=Path,
            help="Directory to scan for license files",
        )
        argp.add_argument(
            "-o",
            "--output-directory",
            type=Path,
            help="Directory to store license files",
        )
        try:
            args = argp.parse_args(argv)
            return cls(args.input_directory, args.output_directory)
        except ArgumentError as exc:
            raise ApplicationError(str(exc), exit_code=2) from exc

    def __init__(
        self,
        input_directory: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        self._idir = input_directory
        self._odir = output_directory

    def run(self) -> int:
        try:
            self._create_output_directory()
            licenses = list(self._get_licenses())
            jsondump(licenses, stdout, indent=4)
        except ApplicationError as exc:
            print(f"ERROR: {exc}", file=stderr, flush=True)
            return exc.exit_code
        else:
            return 0

    def _create_output_directory(self) -> None:
        if self._odir:
            try:
                self._odir.mkdir(exist_ok=True, parents=True)
            except OSError as exc:
                message = f"Can't create output directory: {self._odir}. {exc}"
                raise ApplicationError(message) from exc

    def _get_packages(self) -> "Iterator[PackageLicenses]":
        if self._idir:
            try:
                return scan_directory(self._idir)
            except ScanError as exc:
                message = f"Can't scan directory: {self._idir}. {exc}"
                raise ApplicationError(message) from exc
        else:
            return scan_distributions()

    def _get_licenses(self) -> "Iterator[dict[str,str]]":
        for package in self._get_packages():
            for license in package.licenses:  # noqa: A001
                yield {
                    "package-name": package.name,
                    "package-version": package.version,
                    "license": license.text[0:48],
                    "source": license.source.capitalize(),
                    "state": license.state.upper(),
                }
                self._try_save_license(package.license, license.text)

    def _try_save_license(self, text: str | None, identifier: str) -> None:
        if self._odir and text and identifier.startswith("sha256:"):
            digest = identifier[7:]
            file = self._odir / f"{digest}.txt"
            try:
                file.write_text(text)
            except OSError as exc:
                message = f"Can't write license file: {file}. {exc}"
                raise ApplicationError(message) from exc


def main() -> int:
    try:
        app = Application.from_args()
        return app.run()
    except ApplicationError as exc:
        print(f"ERROR: {exc}", file=stderr, flush=True)
        return exc.exit_code
