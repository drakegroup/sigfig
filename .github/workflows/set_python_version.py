from pathlib import Path
import toml
from sys import argv

def apply_pyproject_python_version(version):
    pyproject_path = Path(__file__).parent / "../../pyproject.toml"
    with open(pyproject_path, "r") as f:
        pyproject = toml.load(f)
    pyproject["tool"]["poetry"]["dependencies"]["python"] = version
    with open(pyproject_path, "w") as f:
        f.write(toml.dumps(pyproject))

if __name__ == "__main__":
    apply_pyproject_python_version(argv[1])
