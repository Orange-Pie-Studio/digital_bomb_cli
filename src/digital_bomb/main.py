"""_summary_"""

import shutil
import tempfile
import zipfile
import tomllib
from pathlib import Path

import requests
from packaging import version
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from digital_bomb.config import REPO, SRC_DIR as GAME_DIR, __version__, VERSION_PATH
from digital_bomb.core.index import index

console: Console = Console()

class GameUpdater:
    def __init__(self):
        self.local_ver = __version__
        self.release_data: dict | None = None
        self.latest_ver: str | None = None

    def _write_local_version(self, ver: str):
        """_summary_

        :param ver: _description_
        :type ver: str
        """

        with open(VERSION_PATH, "rb") as f:
            data: dict[str, str] = tomllib.load(f)
            data["project"]["version"] = ver

    def fetch_release_info(self) -> tuple[str | None, dict | None]:
        """_summary_

        :return: _description_
        :rtype: tuple[str | None, dict | None]
        """
        url = f"https://api.github.com/repos/{REPO}/releases/latest"

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            tag = data['tag_name'].lstrip('v')
            return tag, data
        
        except Exception as e:
            return None, None

    def check_update(self) -> bool:
        """_summary_

        :return: _description_
        :rtype: bool
        """
        self.latest_ver, self.release_data = self.fetch_release_info()

        if not self.latest_ver:
            return False
        
        return version.parse(self.latest_ver) > version.parse(self.local_ver)

    def _download_with_progress(self, url: str, dest: Path) -> None:
        """_summary_

        :param url: _description_
        :type url: str
        :param dest: _description_
        :type dest: Path
        """

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TextColumn("•"),
                TransferSpeedColumn(),
                TextColumn("•"),
                TimeRemainingColumn(),
                console=console,
                transient=False,
            ) as progress:
                task = progress.add_task(
                    f"下载 {dest.name}",
                    total=total_size if total_size > 0 else None,
                )

                with open(dest, 'wb') as f:

                    for chunk in r.iter_content(chunk_size=8192):

                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

                if total_size == 0:
                    progress.update(task, completed=True)

    def _apply_patch(self, patch_url: str) -> None:
        """_summary_

        :param patch_url: _description_
        :type patch_url: str
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "patch.zip"
            console.print(f"[bold cyan]⚡ 增量更新[/bold cyan] {self.local_ver} → {self.latest_ver}")
            self._download_with_progress(patch_url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zf:

                if ".deleted_files.txt" in zf.namelist():
                    deleted = zf.read(".deleted_files.txt").decode().splitlines()

                    for rel_path in deleted:
                        target = GAME_DIR / rel_path

                        if target.exists():

                            if target.is_dir():
                                shutil.rmtree(target, ignore_errors=True)

                            else:
                                target.unlink()

                            console.print(f"  [dim]删除: {rel_path}[/dim]")

                for member in zf.namelist():
                    
                    if member == ".deleted_files.txt":
                        continue

                    target = GAME_DIR / member
                    target.parent.mkdir(parents=True, exist_ok=True)

                    with zf.open(member) as src, open(target, 'wb') as dst:
                        dst.write(src.read())

                    console.print(f"  [green]更新: {member}[/green]")

    def _download_full_source(self, release_data: dict) -> None:
        """_summary_

        :param release_data: _description_
        :type release_data: dict
        """
        zip_url = None

        for asset in release_data.get('assets', []):

            if asset['name'].endswith('.zip'):
                zip_url = asset['browser_download_url']
                break

        if not zip_url:
            zip_url = f"https://github.com/{REPO}/archive/refs/tags/{release_data['tag_name']}.zip"

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "full.zip"
            console.print(f"[bold yellow]📦 全量更新[/bold yellow]")
            self._download_with_progress(zip_url, zip_path)
            extract_dir = Path(tmpdir) / "extract"

            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)

            extracted_root = next(extract_dir.glob('*/'))

            for item in GAME_DIR.iterdir():

                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)

                else:
                    item.unlink()

            for src_item in extracted_root.iterdir():
                dst = GAME_DIR / src_item.name

                if src_item.is_dir():
                    shutil.copytree(src_item, dst, dirs_exist_ok=True)

                else:
                    shutil.copy2(src_item, dst)

                console.print(f"  [green]复制: {src_item.name}[/green]")

    # ---------- 主更新流程 ----------
    def apply_update(self) -> None:
        """_summary_"""

        if not self.release_data or not self.latest_ver:
            return

        patch_asset = None

        for asset in self.release_data.get('assets', []):
            name = asset['name']

            if name.startswith(f"patch_{self.local_ver}_to_{self.latest_ver}"):
                patch_asset = asset
                break

        if patch_asset:

            try:
                self._apply_patch(patch_asset['browser_download_url'])

            except Exception as e:
                console.print(f"[yellow]警告[/yellow] 增量更新失败 ({e})，回退全量更新")
                self._download_full_source(self.release_data)

        else:
            console.print("[dim]未找到补丁，执行全量更新[/dim]")
            self._download_full_source(self.release_data)

        self._write_local_version(self.latest_ver)
        console.print(f"[bold green]✅ 更新完成，当前版本 {self.latest_ver}[/bold green]")

if __name__ == "__main__":
    updater = GameUpdater()

    if updater.check_update():
        updater.apply_update()

    index()