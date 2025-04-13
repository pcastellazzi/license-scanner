from dataclasses import dataclass
from enum import StrEnum, auto
from functools import cached_property
from hashlib import sha256
from typing import NamedTuple

import packaging.licenses
import trove_classifiers

__all__ = ("License", "LicenseSource", "LicenseState", "PackageLicenses")


class LicenseSource(StrEnum):
    CLASSIFIER = auto()
    EXPRESSION = auto()
    LICENSE = auto()
    UNKNOWN = auto()


class LicenseState(StrEnum):
    AMBIGUOUS = auto()
    DEPRECATED = auto()
    INVALID = auto()
    VALID = auto()
    UNKNOWN = auto()


class License(NamedTuple):
    text: str
    source: LicenseSource
    state: LicenseState


@dataclass
class PackageLicenses:
    FILE_DETECTION_CUTOFF = 512
    CLASSIFIER_PREFIX = "License"
    CLASSIFIER_SEPARATOR = "::"

    name: str
    version: str
    license: str | None
    license_expression: str | None
    classifiers: list[str]

    @cached_property
    def licenses(self) -> list[License]:
        if lic := self._parse_license_expression():
            return [lic]
        if lic := self._parse_license():
            return [lic]
        if lic := self._parse_classifiers():
            return lic
        return [License("UNKNOWN", LicenseSource.UNKNOWN, LicenseState.UNKNOWN)]

    def _parse_license_expression(self) -> License | None:
        if self.license_expression:
            valid = self._parse_spdx_expression(self.license_expression)
            return License(
                self.license_expression,
                LicenseSource.EXPRESSION,
                LicenseState.VALID if valid else LicenseState.INVALID,
            )
        return None

    def _parse_license(self) -> License | None:
        if self.license:
            if self._parse_spdx_expression(self.license):
                return License(self.license, LicenseSource.LICENSE, LicenseState.VALID)

            if len(self.license) >= self.FILE_DETECTION_CUTOFF:
                digest = self._hash_license()
                return License(
                    f"sha256:{digest}", LicenseSource.LICENSE, LicenseState.AMBIGUOUS
                )
            return License(self.license, LicenseSource.LICENSE, LicenseState.AMBIGUOUS)
        return None

    def _parse_classifiers(self) -> list[License]:
        licenses: list[License] = []
        for classifier in self.classifiers:
            if classifier.startswith(self.CLASSIFIER_PREFIX):
                if classifier in trove_classifiers.classifiers:
                    text = classifier.split(self.CLASSIFIER_SEPARATOR)[-1].strip()
                    licenses.append(
                        License(text, LicenseSource.CLASSIFIER, LicenseState.VALID)
                    )
                    continue
                if classifier in trove_classifiers.deprecated_classifiers:
                    text = classifier.split(self.CLASSIFIER_SEPARATOR)[-1].strip()
                    licenses.append(
                        License(text, LicenseSource.CLASSIFIER, LicenseState.DEPRECATED)
                    )
                    continue
            licenses.append(
                License(classifier, LicenseSource.CLASSIFIER, LicenseState.INVALID)
            )
        return licenses

    def _parse_spdx_expression(self, expression: str) -> bool:
        try:
            packaging.licenses.canonicalize_license_expression(expression)
        except packaging.licenses.InvalidLicenseExpression:
            return False
        else:
            return True

    def _hash_license(self) -> str:
        # This method is only called when a license is of certain length.
        # self.license should never be None here.
        assert self.license is not None  # noqa: S101
        text = self.license or ""
        return sha256(text.encode()).hexdigest()
