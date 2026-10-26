import zipfile
import requests
import io
import difflib
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, DownloadColumn, TransferSpeedColumn

console = Console()

def main_upgrade():
    spool = Path("src/var/spool/updates")
    console.print(f"[bold]:: Searching for updates in {spool}...[/]")
    
    updates = list(spool.glob("update_*.json"))
    
    if not updates:
        console.print("[bold green]System is up to date.[/]")
        return
        
    console.print(f"[bold cyan]:: Found {len(updates)} update(s).[/]")

    for upd in updates:
        try:
            data = json.loads(upd.read_text())
            version = data["version"]
            url = data["url"]
            
            console.print(f"[bold]:: Downloading update {version}...[/]")
            
            r = requests.get(url, stream=True)
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            buffer = io.BytesIO()

            with Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(bar_width=30, style="#3584e4"),
                DownloadColumn(),
                TransferSpeedColumn(),
            ) as progress:
                task = progress.add_task(f"[bold #3584e4]Downloading...", total=total_size)
                for chunk in r.iter_content(chunk_size=8192):
                    buffer.write(chunk)
                    progress.update(task, advance=len(chunk))
            
            with zipfile.ZipFile(buffer) as z:
                prefix = None
                for name in z.namelist():
                    if "/src/" in name:
                        prefix = name.split("/src/")[0] + "/src/"
                        break
                
                if not prefix:
                    console.print("[bold red]:: Error: 'src/' not found in archive.[/]")
                    continue
                
                for file_info in z.infolist():
                    if not file_info.filename.startswith(prefix):
                        continue
                        
                    rel_path = file_info.filename[len(prefix):]
                    if not rel_path: continue
                        
                    out_file = Path("src") / rel_path

                    if rel_path.startswith(("var/", "etc/passwd.cfg")):
                        console.print(f"  [dim]Skipped: {rel_path}[/]")
                        continue
                        
                    if file_info.is_dir():
                        out_file.mkdir(parents=True, exist_ok=True)
                        continue
                        
                    new_content = z.read(file_info).decode('utf-8', errors='replace')
                    
                    if not out_file.exists():
                        out_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(out_file, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        console.print(f"  [bold green]Created: {rel_path}[/]")
                        continue
                    
                    old_content = out_file.read_text(encoding='utf-8', errors='replace')
                    
                    if old_content == new_content:
                        console.print(f"  [dim]Unchanged: {rel_path}[/]")
                        continue 
                    
                    console.print(f"  [bold yellow]Merging: {rel_path}[/]")
                    
                    old_lines = old_content.splitlines(keepends=True)
                    new_lines = new_content.splitlines(keepends=True)
                    
                    result_lines = list(old_lines)
                    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
                    
                    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
                        if tag == 'equal':
                            continue 
                        elif tag == 'insert':
                            result_lines[i1:i1] = new_lines[j1:j2]
                        elif tag == 'delete':
                            del result_lines[i1:i2]
                        elif tag == 'replace':
                            result_lines[i1:i2] = new_lines[j1:j2]
                            
                    merged = "".join(result_lines)
                    
                    backup_file = out_file.with_suffix(out_file.suffix + ".bak")
                    if backup_file.exists():
                        backup_file.unlink()
                    out_file.rename(backup_file)
                    with open(out_file, "w", encoding="utf-8") as f:
                        f.write(merged)

            state_file = Path("src/var/lib/pkg/last_update.cfg")
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(version)

            upd.unlink()
            console.print(f"[bold green]:: System updated to version {version}[/]")
            
        except Exception as e:
            console.print(f"[bold red]:: Error: {e}[/]")