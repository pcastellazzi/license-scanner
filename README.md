# license-scanner

`license-scanner` is a tool to list the license of all the dependencies in
your Python project.

## Installation

```bash
pip install git+https://github.com/pcastellazzi/license-scanner.git
```

## Usage

- List package licenses

  ```bash
  license-scanner
  ```

- View the inline documentation

  ```bash
  license-scanner --help
  ```

  Also available [here](https://github.com/pcastellazzi/license-scanner/blob/master/src/license_scanner/cli.py).

## Development

- [uv](https://docs.astral.sh/uv/) is used for project management
- [GNU Make](https://www.gnu.org/software/make/) is used to glue tasks
- [pytest](https://pytest.org) is the test runner

For more details check
[python-project](https://github.com/pcastellazzi/python-project), the template
used to build this project.
