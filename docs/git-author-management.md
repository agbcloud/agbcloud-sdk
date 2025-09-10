# Git Author Information Management

This document provides comprehensive methods for managing and hiding original commit author information when applying patches from external repositories.

## Table of Contents

- [Overview](#overview)
- [Methods](#methods)
- [Real Example: Our Recent Usage](#real-example-our-recent-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

When applying patches from other repositories, Git preserves the original author information. This document outlines various methods to hide or modify this information to maintain consistent authorship in your repository.

## Methods

### Method 1: Apply and Reset Author (Single Commit)

**Use case**: When applying a single patch file

```bash
# Method 1a: During patch application
git am --reset-author < patch-file.patch

# Method 1b: After commit is already made
git commit --amend --reset-author --no-edit
```

### Method 2: Specify Custom Author

**Use case**: When you want to set a specific author

```bash
# During patch application
git am --author="AgbAccount <m18116222400@163.com>" < patch-file.patch

# Modify existing commit
git commit --amend --author="AgbAccount <m18116222400@163.com>" --no-edit
```

### Method 3: Apply Without Commit History

**Use case**: When you want to apply changes without preserving any commit history

```bash
# Apply patch without creating commit
git apply patch-file.patch

# Stage and commit with your own information
git add .
git commit -m "Applied changes from external source"
```

### Method 4: Interactive Rebase (Multiple Commits)

**Use case**: When you need to modify several recent commits

```bash
# Start interactive rebase for last 5 commits
git rebase -i HEAD~5

# In the editor, change 'pick' to 'edit' for commits you want to modify
# Then for each commit:
git commit --amend --reset-author --no-edit
git rebase --continue
```

### Method 5: Filter Branch (History Rewriting)

**Use case**: When you need to modify specific commits in history

```bash
# Modify specific commit by SHA
git filter-branch --env-filter '
if [ $GIT_COMMIT = COMMIT_SHA_HERE ]
then
    export GIT_AUTHOR_NAME="AgbAccount"
    export GIT_AUTHOR_EMAIL="m18116222400@163.com"
    export GIT_COMMITTER_NAME="AgbAccount"
    export GIT_COMMITTER_EMAIL="m18116222400@163.com"
fi
' --tag-name-filter cat -- --branches --tags

# Clean up after filter-branch
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now
```

### Method 6: Batch Processing Script

**Use case**: When you frequently need to process patches

Create a script `process_patch.sh`:

```bash
#!/bin/bash
# Usage: ./process_patch.sh patch-file.patch "commit message"

patch_file=$1
commit_msg=${2:-"Applied changes from external source"}

git apply "$patch_file"
git add .
git commit --author="AgbAccount <m18116222400@163.com>" -m "$commit_msg"
```

Make it executable:
```bash
chmod +x process_patch.sh
```

## Real Example: Our Recent Usage

Here's the exact scenario we encountered and how we resolved it:

### Problem
We had a commit with author `yuebing.yb <yuebing.yb@alibaba-inc.com>` that needed to be changed to `AgbAccount <m18116222400@163.com>`.

### Solution Steps

1. **Identify the problematic commit:**
   ```bash
   git log --pretty=format:"%h - %an <%ae> - %s" -10
   ```

2. **Use filter-branch to modify the specific commit:**
   ```bash
   git filter-branch --env-filter '
   if [ $GIT_COMMIT = 78f924e5b29c6605eddeaa8ca552c6156d6da219 ]
   then
       export GIT_AUTHOR_NAME="AgbAccount"
       export GIT_AUTHOR_EMAIL="m18116222400@163.com"
       export GIT_COMMITTER_NAME="AgbAccount"
       export GIT_COMMITTER_EMAIL="m18116222400@163.com"
   fi
   ' --tag-name-filter cat -- --branches --tags
   ```

3. **Clean up:**
   ```bash
   rm -rf .git/refs/original/
   git reflog expire --expire=now --all
   git gc --prune=now
   ```

4. **Verify the result:**
   ```bash
   git log --pretty=format:"%h - %an <%ae> - %s" -5
   ```

### Result
All commits now show consistent author information: `AgbAccount <m18116222400@163.com>`

## Best Practices

### Before Starting
1. **Always backup your repository:**
   ```bash
   git clone your-repo your-repo-backup
   ```

2. **Set correct git configuration:**
   ```bash
   git config user.name "AgbAccount"
   git config user.email "m18116222400@163.com"
   ```

### Choosing the Right Method

| Scenario | Recommended Method | Reason |
|----------|-------------------|---------|
| Single new patch | Method 3 (`git apply`) | Clean, no history preservation |
| Recent commits (1-5) | Method 4 (Interactive rebase) | Safe, targeted changes |
| Specific old commits | Method 5 (Filter branch) | Precise control |
| Frequent patch processing | Method 6 (Script) | Automation |

### After History Rewriting

1. **Force push with lease (safer than --force):**
   ```bash
   git push --force-with-lease origin branch-name
   ```

2. **Inform team members** if this is a shared repository

3. **Update tags if affected:**
   ```bash
   git push --force-with-lease --tags
   ```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Cannot force update the current branch"
```bash
# Solution: Switch to different branch first
git checkout -b temp-branch
git branch -D problematic-branch
git checkout -b problematic-branch
```

#### Issue 2: Remote rejects force push
```bash
# Use force-with-lease for safety
git push --force-with-lease origin branch-name

# If still rejected, ensure you have latest remote state
git fetch origin
git push --force-with-lease origin branch-name
```

#### Issue 3: Tags not updating after filter-branch
```bash
# Manually update tags
git tag -d tag-name
git tag -a tag-name commit-sha -m "Updated tag message"
git push --force-with-lease --tags
```

#### Issue 4: Backup refs still exist
```bash
# Clean up more thoroughly
rm -rf .git/refs/original/
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Safety Checklist

Before running history-rewriting commands:

- [ ] Repository is backed up
- [ ] You're on the correct branch
- [ ] Team members are notified (if shared repo)
- [ ] You understand the implications of rewriting history
- [ ] You have the correct commit SHAs identified

## Notes

- **History rewriting is permanent** - always backup first
- **Shared repositories** require team coordination
- **Tags may need manual updating** after filter-branch
- **CI/CD pipelines** might be affected by changed commit SHAs
- **Use `--force-with-lease`** instead of `--force` for safer pushes

## Quick Reference Commands

```bash
# Check current authors
git log --pretty=format:"%h - %an <%ae> - %s" -10

# Set git config
git config user.name "AgbAccount"
git config user.email "m18116222400@163.com"

# Apply patch without history
git apply patch.patch && git add . && git commit -m "message"

# Amend last commit author
git commit --amend --reset-author --no-edit

# Clean up after filter-branch
rm -rf .git/refs/original/ && git reflog expire --expire=now --all && git gc --prune=now
```

## For Claude Code Reference

This document is saved at `docs/git-author-management.md` in the project root. Key operations include:

1. **Standard author unification workflow:**
   - Identify problematic commits: `git log --pretty=format:"%h - %an <%ae> - %s" -10`
   - Use filter-branch for specific commits: See Method 5 above
   - Clean up: `rm -rf .git/refs/original/ && git reflog expire --expire=now --all && git gc --prune=now`

2. **Project-specific settings:**
   - Author: `AgbAccount <m18116222400@163.com>`
   - Always backup before history rewriting
   - Use `--force-with-lease` for safer pushes