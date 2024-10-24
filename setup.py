from pathlib import Path
from setuptools import setup, find_packages
from yaml import safe_load
import toml

if __name__ == "__main__":
    pyproject = toml.load(Path(__file__).parent / 'pyproject.toml')
    setup(
        name = pyproject['tool']['poetry']['name'],
        description = pyproject['tool']['poetry']['description'],

        version = safe_load(open(Path(__file__).parent / 'CITATION.cff'))['version'],
        license = 'MIT',
        url = pyproject['tool']['poetry']['urls']['Homepage'],
        install_requires = ['SortedContainers'],
        packages = find_packages(exclude = ['doc', 'test']),
        long_description = open(Path(__file__).parent / 'README.rst', encoding='utf-8').read(),
        long_description_content_type = 'text/x-rst',
        author = pyproject['tool']['poetry']['authors'],
        maintainer = pyproject['tool']['poetry']['maintainers'],

        keywords = pyproject['tool']['poetry']['keywords'],
        classifiers = pyproject['tool']['poetry']['classifiers'],
    )
