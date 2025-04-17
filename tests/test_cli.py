from pathlib import Path

import pytest

from license_scanner.cli import Application, ApplicationError


def test_parameters() -> None:
    app = Application.from_args([])
    assert isinstance(app, Application)

    with pytest.raises(ApplicationError) as excinfo:
        Application.from_args(["parameters are not accepted"])
    assert excinfo.value.exit_code == 2


@pytest.mark.parametrize("args", [["-h"], ["--help"]])
def test_help(args: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(ApplicationError) as excinfo:
        Application.from_args(args)
    assert excinfo.value.exit_code == 0
    assert excinfo.value.message is None

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out.startswith("usage: ")


@pytest.mark.parametrize("args", [["-i"], ["--input-directory"]])
def test_input_directory(args: list[str], tmp_path: Path) -> None:
    idir = tmp_path / "valid"
    idir.mkdir()
    app = Application.from_args([*args, str(idir)])
    assert isinstance(app, Application)


@pytest.mark.parametrize("args", [["-i"], ["--input-directory"]])
def test_input_directory_errors(args: list[str], tmp_path: Path) -> None:
    idir = tmp_path / "does-not-exists"
    with pytest.raises(ApplicationError, match="invalid input directory") as excinfo:
        Application.from_args([*args, str(idir)])
    assert excinfo.value.exit_code == 2

    idir = tmp_path / "can-not-be-read"
    idir.mkdir(mode=0o000)
    with pytest.raises(ApplicationError, match="invalid input directory") as excinfo:
        Application.from_args([*args, str(idir)])
    assert excinfo.value.exit_code == 2
    idir.chmod(0o700)  # ensure the tmp_path can remove the directory

    idir = tmp_path / "not-a-directory"
    idir.write_text("invalid")
    with pytest.raises(ApplicationError, match="invalid input directory") as excinfo:
        Application.from_args([*args, str(idir)])
    assert excinfo.value.exit_code == 2


@pytest.mark.parametrize("args", [["-o"], ["--output-directory"]])
def test_output_directory(args: list[str], tmp_path: Path) -> None:
    odir = tmp_path / "present"
    odir.mkdir()
    app = Application.from_args([*args, str(odir)])
    assert isinstance(app, Application)

    odir = tmp_path / "can" / "be" / "created"
    app = Application.from_args([*args, str(odir)])
    assert isinstance(app, Application)


@pytest.mark.parametrize("args", [["-o"], ["--output-directory"]])
def test_output_directory_errors(args: list[str], tmp_path: Path) -> None:
    odir = tmp_path / "can-not-be-written"
    odir.mkdir(mode=0o555)  # dr-xr-xr-x
    with pytest.raises(ApplicationError, match="invalid output directory") as excinfo:
        Application.from_args([*args, str(odir)])
    assert excinfo.value.exit_code == 2

    odir = tmp_path / "not-a-directory"
    odir.write_text("invalid")
    with pytest.raises(ApplicationError, match="invalid output directory") as excinfo:
        Application.from_args([*args, str(odir)])
    assert excinfo.value.exit_code == 2
