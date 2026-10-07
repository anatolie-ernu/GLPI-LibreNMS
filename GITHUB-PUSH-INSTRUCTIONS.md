# Push to GitHub - Instructions

## Status

✅ **Local Git Repository:** READY

```
Current branch: master
Commits: 1 (v1.0)
Files: 13
```

---

## ✅ Pre-Push Checklist

- [x] All files committed locally
- [x] Git initialized
- [x] Commit message comprehensive

---

## 📋 Steps to Push to GitHub

### 1. Create Repository on GitHub

**If you haven't already created the repo:**

1. Go to https://github.com/new
2. **Repository name:** `GLPI-LibreNMS`
3. **Description:** `GLPI + LibreNMS + Nginx Proxy Manager with Auto-Discovery (Docker)`
4. **Public** (for sharing)
5. **Initialize without README** (we already have one)
6. Click "Create repository"

**You'll see:**
```
Quick setup — if you've done this kind of thing before
or
…or push an existing repository from the command line
```

---

### 2. Add Remote & Push

Copy exact commands from GitHub (or use these):

```bash
# Navigate to repository folder
cd /path/to/GLPI-LibreNMS

# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/GLPI-LibreNMS.git

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

---

### 3. Alternative: SSH (If you have SSH key)

```bash
# Add SSH remote
git remote add origin git@github.com:USERNAME/GLPI-LibreNMS.git

# Push
git push -u origin main
```

---

### 4. Verify Push

After push, you should see:

```
Enumerating objects: 14, done.
Counting objects: 100% (14/14), done.
...
* [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## 🔐 Authentication

### HTTPS (Recommended for start)

When GitHub asks for password:
- **Username:** your GitHub username
- **Password:** Personal Access Token (NOT your password!)

**Get PAT:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Copy token and use as password

### SSH (Recommended for frequent pushes)

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your@email.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy to GitHub Settings → SSH Keys

# Test connection
ssh -T git@github.com
```

---

## 📋 Full Push Sequence

```bash
# 1. Navigate to outputs folder
cd /mnt/user-data/outputs

# 2. Check current status
git status
git log --oneline

# 3. Add remote (replace USERNAME)
git remote add origin https://github.com/USERNAME/GLPI-LibreNMS.git

# 4. Rename branch
git branch -M main

# 5. Push
git push -u origin main

# 6. Verify
git remote -v
```

---

## ✅ After Push

Once pushed to GitHub:

### Update Repository with Latest Changes

```bash
# When you update files locally
git add .
git commit -m "Update: description of changes"
git push

# Pull latest if working from multiple machines
git pull origin main
```

### Add More Scripts

```bash
# Add new file
echo "#!/bin/bash" > new-script.sh

# Commit
git add new-script.sh
git commit -m "Add: new-script.sh - description"
git push
```

---

## 🔧 Common Git Commands

```bash
# Check status
git status

# View commits
git log --oneline

# View remote
git remote -v

# Add all changes
git add .

# Commit
git commit -m "message"

# Push
git push

# Pull
git pull

# Create branch
git checkout -b feature-name

# Switch branch
git checkout branch-name

# Merge branch
git merge branch-name
```

---

## 📞 Troubleshooting

### "fatal: remote origin already exists"

```bash
# Remove old remote
git remote remove origin

# Add new one
git remote add origin https://github.com/USERNAME/GLPI-LibreNMS.git
```

### "Authentication failed"

```bash
# Use personal access token (not password)
# Or setup SSH key
```

### "Permission denied (publickey)"

```bash
# SSH key not configured
# Either:
# 1. Use HTTPS instead
# 2. Setup SSH key (see SSH section above)
```

---

## ✨ After You Push

Share with team:

```
GitHub: https://github.com/USERNAME/GLPI-LibreNMS
```

---

**Ready to push?** 🚀

Run the 5-step sequence above!

---

Generated: October 7, 2026  
By: Anatolie Ernu (ERNU.EU)
