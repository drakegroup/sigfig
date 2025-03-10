CI Flow
=======

With every merge to `master`:

* The app's patch version is bumped (unless the version is manually set).
* Tests are run and a coverage badge is generated.
* The above changes are committed and pushed to the repository.
* The package is published to PyPI.
