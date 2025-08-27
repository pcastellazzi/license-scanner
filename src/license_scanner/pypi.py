from os import environ
from types import TracebackType
from typing import NamedTuple, Self

import httpx

PYPI_RETRIES = int(environ.get("PYPI_RETRIES", "3"))
PYPI_TIMEOUT = float(environ.get("PYPI_TIMEOUT", "10.0"))

PYPI_PACKAGE = "https://pypi.org/pypi/{package}/json"
PYPI_STATS = "https://pypi.org/stats/"


class Package(NamedTuple):
    """
    This is a simplified version of the metadata available and only includes
    the fields that are relevant for the tests.
    Reference: <https://docs.pypi.org/api/json/>.
    """

    classifiers: list[str]
    license: str | None
    license_expression: str | None
    name: str
    requires_dist: list[str] | None
    version: str


class Stats(NamedTuple):
    """
    Top packages from PyPI stats.
    Reference: <https://docs.pypi.org/api/stats/>.
    """

    top_packages: dict[str, dict[str, int]]
    total_packages_size: int


class Client:
    """
    Follow the HTTP client unspoken rules:
    - Use a session
    - Explicitly allow/dissallow redirects
    - Set retries
    - Set timeouts
    - Use your library "response.raise_for_status" equivalent
    - Use your library "response.json" equivalent
    """

    def __init__(self) -> None:
        self._session = httpx.Client(
            follow_redirects=False,
            headers={"Accept": "application/json"},
            timeout=PYPI_TIMEOUT,
            transport=httpx.HTTPTransport(retries=PYPI_RETRIES),
        )

    def get_package(self, package: str) -> Package:
        data = self._session.get(PYPI_PACKAGE.format(package=package)).json()
        return Package(**{f: data["info"][f] for f in Package._fields})

    def get_stats(self) -> Stats:
        data = self._session.get(PYPI_STATS).json()
        return Stats(**{f: data[f] for f in Stats._fields})

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._session.close()
