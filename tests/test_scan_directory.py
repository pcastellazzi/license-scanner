from json import dumps as jsondumps
from typing import TYPE_CHECKING

import pytest

from license_scanner.scanner import ScanError, scan_directory

if TYPE_CHECKING:
    from pathlib import Path


def test_defaults(tmp_path: "Path") -> None:
    example = {}
    json_file = tmp_path / "example-package.json"
    json_file.write_text(jsondumps(example))
    results = list(scan_directory(tmp_path))

    assert len(results) == 1
    assert results[0].name == ""
    assert results[0].version == ""
    assert results[0].license is None
    assert results[0].license_expression is None
    assert results[0].classifiers == []


def test_metadata(tmp_path: "Path") -> None:
    example: dict[str, str | list[str]] = {
        "name": "example-package",
        "version": "1.0.0",
        "license": "BSD",
        "license_expression": "MIT",
        "classifiers": ["Programming Language :: Python :: 3"],
    }
    json_file = tmp_path / "example-package.json"
    json_file.write_text(jsondumps(example))
    results = list(scan_directory(tmp_path))

    assert len(results) == 1
    assert results[0].name == "example-package"
    assert results[0].version == "1.0.0"
    assert results[0].license == "BSD"
    assert results[0].license_expression == "MIT"
    assert results[0].classifiers == ["Programming Language :: Python :: 3"]


def test_encoding_error(tmp_path: "Path") -> None:
    file = tmp_path / "bad-encoding.json"
    file.write_bytes(b'{"text": "invalid utf-8 \x80"}')
    with pytest.raises(ScanError):
        list(scan_directory(tmp_path))


def test_invalid_json(tmp_path: "Path") -> None:
    file = tmp_path / "invalid.json"
    file.write_bytes(b'{"invalid json"}')
    with pytest.raises(ScanError):
        list(scan_directory(tmp_path))


def test_io_error(tmp_path: "Path") -> None:
    file = tmp_path / "unreadable-file.json"
    file.write_text("")
    file.chmod(0o000)  # make it unreadable
    with pytest.raises(ScanError):
        list(scan_directory(tmp_path))


def test_invalid_object(tmp_path: "Path") -> None:
    file = tmp_path / "invalid-object.json"
    file.write_text("[]")
    with pytest.raises(ScanError):
        list(scan_directory(tmp_path))
