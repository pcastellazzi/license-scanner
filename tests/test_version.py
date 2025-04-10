from importlib.metadata import distribution


def test_true() -> None:
    assert distribution("license_scanner").version == "0.1.0"
