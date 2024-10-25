from pathlib import Path
from datetime import datetime
from yaml import safe_load, safe_dump
import toml
from requests import get
from semver import Version
import click

citation_path = Path(__file__).parent / "../../CITATION.cff"

local_version = safe_load(open(citation_path))['version']
local_version = Version.parse(local_version)

def apply_citation_version(version):
    citation_path = Path(__file__).parent / "../../CITATION.cff"
    with open(citation_path, "r") as f:
        citation = safe_load(f)
    citation["version"] = str(version)
    citation["date-released"] = datetime.now().strftime("%Y-%m-%d")
    with open(citation_path, "w") as f:
        f.write(safe_dump(citation, sort_keys=False))
        
def apply_pyproject_version(version):
    pyproject_path = Path(__file__).parent / "../../pyproject.toml"
    with open(pyproject_path, "r") as f:
        pyproject = toml.load(f)
    pyproject["tool"]["poetry"]["version"] = str(version)
    with open(pyproject_path, "w") as f:
        f.write(toml.dumps(pyproject))

def get_version():
    print(local_version)

def increment_version():
    published_version = Version.parse(get('https://pypi.org/pypi/sigfig/json').json()['info']['version'])
    if local_version > published_version:
        return
    new_version = published_version.bump_patch()
    apply_citation_version(new_version)
    apply_pyproject_version(new_version)

@click.command()
@click.option('--increment', is_flag=True, help='Increment the app\'s patch version.')
@click.option('--get', is_flag=True, help='Print the app\'s version stored in /CITATION.cff.')
def main(increment, get):
    """Tool to increment and/or display the app version stored in /CITATION.cff and /pyproject.toml."""
    if increment:
        increment_version()
    if get:
        get_version()

if __name__ == "__main__":
    main()
