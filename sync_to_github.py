#!/usr/bin/env python3
"""
Quick Sync to GitHub - Morning Scanner
This script helps you quickly sync local changes to GitHub
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a git command and show the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_git_status():
    """Check current git status."""
    print("📊 Checking Git status...")
    
    # Check if we're in a git repo
    if not os.path.exists('.git'):
        print("❌ Not in a git repository")
        return False
    
    # Check current status
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    
    if result.stdout.strip():
        print("📝 Changes detected:")
        for line in result.stdout.strip().split('\n'):
            if line:
                status = line[:2]
                filename = line[3:]
                print(f"   {status} {filename}")
        return True
    else:
        print("✅ No changes to commit")
        return False

def sync_to_github():
    """Sync local changes to GitHub."""
    print("🚀 Morning Scanner - Sync to GitHub")
    print("=" * 50)
    
    # Check git status
    has_changes = check_git_status()
    
    if not has_changes:
        print("\n🎯 No changes to sync. Your code is already up to date!")
        return
    
    print(f"\n🔄 Syncing {has_changes} changes to GitHub...")
    
    # Step 1: Add all changes
    if not run_command("git add .", "Adding changes to git"):
        return
    
    # Step 2: Commit changes
    commit_message = input("\n💬 Enter commit message (or press Enter for default): ").strip()
    if not commit_message:
        commit_message = "Update Morning Scanner code"
    
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        return
    
    # Step 3: Push to GitHub
    if not run_command("git push origin main", "Pushing to GitHub"):
        return
    
    print("\n🎉 SUCCESS! Your code is now synced to GitHub.")
    print("📅 The next automatic run at 08:40 will use your updated code!")
    
    # Show next steps
    print("\n📋 What happens next:")
    print("   • Your changes are now on GitHub")
    print("   • Next automatic run at 08:40 will use updated code")
    print("   • You can test manually in GitHub Actions tab")
    print("   • Monitor runs in the Actions tab")

def show_manual_commands():
    """Show manual git commands for reference."""
    print("\n📚 MANUAL GIT COMMANDS (if you prefer):")
    print("=" * 40)
    print("Check status:")
    print("  git status")
    print()
    print("Add changes:")
    print("  git add .")
    print()
    print("Commit changes:")
    print("  git commit -m 'Your message here'")
    print()
    print("Push to GitHub:")
    print("  git push origin main")
    print()
    print("Check remote:")
    print("  git remote -v")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        show_manual_commands()
        return
    
    try:
        sync_to_github()
    except KeyboardInterrupt:
        print("\n⏹️ Sync cancelled by user")
    except Exception as e:
        print(f"\n💥 Error during sync: {e}")
        print("\nTry running with --manual flag to see manual commands:")
        print("  python3 sync_to_github.py --manual")

if __name__ == "__main__":
    main() 