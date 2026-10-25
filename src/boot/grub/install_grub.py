import os
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
import readchar
import io
import zipfile
import requests
from pathlib import Path
import readchar
import io
import zipfile
import requests

console = Console()

LOGO = """
[bold #3584e4]    _  __         _    ___  ____  [/]
[bold #3584e4]    | |/ /___ _ __| |_ / _ \/ ___| [/]
[bold #3584e4]    | ' // _ \ '_ \ __ | | | \___ \ [/]
[bold #3584e4]    | . \  __/ | | |_| | |_| |___) |[/]
[bold #3584e4]    |_|\_\___|_| |_|\__|\___/|____/ [/]
[dim #9a9996]         GNOME GRUB • kentOS-V0.1       [/]
"""

MENU_ITEMS = [
    "Download kentOS           ",
    "Reboot            ",
    "Shutdown    "
]

GITHUB_URL = "https://github.com/testat23/kentOS/tree/main/src" # заменить!!!

def download_and_extract(github_url):
    parts = github_url.strip('/').split('/')
    owner, repo, branch = parts[3], parts[4], parts[6]
    folder_name = parts[-1]
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    
    try:
        response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        buffer = io.BytesIO()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="#3584e4", complete_style="#3584e4"),
            DownloadColumn(),
            TransferSpeedColumn(),
        ) as progress:
            task = progress.add_task("[bold #3584e4]Downloading...", total=total_size)
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    buffer.write(chunk)
                    progress.update(task, advance=len(chunk))
        
        buffer.seek(0)
        console.print("[bold green]:: Download complete! ::[/]")
        time.sleep(0.5)

        target_dir = Path(folder_name)
        target_dir.mkdir(parents=True, exist_ok=True)

        from src.boot.grub.grub import main_grub
        main_grub()

        with zipfile.ZipFile(buffer) as z:
            prefix = None
            for name in z.namelist():
                if f"/{folder_name}/" in name:
                    prefix = name.split(f"/{folder_name}/")[0] + f"/{folder_name}/"
                    break
            
            if prefix:
                for file_info in z.infolist():
                    if file_info.filename.startswith(prefix):
                        rel_path = file_info.filename[len(prefix):]
                        if not rel_path:
                            continue
                        out_file = target_dir / rel_path
                        if file_info.is_dir():
                            out_file.mkdir(parents=True, exist_ok=True)
                        else:
                            out_file.parent.mkdir(parents=True, exist_ok=True)
                            with z.open(file_info) as source, open(out_file, "wb") as target:
                                target.write(source.read())
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/]")
        time.sleep(2)
        return False

def draw_menu(selected_index):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    console.print(Align.center(Text.from_markup(LOGO)))
    console.print("\n")
    
    menu_text = Text()
    for i, item in enumerate(MENU_ITEMS):
        if i == selected_index:
            menu_text.append(f"  >  {item}  \n", style="bold white on #3584e4")
        else:
            menu_text.append(f"     {item}  \n", style="dim white")
            
    panel = Panel(
        Align.center(menu_text),
        title="[bold #3584e4]kentOS Boot Menu[/]",
        subtitle="[dim]↑/↓ choice • Enter load[/]",
        border_style="#3584e4",
        padding=(1, 4),
        style="on #242424"
    )
    
    console.print(Align.center(panel))

def main_instG():
    selected = 0
    while True:
        draw_menu(selected)
        
        key = readchar.readkey()
        
        if key == readchar.key.UP:
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key == readchar.key.ENTER:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            if selected == 0:
                console.print("[bold #3584e4]Download kentOS...")
                success = download_and_extract(GITHUB_URL)

                return 0 
            elif selected == 1:
                console.print("[bold #3584e4]Reboot...")
                time.sleep(1)
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print("[bold #3584e4]Load...")
                time.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            elif selected == 2:
                console.print("[bold #3584e4]Shutdown...")
                time.sleep(0.42)
                os.system('cls' if os.name == 'nt' else 'clear')
                sys.exit(0)