# ⚠️ SQLite on Render - Important Information

## Current Configuration

Your app is now configured to use **SQLite** instead of PostgreSQL.

## ⚠️ CRITICAL WARNING: Data Loss

**SQLite data on Render is NOT persistent!**

### When You WILL Lose Data:

1. ✅ **Every deployment** - New deploy = empty database
2. ✅ **Container restarts** - Platform restart = data gone
3. ✅ **Auto-scaling** - New instance = fresh database
4. ✅ **Platform maintenance** - Updates = data reset

**Bottom Line**: Assume all data is temporary and will be deleted frequently.

---

## 📊 Comparison: SQLite vs PostgreSQL

| Feature | SQLite (Current) | PostgreSQL |
|---------|------------------|------------|
| **Data Persistence** | ❌ Lost on deploy | ✅ Permanent |
| **Setup Complexity** | ✅ Simple | Medium |
| **Cost** | ✅ Free | ✅ Free tier available |
| **Production Ready** | ❌ No | ✅ Yes |
| **Performance** | Medium | ✅ Better |
| **Concurrent Users** | Limited | ✅ Unlimited |
| **Backup/Restore** | ❌ Not possible | ✅ Built-in |

---

## ✅ When SQLite is OK

Use SQLite for:
- 🧪 **Testing deployments** - Just trying Render
- 🎨 **UI/UX demos** - Showing the interface
- 🏃 **Quick prototypes** - Short-lived projects
- 📚 **Learning/tutorials** - Educational purposes
- 🔍 **Development** - Local testing

---

## ❌ When SQLite is NOT OK

Don't use SQLite for:
- 🏭 **Production apps** - Real users will lose data
- 💼 **Business applications** - Data loss = bad
- 👥 **Multi-user apps** - Concurrency issues
- 📊 **Data collection** - You'll lose the data
- 🚀 **Anything important** - Just don't

---

## 🎯 Recommended Solutions

### Option 1: PostgreSQL on Render (Best)

**Pros**:
- ✅ Persistent storage
- ✅ Free tier (0.1 GB, 90-day retention)
- ✅ Production-ready
- ✅ Easy setup

**How to Switch Back**:
```bash
# Restore PostgreSQL config
mv render-postgres.yaml.backup render.yaml

# Commit and deploy
git add render.yaml
git commit -m "Switch back to PostgreSQL"
git push
```

Render will automatically:
1. Create PostgreSQL database
2. Connect your app
3. Persist all data permanently

---

### Option 2: External Database Service

**Supabase (Recommended)**:
- Free PostgreSQL hosting
- 500 MB storage
- Unlimited API requests
- Auto backups

**Setup**:
1. Create account at https://supabase.com
2. Create new project
3. Get connection string
4. Add to Render env vars:
   ```
   DATABASE_URL=postgresql://[username]:[password]@[host]:5432/[database]
   ```

**Other Options**:
- **Neon** - Serverless PostgreSQL (generous free tier)
- **PlanetScale** - Serverless MySQL
- **MongoDB Atlas** - NoSQL database
- **CockroachDB** - Distributed SQL

---

### Option 3: Render Disks (SQLite + Persistence)

**For SQLite lovers who want persistence**:

Requires: Starter plan or higher ($7/month)

**Setup**:
1. Upgrade to Starter plan
2. Add disk mount in render.yaml:
   ```yaml
   disk:
     name: cv-builder-data
     mountPath: /data
     sizeGB: 1
   ```
3. Update DATABASE_URL:
   ```
   DATABASE_URL=sqlite:////data/cv_builder.db
   ```

**Cost**: $0.25/GB/month + $7/month Starter plan

---

## 🚀 Current Setup Works For

Your **current SQLite setup** is perfect for:

### Scenario 1: Quick Demo
```
1. Deploy to Render
2. Show UI/features to client
3. Client sees it works
4. Switch to PostgreSQL for production
```

### Scenario 2: Testing Platform
```
1. Test Render deployment process
2. Verify app runs correctly
3. Check SEO features work
4. Then add persistent database
```

### Scenario 3: Development
```
1. Use SQLite locally (run_local.py)
2. Test features quickly
3. Deploy to Render with PostgreSQL
```

---

## 📝 Modified Files

### ✅ requirements.txt
Removed:
```txt
psycopg[binary]==3.2.3
```

Now uses only SQLite (built-in with Python).

### ✅ render.yaml
Changed:
```yaml
# Before
DATABASE_URL: [from PostgreSQL service]

# After
DATABASE_URL: sqlite:////opt/render/project/src/cv_builder.db
```

Removed:
- PostgreSQL database service
- Redis service (uses in-memory)

### ✅ Backup Created
- `render-postgres.yaml.backup` - Your PostgreSQL config

---

## 🔄 How to Switch Back to PostgreSQL

### Quick Switch:

```bash
# 1. Restore PostgreSQL config
mv render-postgres.yaml.backup render.yaml

# 2. Update requirements.txt
# Add back: psycopg[binary]==3.2.3

# 3. Commit and push
git add .
git commit -m "Restore PostgreSQL configuration"
git push
```

### Manual Setup:

See [DEPLOYMENT.md](DEPLOYMENT.md) for full PostgreSQL setup guide.

---

## 💡 Pro Tips

### For Testing (Current SQLite Setup):
```bash
# 1. Deploy
git push

# 2. Test features
# - Create CV
# - Print to PDF
# - Test SEO

# 3. Note: Data resets on each deploy!
```

### For Production (Switch to PostgreSQL):
```bash
# Recommended approach
mv render-postgres.yaml.backup render.yaml
git add .
git commit -m "Use PostgreSQL for production"
git push
```

---

## 🆘 FAQ

**Q: Can I use SQLite in production?**
A: Not on Render free tier - data is lost on every deploy.

**Q: How do I keep SQLite data?**
A: Upgrade to Starter plan + use Render Disks ($7+/mo).

**Q: Is PostgreSQL free?**
A: Yes! Render offers free PostgreSQL tier (0.1 GB).

**Q: What about my local development?**
A: Keep using SQLite locally (run_local.py) - it's perfect for that!

**Q: Can I backup SQLite data?**
A: Not on Render free tier - filesystem is ephemeral.

**Q: When will I lose data?**
A: On every deployment, restart, or platform maintenance.

---

## ✅ Recommendation

**For your CV Builder app**:

### Development (Local):
```bash
python run_local.py
# Uses SQLite - perfect! ✅
```

### Production (Render):
```bash
# Use PostgreSQL - switch back:
mv render-postgres.yaml.backup render.yaml
git push
# Data persists forever ✅
```

**Best of both worlds**:
- 🏠 Local: Fast SQLite
- ☁️ Cloud: Reliable PostgreSQL

---

## 📚 More Info

- [Render Disks Docs](https://render.com/docs/disks)
- [PostgreSQL Setup](DEPLOYMENT.md#postgresql)
- [Supabase Setup](https://supabase.com/docs)
- [SQLite on Render](https://render.com/docs/sqlite)

---

**Current Status**: ⚠️ SQLite (data not persistent)
**Recommended**: Switch to PostgreSQL for production
**To Switch**: `mv render-postgres.yaml.backup render.yaml && git push`
