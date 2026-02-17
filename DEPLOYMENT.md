# CV Builder - Deployment Guide

Complete guide for deploying CV Builder to production on Render.com.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Docker Testing](#local-docker-testing)
3. [Production Deployment](#production-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [SEO Setup](#seo-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

1. **GitHub Account** - For code repository
2. **Render.com Account** - For hosting (free tier available)
3. **Google Cloud Console** - For OAuth authentication
4. **Google Analytics** (Optional) - For traffic tracking
5. **Google Search Console** (Optional) - For SEO monitoring

### Required Tools

- Git
- Docker & Docker Compose (for local testing)
- Text editor / IDE

---

## Local Docker Testing

Before deploying to production, test the Docker setup locally.

### Step 1: Set Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from .env.local.sqlite and modify
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX  # Optional
```

### Step 2: Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f web
```

### Step 3: Access the Application

Open browser to: http://localhost:8000

### Step 4: Test the Build

```bash
# Test production Docker build
docker build -t cvbuilder:test .

# Run the production image
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///cv_builder.db \
  -e REDIS_URL= \
  -e SECRET_KEY=test-key \
  cvbuilder:test
```

### Step 5: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Production Deployment

### Step 1: Prepare Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - CV Builder with SEO"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/cv-builder.git
git branch -M main
git push -u origin main
```

### Step 2: Connect to Render

1. Go to https://render.com
2. Sign up / Log in
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Select the repository containing CV Builder
6. Render will detect `render.yaml` automatically
7. Click "Apply"

### Step 3: Wait for Deployment

Initial deployment takes 10-15 minutes:
- PostgreSQL database provisioning (3-5 min)
- Redis provisioning (1-2 min)
- Docker build (5-10 min)
- First deployment (2-3 min)

Monitor progress in Render Dashboard → Logs

### Step 4: Note Your URLs

After deployment, note these URLs:
- **App URL**: `https://cv-builder-XXXX.onrender.com`
- **Database**: Internal URL (auto-configured)
- **Redis**: Internal URL (auto-configured)

---

## Post-Deployment Configuration

### Configure Base URL

1. Go to Render Dashboard → cv-builder service
2. Click "Environment" tab
3. Add/Edit:
   ```
   APP_BASE_URL = https://cv-builder-XXXX.onrender.com
   ```
4. Click "Save Changes"
5. Service will automatically redeploy

### Configure Google OAuth

#### Step 1: Create OAuth Credentials

1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Name: "CV Builder"
7. Authorized redirect URIs:
   ```
   https://cv-builder-XXXX.onrender.com/auth/callback
   ```
8. Click "Create"
9. Copy Client ID and Client Secret

#### Step 2: Add to Render

1. Go to Render Dashboard → cv-builder service
2. Click "Environment" tab
3. Add:
   ```
   GOOGLE_CLIENT_ID = your_client_id_here
   GOOGLE_CLIENT_SECRET = your_client_secret_here
   ```
4. Save changes (will trigger redeploy)

#### Step 3: Test OAuth

1. Wait for redeploy to complete
2. Visit your app URL
3. Click "Sign In with Google"
4. Should redirect to Google login
5. After login, should redirect back to dashboard

---

## SEO Setup

See [SEO_SETUP.md](./SEO_SETUP.md) for detailed instructions. Quick overview:

### Google Analytics

1. Create GA4 property at https://analytics.google.com
2. Get Measurement ID (G-XXXXXXXXXX)
3. Add to Render environment:
   ```
   GOOGLE_ANALYTICS_ID = G-XXXXXXXXXX
   ```

### Google Search Console

1. Go to https://search.google.com/search-console
2. Add property with your Render URL
3. Verify ownership (HTML file or meta tag)
4. Submit sitemap:
   ```
   https://cv-builder-XXXX.onrender.com/sitemap.xml
   ```

### Bing Webmaster Tools

1. Go to https://www.bing.com/webmasters
2. Add site (can import from Google Search Console)
3. Submit sitemap:
   ```
   https://cv-builder-XXXX.onrender.com/sitemap.xml
   ```

### Create Social Media Images

1. Create images (see [app/static/images/README.md](app/static/images/README.md)):
   - `og-image.png` (1200x630px)
   - `twitter-image.png` (1200x600px)
   - `favicon.ico` (32x32px)
   - `apple-touch-icon.png` (180x180px)

2. Add to repository:
   ```bash
   git add app/static/images/
   git commit -m "Add social media images"
   git push
   ```

3. Render will auto-deploy with new images

---

## Custom Domain (Optional)

### Step 1: Purchase Domain

Buy domain from:
- Namecheap
- GoDaddy
- Google Domains
- Cloudflare

### Step 2: Configure in Render

1. Render Dashboard → cv-builder → Settings
2. Click "Custom Domains"
3. Add domain: `cvbuilder.com` (or your domain)
4. Render will provide DNS records

### Step 3: Update DNS

Add these records to your domain registrar:

```
Type    Name    Value
CNAME   www     cv-builder-XXXX.onrender.com
A       @       [IP provided by Render]
```

### Step 4: Update Configuration

1. Update `APP_BASE_URL` to your domain:
   ```
   APP_BASE_URL = https://cvbuilder.com
   ```

2. Update Google OAuth redirect URI:
   ```
   https://cvbuilder.com/auth/callback
   ```

3. Update sitemap submissions in Search Console

---

## Monitoring & Maintenance

### Health Checks

Your app has a health endpoint:
```
https://your-app.onrender.com/health
```

Returns:
```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok"
}
```

### Logs

View logs in Render Dashboard:
1. Click on cv-builder service
2. Go to "Logs" tab
3. Real-time streaming logs
4. Search and filter capabilities

### Database Backups

Render Free tier: No automatic backups
Render Starter tier: 90-day backup retention

Manual backup:
```bash
# From Render Shell
pg_dump $DATABASE_URL > backup.sql

# Download via Render dashboard
```

### Performance Monitoring

1. **Render Metrics**:
   - CPU usage
   - Memory usage
   - Request counts
   - Response times

2. **Google Analytics**:
   - Traffic sources
   - User behavior
   - Conversion rates

3. **Search Console**:
   - Search impressions
   - Click-through rate
   - Keyword rankings

---

## Troubleshooting

### Build Failures

**Error: Docker build failed**
- Check Dockerfile syntax
- Ensure all dependencies in requirements.txt
- View build logs in Render Dashboard

**Error: Database connection failed**
- Wait for database to finish provisioning
- Check DATABASE_URL is auto-populated
- Restart service if database is ready

### OAuth Issues

**Error: Redirect URI mismatch**
- Ensure redirect URI in Google Console matches exactly
- Must include https:// and /auth/callback
- No trailing slash

**Error: Invalid client**
- Check GOOGLE_CLIENT_ID and SECRET are set correctly
- Verify OAuth consent screen is configured
- Check credentials haven't expired

### Application Errors

**Error: 500 Internal Server Error**
- Check application logs in Render Dashboard
- Look for Python stack traces
- Common issues:
  - Missing environment variables
  - Database migration needed
  - Import errors

**Error: Application sleeping**
- Free tier sleeps after 15 min inactivity
- First request after sleep takes 30-60 seconds
- Upgrade to Starter plan ($7/mo) for always-on

### SEO Issues

**Sitemap not found**
- Verify APP_BASE_URL is set correctly
- Check route is defined in app/__init__.py
- Test locally: http://localhost:8000/sitemap.xml

**Not appearing in Google**
- Submit sitemap to Search Console
- Wait 1-2 weeks for indexing
- Check robots.txt isn't blocking crawlers
- Verify meta tags in page source

---

## Upgrade to Production

For production use, upgrade from free tier:

### Web Service: Starter Plan ($7/month)
- Always-on (no sleeping)
- 512 MB RAM, 0.5 CPU
- Auto-scaling
- Better performance

### Database: Starter Plan ($7/month)
- 1 GB storage
- 90-day backup retention
- Point-in-time recovery
- Better performance

### Redis: Starter Plan ($10/month)
- 256 MB memory
- Better performance
- Persistent storage

**Total: ~$24/month for production-ready setup**

---

## Security Best Practices

1. **Never commit secrets**:
   - Add `.env` to `.gitignore`
   - Use Render environment variables
   - Rotate keys regularly

2. **HTTPS Only**:
   - Render provides free SSL
   - Set `TALISMAN_FORCE_HTTPS=true`
   - Update OAuth to require HTTPS

3. **Rate Limiting**:
   - Already configured with Flask-Limiter
   - Adjust limits in render.yaml if needed

4. **Database Security**:
   - Use strong passwords
   - Limit IP access if possible
   - Regular backups

5. **Monitoring**:
   - Set up Sentry for error tracking
   - Monitor logs regularly
   - Set up uptime monitoring

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **Docker Docs**: https://docs.docker.com
- **SEO Guide**: See [SEO_GUIDE.md](./SEO_GUIDE.md)
- **SEO Setup**: See [SEO_SETUP.md](./SEO_SETUP.md)

---

## Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render blueprint deployed
- [ ] APP_BASE_URL configured
- [ ] Google OAuth configured and tested
- [ ] Google Analytics added (optional)
- [ ] Sitemap submitted to Search Console
- [ ] Sitemap submitted to Bing Webmaster
- [ ] Social media images created
- [ ] Custom domain configured (optional)
- [ ] Sentry error tracking (optional)
- [ ] Monitoring set up
- [ ] Backup strategy implemented

---

**Last Updated**: 2026-02-17
**Version**: 1.0
