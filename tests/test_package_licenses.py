from license_scanner import LicenseSource, LicenseState, PackageLicenses


def test_valid_license_expression() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression="MIT",
        classifiers=[],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "MIT"
    assert package.licenses[0].source == LicenseSource.EXPRESSION
    assert package.licenses[0].state == LicenseState.VALID


def test_invalid_license_expression() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression="INVALID",
        classifiers=[],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "INVALID"
    assert package.licenses[0].source == LicenseSource.EXPRESSION
    assert package.licenses[0].state == LicenseState.INVALID


def test_valid_license() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license="MIT",
        license_expression=None,
        classifiers=[],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "MIT"
    assert package.licenses[0].source == LicenseSource.LICENSE
    assert package.licenses[0].state == LicenseState.VALID


def test_file_detection_cutoff() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=" " * PackageLicenses.FILE_DETECTION_CUTOFF,
        license_expression=None,
        classifiers=[],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text.startswith("sha256:")
    assert package.licenses[0].source == LicenseSource.LICENSE
    assert package.licenses[0].state == LicenseState.AMBIGUOUS


def test_ambiguous_license() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license="INVALID",
        license_expression=None,
        classifiers=[],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "INVALID"
    assert package.licenses[0].source == LicenseSource.LICENSE
    assert package.licenses[0].state == LicenseState.AMBIGUOUS


def test_valid_classifier() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression=None,
        classifiers=["Operating System :: Unix"],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "UNKNOWN"
    assert package.licenses[0].source == LicenseSource.UNKNOWN
    assert package.licenses[0].state == LicenseState.UNKNOWN


def test_valid_license_classifier() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression=None,
        classifiers=["License :: OSI Approved :: GNU General Public License (GPL)"],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "GNU General Public License (GPL)"
    assert package.licenses[0].source == LicenseSource.CLASSIFIER
    assert package.licenses[0].state == LicenseState.VALID


def test_invalid_classifier() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression=None,
        classifiers=["INVALID"],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "UNKNOWN"
    assert package.licenses[0].source == LicenseSource.UNKNOWN
    assert package.licenses[0].state == LicenseState.UNKNOWN


def test_invalid_license_classifier() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression=None,
        classifiers=["License :: OSI Approved :: INVALID"],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "License :: OSI Approved :: INVALID"
    assert package.licenses[0].source == LicenseSource.CLASSIFIER
    assert package.licenses[0].state == LicenseState.INVALID


def test_deprecated_classifier() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression=None,
        classifiers=["License :: OSI Approved :: Intel Open Source License"],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "Intel Open Source License"
    assert package.licenses[0].source == LicenseSource.CLASSIFIER
    assert package.licenses[0].state == LicenseState.DEPRECATED


def test_unknown() -> None:
    package = PackageLicenses(
        name="test-package",
        version="1.0.0",
        license=None,
        license_expression=None,
        classifiers=[],
    )
    assert len(package.licenses) == 1
    assert package.licenses[0].text == "UNKNOWN"
    assert package.licenses[0].source == LicenseSource.UNKNOWN
    assert package.licenses[0].state == LicenseState.UNKNOWN
