# 🔄 Code Sync Guide - Morning Scanner

## 📋 **HOW CODE SYNCING WORKS**

### **🔄 The Workflow:**

```
Your Computer (Local)     ←→     GitHub (Cloud)
     ↓                              ↓
  Edit Code                    Runs at 08:40
     ↓                              ↓
  Save Files                   Uses Latest Code
     ↓                              ↓
  Run Sync Script            Sends Email Report
     ↓                              ↓
  Code Pushed to GitHub      You Get Daily Email
```

### **⏰ Timing:**
- **Local Changes**: Made anytime on your computer
- **GitHub Sync**: When you run the sync script
- **Automatic Runs**: Every morning at 08:40 Stockholm time
- **Email Reports**: Based on the latest code on GitHub

---

## 🚀 **QUICK SYNC (Recommended)**

### **Use the Sync Script:**
```bash
python3 sync_to_github.py
```

**What it does:**
1. ✅ Checks what files you've changed
2. ✅ Adds all changes to git
3. ✅ Commits with your message
4. ✅ Pushes to GitHub
5. ✅ Confirms success

**Example:**
```bash
$ python3 sync_to_github.py
🚀 Morning Scanner - Sync to GitHub
==================================================
📊 Checking Git status...
📝 Changes detected:
   M sources/extras.py
   M main.py
   A .github/workflows/daily_scan.yml

🔄 Syncing changes to GitHub...
🔄 Adding changes to git...
✅ Adding changes to git successful
💬 Enter commit message (or press Enter for default): Added new RSS feeds

🔄 Committing changes...
✅ Committing changes successful
🔄 Pushing to GitHub...
✅ Pushing to GitHub successful

🎉 SUCCESS! Your code is now synced to GitHub.
📅 The next automatic run at 08:40 will use your updated code!
```

---

## 📚 **MANUAL SYNC (Alternative)**

### **Step-by-Step Commands:**

#### **1. Check What Changed:**
```bash
git status
```

#### **2. Add Changes:**
```bash
git add .
```

#### **3. Commit Changes:**
```bash
git commit -m "Your description here"
```

#### **4. Push to GitHub:**
```bash
git push origin main
```

---

## 🎯 **WHEN TO SYNC**

### **✅ Sync After Making Changes:**
- Adding new RSS feeds
- Fixing bugs
- Improving analysis
- Adding new features
- Updating configuration

### **⏰ Sync Timing:**
- **Immediate**: After important changes
- **Daily**: Before going to bed
- **Weekly**: Regular maintenance
- **Before 08:40**: To ensure latest code runs

---

## 🔍 **VERIFYING SYNC**

### **Check GitHub:**
1. Go to your repository on GitHub
2. Look at the latest commit
3. Check the Actions tab for recent runs

### **Check Local Status:**
```bash
git status
git log --oneline -5
```

---

## 🚨 **COMMON SCENARIOS**

### **Scenario 1: You Made Changes**
```bash
# Edit some files...
# Save changes...

# Sync to GitHub
python3 sync_to_github.py

# Next 08:40 run will use your changes!
```

### **Scenario 2: No Changes Made**
```bash
python3 sync_to_github.py
# Output: "No changes to sync. Your code is already up to date!"
```

### **Scenario 3: Sync Failed**
```bash
# Check what went wrong
git status
git remote -v

# Try manual sync
git add .
git commit -m "Fix sync issue"
git push origin main
```

---

## 📱 **MONITORING AUTOMATIC RUNS**

### **GitHub Actions Tab:**
1. Go to your repository
2. Click **Actions** tab
3. See all scheduled and manual runs
4. Check logs and results
5. Download generated reports

### **Daily Check:**
- **Morning**: Check email for daily report
- **Afternoon**: Check Actions tab for run status
- **Evening**: Sync any local changes

---

## 💡 **BEST PRACTICES**

### **✅ Do:**
- Sync after making changes
- Use descriptive commit messages
- Test locally before syncing
- Monitor GitHub Actions runs
- Keep local and GitHub in sync

### **❌ Don't:**
- Forget to sync important changes
- Push broken code
- Ignore sync errors
- Let local and GitHub get out of sync

---

## 🎉 **SUMMARY**

### **The Process:**
1. **Edit Code** → Make changes on your computer
2. **Run Sync** → `python3 sync_to_github.py`
3. **Code Pushed** → Changes go to GitHub
4. **Automatic Run** → Next 08:40 uses updated code
5. **Email Report** → You get results from latest version

### **Key Points:**
- **Local changes don't auto-sync** - you must push them
- **Sync script makes it easy** - just one command
- **GitHub Actions always uses latest code** - after you sync
- **Timing matters** - sync before 08:40 for same-day updates

### **Your Workflow:**
```
Edit Code → Save → Run Sync → Push to GitHub → Automatic 08:40 Run → Email Report
```

**Your Morning Scanner will always use the latest code after you sync!** 🚀📈 