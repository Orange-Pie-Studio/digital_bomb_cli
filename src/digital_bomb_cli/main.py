"""_summary_"""

import sys
from os import getpid
from pathlib import Path
from tomllib import load
from zipfile import ZipFile
from subprocess import Popen, DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP

import requests
from packaging.version import Version, InvalidVersion
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    TextColumn,
)

from digital_bomb_cli.core.index import index
from digital_bomb_cli.utils.i18n import _
from digital_bomb_cli.utils.setup_logging import setup_logging, end_logger

logger = setup_logging(__name__)
console = Console()
VERSION_PATH = Path(sys._MEIPASS) / "pyproject.toml" if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
API = f"https://api.github.com/repos/orange-pie-studio/digital_bomb_cli/releases/latest"

@end_logger(logger)
def get_local_version() -> Version:
    try:
            
        with VERSION_PATH.open('rb') as f:
            title = load(f)
            return Version(title["project"]["version"])
        
    except (FileNotFoundError, KeyError, InvalidVersion) as e:
        logger.exception(f"\n{e}")
        return Version("0.0.0")
    
@end_logger(logger)
def parse_version(s: str) -> Version | None:
    """_summary_"""
        
    a = get_local_version()
    b = Version(s)
    
    if b is None:
        return None
    
    return a < b

@end_logger(logger)
def download_by_pattern() -> str:
    """_summary_"""

    try:
        resp = requests.get(API)
        
    except requests.RequestException as e:
        logger.exception(f"\n{e}")
        return None
        
    resp.raise_for_status()
    data = resp.json()
    
    if not parse_version(data["tag_name"]):
        return None
    
    matched = [a for a in data["assets"] if a["name"].endswith(".zip")]
    matched = matched[0]
    print(_.t("main.update", local_version=get_local_version(), remote_version=data["tag_name"]))
    
    with Progress(
        TextColumn("[#FFFFFF]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None, style="#CD0000", complete_style="#00CD00"),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        
        name = matched["name"]
        url = matched["browser_download_url"]
        total = matched["size"]
        filepath = Path(".") / name

        task_id = progress.add_task(
            "download", filename=name, total=total
        )
        
        try:
            
            with requests.get(url, stream=True, allow_redirects=True) as r:
                r.raise_for_status()
                
                if total == 0:
                    total = int(r.headers.get("Content-Length", 0))
                    progress.update(task_id, total=total)

                with open(filepath, "wb") as f:
                    
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        
                        if not chunk:
                            continue
                        
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))
                        
        except requests.RequestException as e:
            logger.exception(f"\n{e}")
            return None

        progress.update(task_id, completed=total)

    return name

@end_logger(logger)
def extract_zip(zip_path: str) -> Path:
    """_summary_"""
    
    out_dir = Path(".") / "downloaded"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(_.t("main.extract"))
    
    with ZipFile(zip_path) as zf:
        
        for member in zf.namelist():
            target = (out_dir / member).resolve()
            
            if not str(target).startswith(str(out_dir.resolve())):
                raise RuntimeError(f"Invalid path: {member}")
            
        zf.extractall(out_dir)

@end_logger(logger)
def do_self_update(src_dir, dst_dir, exe_to_restart=None):
    """_summary_"""
    
    pid = getpid()
    src, dst = Path(src_dir), Path(dst_dir)

    bat = dst / "_update.bat"
    vbs = dst / "_update.vbs"

    bat.write_text(f"""@echo off
chcp 65001 >nul
:wait
tasklist /FI "PID eq {pid}" | find "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait
)
xcopy /E /Y /I "{src}\\*" "{dst}\\" >nul
{f'start "" "{exe_to_restart}"' if exe_to_restart else 'echo done'}
del "%~f0"
""",
encoding="utf-8"
)

    vbs.write_text(
        'Set sh = CreateObject("WScript.Shell")\n'
        f'sh.Run """{bat}""", 0, False\n'
        'WScript.Sleep 1500\n'
        f'CreateObject("Scripting.FileSystemObject").DeleteFile "{vbs}"\n',
        encoding="utf-8"
    )

    Popen(
        ["wscript.exe", str(vbs)],
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )

    sys.exit(0)

if __name__ == "__main__":
    print(_.t("main.instcructions", version=get_local_version()))
    
    if getattr(sys, "frozen", False):
        downloaded_file = download_by_pattern()
        
        if downloaded_file:
            extract_zip(downloaded_file)
            do_self_update("downloaded", ".", exe_to_restart=sys.executable)
    
    while True:
        index()