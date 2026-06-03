# Git Commit Checklist

Before committing, make sure you've reviewed this checklist to avoid committing sensitive data.

## ✅ Safe to Commit

These files are safe and should be committed:

- [x] `.gitignore` - Protects sensitive files
- [x] `CLAUDE.md` - Codebase documentation
- [x] `IMPLEMENTATION_SUMMARY.md` - Educational overview
- [x] `QUICK_REFERENCE.md` - Quick reference guide
- [x] `README.md` - Project readme
- [x] `requirements.txt` - Python dependencies
- [x] `docker-compose.yml` - Docker configuration
- [x] All `.py` files in `task/` - Source code
- [x] `test_tools.py` - Test file
- [x] Images (`*.png`) - Documentation images

## ❌ NEVER Commit

These should NEVER be committed (already in .gitignore):

- [ ] `.env` files - Contains API keys and secrets
- [ ] `DIAL_API_KEY` - Your personal API key
- [ ] `__pycache__/` directories - Python cache
- [ ] `*.pyc` files - Compiled Python
- [ ] `.vscode/`, `.idea/` - IDE settings
- [ ] `data/` directory - Docker volumes with user data
- [ ] `.claude/` - Claude Code temporary files
- [ ] `*.log` files - Log files
- [ ] Virtual environments (`venv/`, `.venv/`)

## Before Every Commit

Run these commands:

```bash
# 1. Check what will be committed
git status

# 2. Review changes
git diff

# 3. Check for accidentally staged sensitive files
git diff --cached

# 4. Look for API keys or secrets in staged files
git diff --cached | grep -i "api_key\|secret\|password\|token"

# 5. If you see any secrets, DO NOT COMMIT!
#    Remove them with:
git reset HEAD <file>
```

## Safe Commit Commands

```bash
# Stage specific files (recommended)
git add task/app.py
git add task/client.py
git add .gitignore
git add *.md

# Or stage all (but check first!)
git add .

# Commit with descriptive message
git commit -m "Implement DIAL AI agent with tool calling

- Add web search tool using DIAL static_function
- Implement CRUD tools for user management
- Add recursive tool calling in DialClient
- Create comprehensive system prompt
- Add educational documentation

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"

# Push to remote
git push origin main
```

## If You Accidentally Commit Secrets

### Before Pushing

```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Remove the secret from files
# Edit files to remove secrets

# Commit again
git add .
git commit -m "Your message"
```

### After Pushing (More Serious)

```bash
# You must rewrite history - contact your team first!
# This will cause issues for anyone who pulled the bad commit

# Remove file from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (dangerous!)
git push origin --force --all

# Rotate the compromised API key immediately!
```

## Repository Best Practices

1. **Review before committing**: Always run `git diff` first
2. **Commit often**: Small, logical commits are easier to review
3. **Write clear messages**: Explain WHY, not just WHAT
4. **Never force push**: Unless absolutely necessary and team-coordinated
5. **Keep .gitignore updated**: Add new patterns as needed

## Testing Before Commit

```bash
# Run tests
python test_tools.py

# Check for syntax errors
python -m py_compile task/**/*.py

# Verify Docker setup
docker-compose config
```

## Additional Security

Consider these additional protections:

1. **Git hooks**: Use pre-commit hooks to scan for secrets
2. **Secret scanning tools**: 
   - `git-secrets` by AWS
   - `detect-secrets` by Yelp
   - `truffleHog` for history scanning
3. **Environment variables**: Always use `.env` files (never commit them)
4. **Configuration**: Use `config.local.json` for local overrides

## Current Repository Status

Check what's currently ready to commit:

```bash
git status --short

# M = Modified (existing file changed)
# A = Added (new file staged)
# ?? = Untracked (not in git yet)
# !! = Ignored (won't be committed)
```

---

**Remember**: Once something is pushed to a public repo, consider it public forever, even if you delete it later. Always be cautious!
