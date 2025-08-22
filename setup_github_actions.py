#!/usr/bin/env python3
"""
GitHub Actions Setup Helper for Morning Scanner
This script helps you set up automatic daily runs at 08:40
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_status():
    """Check if this is a git repository and has a remote."""
    try:
        # Check if git is initialized
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Not a git repository"
        
        # Check if remote exists
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'origin' not in result.stdout:
            return False, "No remote origin configured"
        
        return True, "Git repository ready"
        
    except FileNotFoundError:
        return False, "Git not installed"
    except Exception as e:
        return False, f"Git error: {e}"

def setup_git_repository():
    """Set up git repository and push to GitHub."""
    print("🔧 Setting up Git repository...")
    
    try:
        # Initialize git if needed
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)
            print("✅ Git repository initialized")
        
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Files added to git")
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 'Morning Scanner setup with automation'], check=True)
        print("✅ Changes committed")
        
        # Set main branch
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        print("✅ Main branch set")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git setup failed: {e}")
        return False

def create_github_workflow():
    """Create the GitHub Actions workflow file."""
    workflow_dir = Path('.github/workflows')
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Daily Morning Scanner

on:
  schedule:
                    # Run at 08:30 Stockholm time (07:30 UTC in winter, 06:30 UTC in summer)
                - cron: '30 7 * * *'  # 07:30 UTC = 08:30 Stockholm (winter)
                - cron: '30 6 * * *'  # 06:30 UTC = 08:30 Stockholm (summer)
  
  # Allow manual triggering
  workflow_dispatch:

jobs:
  morning-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create environment file
      run: |
        echo "TZ=Europe/Stockholm" >> .env
        echo "RUN_HOUR=8" >> .env
        echo "RUN_MINUTE=30" >> .env
        echo "EMAIL_ENABLED=true" >> .env
        echo "TELEGRAM_ENABLED=false" >> .env
        echo "SMTP_HOST=smtp.gmail.com" >> .env
        echo "SMTP_PORT=587" >> .env
        echo "SMTP_USER=${{ secrets.SMTP_USER }}" >> .env
        echo "SMTP_PASS=${{ secrets.SMTP_PASS }}" >> .env
        echo "EMAIL_TO=${{ secrets.EMAIL_TO }}" >> .env
        echo "USE_LLM=false" >> .env
    
    - name: Run Morning Scanner
      run: |
        python main.py
      env:
        SMTP_USER: ${{ secrets.SMTP_USER }}
        SMTP_PASS: ${{ secrets.SMTP_PASS }}
        EMAIL_TO: ${{ secrets.EMAIL_TO }}
    
    - name: Upload logs
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: morning-scanner-logs
        path: |
          storage/errors.log
          storage/picks_log.csv
        retention-days: 7
'''
    
    workflow_file = workflow_dir / 'daily_scan.yml'
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    print(f"✅ GitHub Actions workflow created: {workflow_file}")
    return True

def show_setup_instructions():
    """Show the setup instructions."""
    print("\n" + "="*60)
    print("🚀 GITHUB ACTIONS SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 STEP 1: Push to GitHub")
    print("Run these commands:")
    print("  git add .")
    print("  git commit -m 'Add GitHub Actions automation'")
    print("  git push origin main")
    
    print("\n📋 STEP 2: Add GitHub Secrets")
    print("1. Go to your GitHub repository")
    print("2. Click Settings → Secrets and variables → Actions")
    print("3. Click 'New repository secret'")
    print("4. Add these 3 secrets:")
    
    print("\n   🔑 SMTP_USER")
    print("      Value: fabian.fallenius1@gmail.com")
    
    print("\n   🔑 SMTP_PASS") 
    print("      Value: wuiz ctun ojzs uryu")
    
    print("\n   🔑 EMAIL_TO")
    print("      Value: fabian.fallenius1@gmail.com")
    
    print("\n📋 STEP 3: Test the Workflow")
    print("1. Go to Actions tab in your repository")
    print("2. Click 'Daily Morning Scanner'")
    print("3. Click 'Run workflow' → 'Run workflow'")
    print("4. Watch it execute in real-time!")
    
    print("\n📋 STEP 4: Monitor Daily Runs")
    print("• Check Actions tab every morning")
    print("• View logs and results")
    print("• Download generated reports")
    
    print("\n🎯 RESULT:")
    print("Every morning at 08:40, you'll get an email with:")
    print("• 📰 Top Swedish financial news")
    print("• 📊 Relevance scores and analysis") 
    print("• 🔍 Positive stock opportunities")
    print("• 📈 Market insights and trends")
    print("• 💡 Trading recommendations")
    
    print("\n⏰ Your Morning Scanner will work 24/7, rain or shine!")
    print("="*60)

def main():
    """Main setup function."""
    print("🌅 Morning Scanner - GitHub Actions Setup")
    print("="*50)
    
    # Check git status
    git_ready, git_message = check_git_status()
    print(f"Git Status: {git_message}")
    
    if not git_ready:
        print("\n🔧 Setting up Git repository...")
        if not setup_git_repository():
            print("❌ Failed to setup Git repository")
            print("Please run: git init && git remote add origin YOUR_GITHUB_URL")
            return
    
    # Create GitHub Actions workflow
    print("\n🔧 Creating GitHub Actions workflow...")
    if create_github_workflow():
        print("✅ GitHub Actions workflow created successfully!")
    else:
        print("❌ Failed to create workflow file")
        return
    
    # Show setup instructions
    show_setup_instructions()
    
    print("\n🎉 Setup complete! Follow the instructions above to activate automation.")
    print("Your Morning Scanner will then run automatically every morning at 08:40!")

if __name__ == "__main__":
    main() 