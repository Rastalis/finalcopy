import subprocess
import time

REPO_DIR = "C:/Users/brian/finalcopy"  # Change this to your repo path
PULL_INTERVAL = 30  # Check for updates every 30 seconds

while True:
    print("🔄 Checking for updates...")
    subprocess.run(["git", "-C", REPO_DIR, "pull"], check=False)
    time.sleep(PULL_INTERVAL)
