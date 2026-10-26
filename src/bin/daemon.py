import time
import requests
import json
from pathlib import Path

SPOOL_DIR = Path("src/var/spool/updates")
CACHE_DIR = Path("src/var/cache/pkg")
STATE_FILE = Path("src/var/lib/pkg/last_update.cfg")

def check_updates():
    url = "https://api.github.com/repos/testat23/Download-FULL/commits/main"
    try:
        r = requests.get(url, timeout=5)
        last_commit = r.json().get("sha", "")[:7]
    except Exception:
        return

    current_commit = ""
    if STATE_FILE.exists():
        current_commit = STATE_FILE.read_text().strip()

    if last_commit and last_commit != current_commit:
        
        SPOOL_DIR.mkdir(parents=True, exist_ok=True)
        update_file = SPOOL_DIR / f"update_{last_commit}.json"
        update_file.write_text(json.dumps({
            "version": last_commit,
            "url": "https://github.com/testat23/Download-FULL/archive/refs/heads/main.zip"
        }))

if __name__ == "__main__":
    while True:
        check_updates()
        time.sleep(300) 