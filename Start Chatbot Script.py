import subprocess
import re
import json
import base64
import requests
import os

# === GITHUB SETTINGS ===
GITHUB_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxx"
OWNER = "iJUSTWANTTOUSE"
REPO = "Crisim"
FILE_PATH = "config.json"

# === KOBOLD SETTINGS ===
KOBOLD_EXE = r"xxxxxxxxxxxxxxxxxxxxxxxxxxx"
KOBOLD_SCENARIO = r"xxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Regex to detect tunnel URL
URL_PATTERN = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com")

def update_config(new_url):
    """Update config.json on GitHub via API"""
    print(f"[*] Updating GitHub config with URL: {new_url}")
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

    r = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if r.status_code != 200:
        print("[-] Error fetching config.json info:", r.text)
        return
    sha = r.json()["sha"]

    new_config = {"apiUrl": new_url}
    encoded_content = base64.b64encode(json.dumps(new_config, indent=2).encode()).decode()

    payload = {
        "message": f"Update API URL to {new_url}",
        "content": encoded_content,
        "sha": sha
    }

    r = requests.put(url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, data=json.dumps(payload))
    if r.status_code in [200, 201]:
        print(f"[+] config.json updated successfully to {new_url}")
    else:
        print("[-] Error updating config.json:", r.text)

def watch_kobold():
    """Start KoboldCPP and watch for Cloudflare URL"""
    cmd = [KOBOLD_EXE, KOBOLD_SCENARIO]
    print(f"[*] Starting KoboldCPP with: {cmd}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=os.path.dirname(KOBOLD_EXE)
    )

    updated = False
    try:
        for line in process.stdout:
            print(line, end="")
            if not updated and "Your remote Kobold API can be found at" in line:
                match = URL_PATTERN.search(line)
                if match:
                    url = match.group(0) + "/v1/completions"
                    print(f"\n[+] Detected KoboldCPP API URL: {url}")
                    update_config(url)
                    updated = True  # only update once
    except Exception as e:
        print(f"[-] Error reading KoboldCPP output: {e}")
    finally:
        print("[*] KoboldCPP process is still running. Press Ctrl+C to stop.")
        process.wait()

if __name__ == "__main__":
    watch_kobold()
