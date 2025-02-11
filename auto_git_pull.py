import subprocess
import time

REPO_PATH = "C:\\Users\\brian\\finalcopy"  # Change this if needed
BRANCH = "main"  # Change if using a different branch
CHECK_INTERVAL = 60  # Check every 60 seconds

def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
        return result.stdout.strip()
    except Exception as e:
        print(f"⚠️ Error running command: {command}\n{e}")
        return None

def check_for_updates():
    """Checks for updates and pulls if necessary."""
    print("🔄 Checking for updates...")
    
    run_command("git fetch origin")  # Fetch latest updates

    # Check if local branch is behind the remote branch
    status = run_command(f"git rev-list HEAD..origin/{BRANCH} --count")
    
    if status and int(status) > 0:
        print(f"⬇️ {status} updates found! Pulling changes...")
        run_command(f"git pull origin {BRANCH}")
        print("✅ Updated successfully!")
    else:
        print("✅ No updates found.")

# Run continuously
while True:
    check_for_updates()
    time.sleep(CHECK_INTERVAL)  # Wait before checking again
