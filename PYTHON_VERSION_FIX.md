# Python Version Compatibility Fix

## Problem

Render.com is using Python 3.14 which has compatibility issues with `psycopg2-binary`:

```
ImportError: undefined symbol: _PyInterpreterState_Get
```

## ✅ Solution 1: Pin Python Version (Recommended)

### Step 1: Create runtime.txt

File: `runtime.txt`
```
python-3.12.7
```

This tells Render to use Python 3.12.7 instead of the latest version.

### Step 2: Commit and Push

```bash
git add runtime.txt
git commit -m "Pin Python version to 3.12.7"
git push
```

Render will automatically redeploy with Python 3.12.7.

---

## ✅ Solution 2: Use psycopg3 (Alternative)

If you want to use the latest Python, switch to psycopg3:

### Update requirements.txt

Replace:
```txt
psycopg2-binary==2.9.9
```

With:
```txt
psycopg[binary]==3.2.3
```

### Update database connection code

No code changes needed! psycopg3 is compatible with SQLAlchemy's psycopg2 dialect.

---

## ✅ Solution 3: Build from Source

Add to render.yaml buildCommand:

```yaml
buildCommand: |
  apt-get update && apt-get install -y libpq-dev gcc
  pip install --upgrade pip setuptools wheel
  pip install psycopg2 --no-binary psycopg2
  pip install -r requirements.txt
```

This compiles psycopg2 from source instead of using pre-built binary.

---

## 🎯 Recommended Approach

**Use Solution 1** (runtime.txt with Python 3.12.7)

**Why?**
- ✅ Simplest fix
- ✅ No code changes needed
- ✅ Python 3.12 is stable and tested
- ✅ Works with all existing dependencies
- ✅ No build time increase

**How to Apply:**

1. Create `runtime.txt`:
   ```bash
   echo "python-3.12.7" > runtime.txt
   ```

2. Commit:
   ```bash
   git add runtime.txt
   git commit -m "Fix: Pin Python to 3.12.7 for psycopg2 compatibility"
   git push
   ```

3. Done! Render auto-deploys with correct Python version.

---

## 📊 Version Compatibility Matrix

| Python Version | psycopg2-binary | psycopg3 | Status |
|---------------|-----------------|----------|---------|
| 3.12.x | ✅ Works | ✅ Works | **Recommended** |
| 3.13.x | ⚠️ May fail | ✅ Works | Use psycopg3 |
| 3.14.x | ❌ Fails | ✅ Works | Use psycopg3 or pin to 3.12 |

---

## 🔍 How to Verify

After deploying with the fix:

1. Check Render logs for:
   ```
   ✓ Database initialized
   ```

2. Visit your app URL - should load without errors

3. Test database connection:
   - Sign in with Google
   - Create a test CV
   - Verify it saves

---

## 🆘 If Still Not Working

### Check Render Build Logs

Look for:
- Python version being used
- psycopg2 installation success
- Any import errors

### Alternative: Use SQLite for Testing

Temporarily switch to SQLite in render.yaml:

```yaml
envVars:
  - key: DATABASE_URL
    value: sqlite:///cv_builder.db
```

Then you can debug PostgreSQL issues separately.

---

## 📝 Files to Create/Update

### Create: runtime.txt
```
python-3.12.7
```

### Optional: requirements-render.txt
```txt
# ... (same as requirements.txt but with psycopg3)
psycopg[binary]==3.2.3  # Instead of psycopg2-binary
```

Then update render.yaml:
```yaml
buildCommand: |
  pip install --upgrade pip setuptools wheel
  pip install -r requirements-render.txt
```

---

## ✅ Final Checklist

- [ ] Created runtime.txt with `python-3.12.7`
- [ ] Committed and pushed to GitHub
- [ ] Render auto-deployed
- [ ] Checked build logs (no errors)
- [ ] Visited app URL (loads correctly)
- [ ] Tested database connection (can create CV)
- [ ] Removed any temporary workarounds

---

**Status**: Ready to deploy with Python 3.12.7! 🚀
