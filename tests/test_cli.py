from json import dumps as jsondumps
from pathlib import Path

import pytest

from license_scanner.cli import Application, ApplicationError, main


def test_parameters() -> None:
    app = Application.from_args([])
    assert isinstance(app, Application)

    with pytest.raises(ApplicationError) as excinfo:
        Application.from_args(["parameters are not accepted"])
    assert excinfo.value.exit_code == 2


@pytest.mark.parametrize("args", [["-h"], ["--help"]])
def test_help(args: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert main(args) == 0
    output = capsys.readouterr()
    assert output.err == ""
    assert output.out.startswith("usage: ")


@pytest.mark.parametrize("args", [["-i"], ["--input-directory"]])
def test_input_directory(args: list[str], tmp_path: Path) -> None:
    idir = tmp_path / "valid"
    idir.mkdir()
    assert main([*args, str(idir)]) == 0


@pytest.mark.parametrize("args", [["-i"], ["--input-directory"]])
def test_input_directory_errors(
    args: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def verify(idir: Path) -> None:
        assert main([*args, str(idir)]) == 2
        output = capsys.readouterr()
        assert output.err.startswith("ERROR: ")
        assert "invalid input directory" in output.err

    idir = tmp_path / "does-not-exists"
    verify(idir)

    idir = tmp_path / "can-not-be-read"
    idir.mkdir(mode=0o000)
    verify(idir)
    idir.chmod(0o700)  # ensure the tmp_path can remove the directory

    idir = tmp_path / "not-a-directory"
    idir.write_text("invalid")
    verify(idir)


@pytest.mark.parametrize("args", [["-o"], ["--output-directory"]])
def test_output_directory(args: list[str], tmp_path: Path) -> None:
    odir = tmp_path / "present"
    odir.mkdir()
    assert main([*args, str(odir)]) == 0

    odir = tmp_path / "can" / "be" / "created"
    assert main([*args, str(odir)]) == 0


@pytest.mark.parametrize("args", [["-o"], ["--output-directory"]])
def test_output_directory_errors(
    args: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def verify(odir: Path) -> None:
        assert main([*args, str(odir)]) == 2
        output = capsys.readouterr()
        assert output.err.startswith("ERROR: ")
        assert "invalid output directory" in output.err

    odir = tmp_path / "can-not-be-written"
    odir.mkdir(mode=0o555)  # dr-xr-xr-x
    verify(odir)

    odir = tmp_path / "not-a-directory"
    odir.write_text("invalid")
    verify(odir)


def test_scan_error_is_masked(tmp_path: Path) -> None:
    file = tmp_path / "bad-encoding.json"
    file.write_bytes(b'{"text": "invalid utf-8 \x80"}')

    app = Application(tmp_path, tmp_path)
    with pytest.raises(ApplicationError) as excinfo:
        app.run()
    assert excinfo.value.exit_code == 1
    assert excinfo.value.message
    assert excinfo.value.message.startswith("Can't scan directory")


def test_save_license_error(tmp_path: Path) -> None:
    package: dict[str, str | list[str]] = {
        "name": "example-package",
        "version": "1.0.0",
        "license": "very-big-string" * 200,
        "license_expression": "",
        "classifiers": ["Programming Language :: Python :: 3"],
    }

    idir = tmp_path / "input"
    idir.mkdir()
    (idir / "example-package.json").write_text(jsondumps(package))

    odir = tmp_path / "output"
    odir.mkdir(mode=0o555)  # not writable

    app = Application(idir, odir)
    with pytest.raises(ApplicationError) as excinfo:
        app.run()
    assert excinfo.value.exit_code == 1
    assert excinfo.value.message
    assert excinfo.value.message.startswith("Can't write license file")
