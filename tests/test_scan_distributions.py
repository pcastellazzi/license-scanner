import email.message
from dataclasses import dataclass

import pytest

from license_scanner.scanner import scan_distributions


@dataclass(kw_only=True)
class MockDistribution:
    name: str
    version: str
    license: str | None = None
    license_expression: str | None = None
    classifiers: list[str] | None = None

    def __post_init__(self) -> None:
        self.metadata = email.message.Message()
        if self.license:
            self.metadata["License"] = self.license
        if self.license_expression:
            self.metadata["License-Expression"] = self.license_expression
        if self.classifiers:
            for classifier in self.classifiers:
                self.metadata["Classifier"] = classifier


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    example = MockDistribution(name="test-package", version="1.0.0")
    monkeypatch.setattr("importlib.metadata.distributions", lambda: [example])
    result = list(scan_distributions())

    assert len(result) == 1
    assert result[0].name == "test-package"
    assert result[0].version == "1.0.0"
    assert result[0].license is None
    assert result[0].license_expression is None
    assert result[0].classifiers == []


def test_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    example = MockDistribution(
        name="test-package",
        version="1.0.0",
        license="BSD",
        license_expression="MIT",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: Apache Software License",
            "License :: OSI Approved :: MIT License",
        ],
    )
    monkeypatch.setattr("importlib.metadata.distributions", lambda: [example])
    result = list(scan_distributions())

    assert len(result) == 1
    assert result[0].name == "test-package"
    assert result[0].version == "1.0.0"
    assert result[0].license == "BSD"
    assert result[0].license_expression == "MIT"
    assert set(result[0].classifiers) == {
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: MIT License",
    }
