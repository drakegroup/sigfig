CI Flow
=======

Development, documentation, and publishing dependencies require Python 3.10+
to use security-patched releases. Use ``uv sync --locked --all-groups
--all-extras`` with the Python version in ``.python-version`` to install them.
The library itself still supports Python 3.8+, tested separately by
``old_python_test.yaml`` without the development dependency group.

With every merge to `master`:

* The app's patch version is bumped (unless the version is manually set).
* Tests are run and a coverage badge is generated.
* The above changes are committed and pushed to the repository.
* The package is published to PyPI.
