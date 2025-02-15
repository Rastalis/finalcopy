import subprocess
import os

REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # Get repo directory

def run_command(command, cwd=REPO_DIR):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"⚠️ Error: {result.stderr.strip()}")
    return result

def sync_repo():
    """Pull latest changes, commit updates, and push."""
    print("🔄 Pulling latest changes from GitHub...")
    run_command("git pull origin main")

    print("📝 Staging changes...")
    run_command("git add .")

    print("📌 Committing changes...")
    run_command('git commit -m "Auto-update from ChatGPT" || echo "No changes to commit"')

    print("🚀 Pushing updates to GitHub...")
    run_command("git push origin main")

if __name__ == "__main__":
    sync_repo()
