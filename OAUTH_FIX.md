# OAuth Fix Guide - redirect_uri_mismatch

## Problem Diagnosis

The error `redirect_uri_mismatch` occurs because the redirect URI sent by your app doesn't match what's configured in Google Cloud Console.

**Your Redirect URI**: `https://cv-builder-2-e4lt.onrender.com/auth/callback`

## ✅ Professional Fix (3 Steps)

### Step 1: Set APP_BASE_URL in Render

This is **CRITICAL** and likely the root cause.

1. Go to: https://dashboard.render.com
2. Select your **cv-builder-2** service
3. Click **Environment** tab
4. Find or add `APP_BASE_URL`:
   ```
   APP_BASE_URL = https://cv-builder-2-e4lt.onrender.com
   ```
   ⚠️ **Important**: No trailing slash!

5. Click **Save Changes**
6. Wait for auto-redeploy (2-3 minutes)

### Step 2: Configure Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your **OAuth 2.0 Client ID**
3. Under **Authorized redirect URIs**, add:
   ```
   https://cv-builder-2-e4lt.onrender.com/auth/callback
   ```
4. Under **Authorized JavaScript origins**, add:
   ```
   https://cv-builder-2-e4lt.onrender.com
   ```
5. Click **SAVE**

### Step 3: Verify Environment Variables

In Render Dashboard → Environment, ensure these are set:

```env
APP_BASE_URL=https://cv-builder-2-e4lt.onrender.com
GOOGLE_CLIENT_ID=[your-client-id]
GOOGLE_CLIENT_SECRET=[your-client-secret]
OAUTHLIB_INSECURE_TRANSPORT=0
```

---

## 🔍 Debugging Steps

### Check What Redirect URI is Being Sent

1. Visit your app
2. Click "Sign In with Google"
3. Look at the URL you're redirected to
4. Check the `redirect_uri` parameter

Example:
```
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=...
  redirect_uri=https://cv-builder-2-e4lt.onrender.com/auth/callback  ← Check this
  response_type=code
  scope=openid%20email%20profile
```

The `redirect_uri` must **exactly match** what's in Google Console.

---

## 🎯 Common Issues & Solutions

### Issue 1: Wrong Base URL

**Symptom**: redirect_uri shows `http://` instead of `https://`

**Fix**:
- Set `APP_BASE_URL=https://cv-builder-2-e4lt.onrender.com` in Render
- Ensure `OAUTHLIB_INSECURE_TRANSPORT=0`

### Issue 2: Missing Trailing Slash Mismatch

**Your App Sends**: `https://cv-builder-2-e4lt.onrender.com/auth/callback`
**Google Expects**: `https://cv-builder-2-e4lt.onrender.com/auth/callback/`

**Fix**: Remove trailing slash from Google Console

### Issue 3: Wrong Domain

**Your App Sends**: `https://cv-builder-2-e4lt.onrender.com/auth/callback`
**Google Expects**: `https://localhost:5000/auth/callback`

**Fix**: APP_BASE_URL is not set or wrong in Render

### Issue 4: Multiple Deployments

If you have multiple Render services (cv-builder, cv-builder-2, etc.):
- Each needs its own redirect URI in Google Console
- Or use one and set APP_BASE_URL correctly

---

## 📝 Complete Configuration Checklist

### Render Environment Variables

```env
# Required
APP_BASE_URL=https://cv-builder-2-e4lt.onrender.com
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
SECRET_KEY=[auto-generated-by-render]

# Security
OAUTHLIB_INSECURE_TRANSPORT=0
FLASK_ENV=production

# Database (current config)
DATABASE_URL=sqlite:///cv_builder.db
REDIS_URL=

# Optional
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
SENTRY_DSN=
```

### Google Cloud Console

**OAuth 2.0 Client ID Settings**:

```
Application type: Web application
Name: CV Builder

Authorized JavaScript origins:
  https://cv-builder-2-e4lt.onrender.com

Authorized redirect URIs:
  https://cv-builder-2-e4lt.onrender.com/auth/callback
```

---

## 🔧 Quick Test

After making changes:

```bash
# 1. Clear browser cache or use incognito
# 2. Visit your app
curl https://cv-builder-2-e4lt.onrender.com

# 3. Try OAuth
# Click "Sign In with Google"
# Should redirect to Google
# Should redirect back successfully
```

---

## 🆘 Still Not Working?

### Enable Debug Mode Temporarily

Add to Render environment:
```
AUTHLIB_INSECURE_TRANSPORT=1
```

Then check Render logs during OAuth attempt:
```
Render Dashboard → Logs tab
Filter for: "redirect_uri" or "oauth"
```

### Verify Callback URL

Test the callback URL directly:
```
https://cv-builder-2-e4lt.onrender.com/auth/callback
```

Should return an error (expected without OAuth code), but shouldn't 404.

### Check Google OAuth Consent Screen

1. APIs & Services → OAuth consent screen
2. Ensure:
   - App is not in testing mode (or add your email to test users)
   - Scopes include: email, profile, openid
   - No warnings or errors

---

## 💡 Pro Tips

### Use Environment Variable for Redirect URI

For more control, you can set the redirect URI explicitly in code:

```python
# In routes.py, line 28
redirect_uri = os.environ.get(
    'GOOGLE_REDIRECT_URI',
    url_for("auth.google_callback", _external=True)
)
```

Then in Render:
```
GOOGLE_REDIRECT_URI=https://cv-builder-2-e4lt.onrender.com/auth/callback
```

### Log the Redirect URI

Add debug logging in routes.py:
```python
redirect_uri = url_for("auth.google_callback", _external=True)
print(f"OAuth redirect URI: {redirect_uri}")  # Check Render logs
return oauth.google.authorize_redirect(redirect_uri)
```

---

## ✅ Expected Flow

```
1. User clicks "Sign In with Google"
   → Redirects to /auth/google

2. App generates redirect_uri
   → https://cv-builder-2-e4lt.onrender.com/auth/callback

3. App redirects to Google
   → https://accounts.google.com/o/oauth2/v2/auth?
     redirect_uri=https://cv-builder-2-e4lt.onrender.com/auth/callback

4. Google checks if redirect_uri is authorized
   → Must match Google Console exactly

5. User approves
   → Google redirects to:
     https://cv-builder-2-e4lt.onrender.com/auth/callback?code=...

6. App exchanges code for token
   → Creates/updates user
   → Logs user in
   → Redirects to dashboard ✅
```

---

## 🎯 The Fix That Works

**99% of the time, the issue is**:

```
APP_BASE_URL is not set in Render!
```

**Solution**:
1. Render Dashboard → Environment
2. Add: `APP_BASE_URL=https://cv-builder-2-e4lt.onrender.com`
3. Save & wait for redeploy
4. Try OAuth again ✅

---

**Last Updated**: Check your Render logs after the next deploy to confirm the redirect URI being generated.
