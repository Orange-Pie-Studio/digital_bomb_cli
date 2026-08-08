"""_summary_"""

from pathlib import Path
from tomllib import load
from shutil import get_terminal_size
from importlib.metadata import version

CUT: str = "=" * get_terminal_size().columns

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
SAVE_DIR: Path = PROJECT_ROOT / "saves"
EXP_PATH: Path = SAVE_DIR / "exp.json"
VERSION_PATH: Path = PROJECT_ROOT / "pyproject.toml"

REPO: str = "Orange-Pie-Studio/digital_bomb"
SRC_DIR: Path = Path(__file__).resolve().parent

with open(VERSION_PATH, "rb") as f:
    data: dict[str, str] = load(f)
    __version__: str = data["project"]["version"] or version("digital_bomb")