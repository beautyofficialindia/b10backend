# DEPLOYMENT_GUIDE.md

## Platform Agnostic Deployment
The backend is designed to deploy seamlessly to any PAAS (Render, Railway, Heroku) or traditional VPS.

### 1. Environment Preparation
Ensure the platform injects the following secrets into the environment:
- `SECRET_KEY` (Strong randomized string)
- `DATABASE_URL` (Supabase PostgreSQL Connection String)
- `OPENROUTER_API_KEY` (AI Engine API Key)
- `ALLOWED_HOSTS` (e.g., `api.b10itsolution.com,localhost`)
- `CORS_ALLOW_ALL_ORIGINS` (`False` in strict production)

### 2. Build Steps
Most PAAS providers detect `requirements.txt`. Ensure the build command installs dependencies:
```bash
pip install -r requirements.txt
```

### 3. Release Commands
Before the server starts, you must execute database migrations and initialize static files (if required by your platform, though WhiteNoise handles it dynamically):
```bash
python manage.py migrate
```

### 4. Application Boot
Bind the application to the provided port (usually `$PORT`) using Gunicorn (or the default PAAS runner):
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```
