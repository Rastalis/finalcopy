import subprocess
import time

def run_git_command(command):
    """Executes a Git command and prints output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

print("🔄 Checking for updates...")

# Add all changes
run_git_command("git add .")

# Commit with timestamp
commit_message = f"Auto-update: {time.strftime('%Y-%m-%d %H:%M:%S')}"
run_git_command(f'git commit -m "{commit_message}"')

# Push changes
run_git_command("git push origin main")

print("✅ Changes pushed successfully!")
