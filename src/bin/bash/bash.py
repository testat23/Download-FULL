import json
from pathlib import Path
from colorama import Fore, init
init()

green = Fore.GREEN
red = Fore.RED
cyan = Fore.CYAN
reset = Fore.RESET

def main_bash():
    login_file = Path("src/etc/login.json")
    
    username = "unknown"
    try:
        if login_file.exists():
            with open(login_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                username = data.get("username", "user")
    except Exception as e:
        print(f"Error reading login.json: {e}")
        
    while True:
        prompt = f"{green}{username}{red}@{cyan}kentOS{reset}~{red}${reset} "
        cmd = input(prompt)
        
        if cmd.strip() == "exit":
            break
        elif cmd.strip() == "clear":
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
        elif cmd.strip() == "":
            continue
        else:
            print(f"Command not found: {cmd}")
