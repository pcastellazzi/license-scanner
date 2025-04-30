import json
from pathlib import Path

import pytest

from license_scanner import LicenseSource, LicenseState
from license_scanner.cli import main

TOP100 = Path(__file__).parent / "top100"

if not TOP100.is_dir():
    pytest.fail("samples directory not found, run `make top100` to create it")


def verify_output(odir: Path, output: str) -> None:
    # the type is a suggestion, we assert to ensure the it is correct
    result: list[dict[str, str]] = json.loads(output)
    assert isinstance(result, list)

    expected_fields = {"package-name", "package-version", "license", "source", "state"}
    for lic in result:
        assert isinstance(lic, dict)
        assert set(lic.keys()) == expected_fields
        assert lic["source"].lower() in LicenseSource.__members__.values()
        assert lic["state"].lower() in LicenseState.__members__.values()

        if lic["license"].startswith("sha256:"):
            digest = lic["license"][7:]
            assert len(digest) == 64, repr(lic)
            assert (odir / f"{digest}.txt").is_file()


def test_current_project(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    odir = tmp_path / "output"
    assert main(["-o", str(odir)]) == 0

    output = capsys.readouterr()
    assert output.err == ""
    assert len(output.out) > 0
    verify_output(odir, output.out)


def test_top100(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    odir = tmp_path / "output"
    assert main(argv=["-i", str(TOP100), "-o", str(odir)]) == 0

    output = capsys.readouterr()
    assert output.err == ""
    assert len(output.out) > 0
    verify_output(odir, output.out)
