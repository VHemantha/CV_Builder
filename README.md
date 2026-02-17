# 🏗️ CV Builder

> **Professional Resume Builder** — Create ATS-friendly and professional CVs with real-time preview, multiple templates, and one-click PDF export.

Flask + PostgreSQL + Redis + Docker | Google OAuth | WeasyPrint PDF Generation

---

## ✨ Features

### Phase 1 — MVP (In Progress)
- ✅ **Google OAuth Authentication** — Secure login via Google
- ✅ **CV Dashboard** — Manage multiple CVs with CRUD operations
- ✅ **Interactive Builder** — Form-based editor with live preview
- ✅ **3 ATS Templates** — Clean, Modern, Executive layouts optimized for ATS
- ✅ **PDF Export** — High-quality PDF generation with WeasyPrint
- ✅ **Security Hardened** — CSRF protection, CSP headers, rate limiting
- ✅ **Docker Ready** — Full containerization for dev and production

### Phase 2 — Enhanced UX (Planned)
- 🔄 **3 Professional Templates** — Elegant, Creative, Bold designs
- 🔄 **Drag-and-Drop Sections** — Reorder CV sections with ease
- 🔄 **ATS Score Widget** — Real-time optimization suggestions
- 🔄 **Template Customization** — Color and font selection
- 🔄 **Version History** — Snapshot and restore previous versions
- 🔄 **Auto-Save** — Never lose your work

### Phase 3 — Power Features (Future)
- 🚀 **AI Writing Assistant** — OpenAI-powered content suggestions
- 🚀 **Custom Sections** — Add your own sections
- 🚀 **GDPR Compliance** — Data export and account deletion
- 🚀 **Performance** — Redis caching for preview renders

---

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose** installed
- **Google OAuth credentials** ([Get them here](https://console.cloud.google.com/apis/credentials))

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/cv-builder.git
cd cv-builder
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and set your Google OAuth credentials:
```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 3. Start with Docker Compose
```bash
docker-compose up --build
```

The application will start on **http://localhost:5000**

Services included:
- **Web App** (Flask) — Port 5000
- **PostgreSQL** — Port 5432
- **Redis** — Port 6379
- **pgAdmin** (optional) — Port 5050 (use `--profile tools`)

### 4. Initialize Database
On first run, migrations and template seeding happen automatically. To run manually:

```bash
# Run migrations
docker-compose exec web flask db upgrade

# Seed templates
docker-compose exec web python scripts/seed_templates.py
```

### 5. Access the Application
Open your browser and navigate to:
- **App**: http://localhost:5000
- **pgAdmin** (optional): http://localhost:5050

---

## 🛠️ Development

### Project Structure
```
cv-builder/
├── app/
│   ├── __init__.py           # App factory
│   ├── config.py             # Configuration classes
│   ├── extensions.py         # Flask extensions
│   ├── models/               # Database models
│   ├── auth/                 # Authentication blueprint
│   ├── cv/                   # CV management blueprint
│   ├── templates/            # Jinja2 templates
│   ├── static/               # CSS, JS, fonts
│   └── utils/                # Utilities
├── migrations/               # Alembic migrations
├── tests/                    # Unit and integration tests
├── scripts/                  # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── render.yaml               # Render.com deployment
└── requirements.txt
```

### Running Tests
```bash
# Install dev dependencies
docker-compose exec web pip install -r requirements-dev.txt

# Run tests with coverage
docker-compose exec web pytest tests/ -v --cov=app

# Run specific test file
docker-compose exec web pytest tests/unit/test_models.py -v
```

### Database Migrations
```bash
# Create a new migration
docker-compose exec web flask db migrate -m "Add new field"

# Apply migrations
docker-compose exec web flask db upgrade

# Rollback migration
docker-compose exec web flask db downgrade
```

### Accessing Logs
```bash
# Follow logs for all services
docker-compose logs -f

# Follow logs for web service only
docker-compose logs -f web

# View database logs
docker-compose logs db
```

### Hot Reload
The development setup includes hot reload. Just edit files in `app/` and changes will be reflected automatically.

---

## 🔒 Security

This application implements multiple security best practices:

- **Google OAuth 2.0** — No password storage
- **CSRF Protection** — All forms protected with tokens
- **Rate Limiting** — Redis-backed rate limiting on all endpoints
- **Content Security Policy** — Strict CSP headers via Flask-Talisman
- **Input Sanitization** — Bleach library for HTML sanitization
- **Secure Sessions** — HttpOnly, Secure, SameSite cookies
- **SQL Injection Prevention** — SQLAlchemy ORM with parameterized queries
- **Download Audit Log** — SHA-256 hashed IP addresses
- **Environment Secrets** — All sensitive data in environment variables

---

## 🚢 Deployment

### Deploy to Render.com (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect Render to GitHub**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**
   After deployment, set these in Render dashboard:
   - `APP_BASE_URL` — Your app URL (e.g., `https://cv-builder.onrender.com`)
   - `GOOGLE_CLIENT_ID` — Google OAuth Client ID
   - `GOOGLE_CLIENT_SECRET` — Google OAuth Client Secret
   - `SENTRY_DSN` (optional) — Sentry error tracking

4. **Configure Google OAuth**
   - Add authorized redirect URI: `https://YOUR_APP_URL/auth/callback`

### Manual Deployment (VPS/Cloud)

1. **Build Docker Image**
   ```bash
   docker build -t cv-builder:latest .
   ```

2. **Run with Environment Variables**
   ```bash
   docker run -d \
     -p 8000:8000 \
     --env-file .env \
     cv-builder:latest
   ```

3. **Use Docker Compose in Production**
   ```bash
   FLASK_ENV=production docker-compose up -d
   ```

---

## 📊 Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Flask 3.1, Python 3.12 |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Authentication** | Google OAuth 2.0 (Authlib) |
| **PDF Generation** | WeasyPrint 62 |
| **Containerization** | Docker, Docker Compose |
| **Deployment** | Render.com |
| **Security** | Flask-Talisman, Flask-Limiter, Bleach |
| **Testing** | pytest, pytest-flask |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality
- Run tests: `pytest tests/`
- Format code: `black app/`
- Sort imports: `isort app/`
- Lint: `flake8 app/`

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) — The web framework
- [WeasyPrint](https://weasyprint.org/) — PDF generation
- [Authlib](https://authlib.org/) — OAuth integration
- [Render](https://render.com/) — Deployment platform

---

## 📧 Support

If you have any questions or need help:
- Open an [Issue](https://github.com/your-username/cv-builder/issues)
- Email: support@cvbuilder.com (TODO: Update)

---

**Built with ❤️ using Flask and Claude Code**
