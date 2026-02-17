# 🚀 CV Builder - Quick Setup Guide

Complete setup instructions to get your CV Builder running locally in under 10 minutes!

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Docker** and **Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- ✅ **Google OAuth credentials** ([Setup instructions below](#google-oauth-setup))

---

## Step 1: Google OAuth Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/apis/credentials

2. **Create a New Project** (or select existing)
   - Click "Select a project" → "New Project"
   - Name it "CV Builder" → Create

3. **Configure OAuth Consent Screen**
   - Navigate to "APIs & Services" → "OAuth consent screen"
   - Select "External" → Create
   - Fill in:
     - **App name**: CV Builder
     - **User support email**: Your email
     - **Developer contact**: Your email
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add test users (your Gmail address)
   - Click "Save and Continue" → "Back to Dashboard"

4. **Create OAuth 2.0 Client ID**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: **Web application**
   - Name: **CV Builder Web Client**
   - Authorized redirect URIs:
     - `http://localhost:5000/auth/callback` (for local dev)
   - Click "Create"
   - **IMPORTANT**: Copy your **Client ID** and **Client Secret** — you'll need these next!

---

## Step 2: Clone & Configure

```bash
# Clone the repository
cd C:\Users\Viraj\Documents\CV_buider\CV_Builder

# Copy environment template
cp .env.example .env
```

**Edit `.env` file** and add your Google OAuth credentials:

```env
# Google OAuth (REQUIRED)
GOOGLE_CLIENT_ID=your-actual-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret-here

# Leave these as-is for local development
OAUTHLIB_INSECURE_TRANSPORT=1  # Allows HTTP for local dev
DATABASE_URL=postgresql://cvbuilder:devpassword@db:5432/cvbuilder
REDIS_URL=redis://redis:6379/0
```

---

## Step 3: Start the Application

```bash
# Start all services (Flask + PostgreSQL + Redis)
docker-compose up --build
```

**First-time startup will**:
- Build the Docker images (~2-3 minutes)
- Create database tables automatically
- Seed CV templates
- Start the web server on **http://localhost:5000**

---

## Step 4: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

1. Click **"Sign in with Google"**
2. Select your Google account
3. Grant permissions
4. You'll be redirected to the dashboard!

---

## 🎉 You're Ready!

You can now:
- ✅ Create CVs from the dashboard
- ✅ Edit CV content in the split-pane builder
- ✅ See live preview as you type
- ✅ Download professional PDFs

---

## Common Commands

```bash
# View logs
docker-compose logs -f web

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Run database migrations
docker-compose exec web flask db upgrade

# Access Flask shell
docker-compose exec web flask shell

# Run tests (after installing dev dependencies)
docker-compose exec web pip install -r requirements-dev.txt
docker-compose exec web pytest tests/ -v
```

---

## Troubleshooting

### Issue: "Authentication failed"
**Solution**:
1. Check that your Google OAuth credentials in `.env` are correct
2. Ensure redirect URI in Google Console matches exactly: `http://localhost:5000/auth/callback`
3. Verify your Google account is added as a test user

### Issue: "Database connection failed"
**Solution**:
```bash
# Wait for PostgreSQL to fully start (takes ~10 seconds on first run)
docker-compose logs db

# Restart the web service
docker-compose restart web
```

### Issue: "Port 5000 already in use"
**Solution**:
```bash
# Option 1: Stop the conflicting service
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Option 2: Change the port in docker-compose.yml
# Edit line: "5000:8000" to "8080:8000"
# Then access at http://localhost:8080
```

### Issue: "WeasyPrint PDF generation fails"
**Solution**:
- WeasyPrint dependencies are included in Dockerfile
- If issues persist, rebuild: `docker-compose build --no-cache web`

---

## Next Steps

### Phase 2 Enhancements (Optional)
- Add 3 professional templates (Elegant, Creative, Bold)
- Implement ATS scoring widget
- Add drag-and-drop section reordering
- Template color customization
- Version history

### Deploy to Production
See [README.md](README.md#deployment) for Render.com deployment instructions.

---

## Development Tips

### Hot Reload is Enabled
- Edit files in `app/` and changes appear automatically
- No need to restart Docker for code changes
- Refresh browser to see updates

### Database GUI (pgAdmin)
```bash
# Start pgAdmin
docker-compose --profile tools up -d pgadmin

# Access at http://localhost:5050
# Email: admin@cvbuilder.local
# Password: admin

# Connect to database:
# Host: db
# Port: 5432
# Database: cvbuilder
# Username: cvbuilder
# Password: devpassword
```

### VS Code Setup
Recommended extensions:
- Python
- Docker
- Jinja (Better Jinja)
- Prettier (HTML/CSS/JS formatting)

---

## Support

- 📖 Full documentation: [README.md](README.md)
- 🐛 Report issues: [GitHub Issues](https://github.com/your-username/cv-builder/issues)
- 📧 Email: support@cvbuilder.com (TODO: Update)

---

**Happy Building! 🎨**
