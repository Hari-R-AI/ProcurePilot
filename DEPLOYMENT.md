# Deployment Guide for ProcurePilot

## Overview

ProcurePilot consists of:
- **Backend**: FastAPI application (Python)
- **Frontend**: Next.js application (JavaScript/TypeScript)

Both can be deployed independently or together using Docker Compose.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Backend Setup

```bash
# Navigate to backend
cd apps/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env.local
# Edit .env.local with your settings

# Run development server
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend
cd apps/web

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## Docker Deployment

### Using Docker Compose (Recommended for Local Dev)

```bash
# From project root
docker-compose up
```

This starts:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

#### Configure Environment

Create `.env.docker` in project root:

```env
GROQ_API_KEY=your-groq-api-key-here
PROCUREPILOT_ENV=development
```

Rebuild after env changes:

```bash
docker-compose up --build
```

### Stopping Services

```bash
docker-compose down

# With volume cleanup
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web
```

---

## Backend Deployment

### Option 1: Docker (Recommended)

#### Build Image

```bash
cd apps/api
docker build -t procurepilot-api:latest .
```

#### Run Container

```bash
docker run -d \
  --name procurepilot-api \
  -p 8000:8000 \
  -e PROCUREPILOT_GROQ_API_KEY=your-key \
  -e PROCUREPILOT_ENV=production \
  -e PROCUREPILOT_DATABASE_URL=sqlite:///./procurepilot.db \
  -v procurepilot-data:/app/data \
  procurepilot-api:latest
```

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROCUREPILOT_ENV` | `development` | Environment (development/staging/production) |
| `PROCUREPILOT_DEBUG` | `false` | Debug mode |
| `PROCUREPILOT_DATABASE_URL` | `sqlite:///./procurepilot.db` | Database URL |
| `PROCUREPILOT_GROQ_API_KEY` | (required) | Groq API key |
| `PROCUREPILOT_LOG_LEVEL` | `INFO` | Logging level |
| `PROCUREPILOT_CORS_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins |

### Option 2: HuggingFace Spaces

1. Create new Space on HuggingFace
2. Select "Docker" runtime
3. Push code:

```bash
git clone https://huggingface.co/spaces/username/procurepilot
cd procurepilot

# Copy backend files
cp -r ../../apps/api/* .

# Create Space requirements
# Add Dockerfile, .env setup, etc.
```

### Option 3: Manual Deployment

```bash
cd apps/api

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn (production WSGI server)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

1. **Connect GitHub Repository**
   - Go to https://vercel.com/new
   - Import GitHub repository
   - Select project root

2. **Configure Project**
   - Framework: Next.js
   - Root Directory: `apps/web`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Set Environment Variables**
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
   ```

4. **Deploy**
   - Vercel automatically deploys on every push

### Option 2: Docker

```bash
cd apps/web

# Build image
docker build -t procurepilot-web:latest .

# Run container
docker run -d \
  --name procurepilot-web \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://api-server:8000 \
  procurepilot-web:latest
```

### Option 3: Traditional Hosting

```bash
cd apps/web

# Build
npm run build

# Start production server
npm start
```

Deploy the output to any Node.js hosting:
- AWS (EC2, ECS, Lambda with wrapper)
- Google Cloud Run
- Azure App Service
- DigitalOcean
- Netlify (Static export)

---

## Environment Configuration

### Backend Environment Variables

Create `apps/api/.env.production`:

```env
PROCUREPILOT_ENV=production
PROCUREPILOT_DEBUG=false
PROCUREPILOT_DATABASE_URL=postgresql://user:password@host:5432/procurepilot
PROCUREPILOT_GROQ_API_KEY=your-groq-api-key
PROCUREPILOT_LOG_LEVEL=INFO
PROCUREPILOT_CORS_ORIGINS=["https://your-domain.com"]
PROCUREPILOT_ALLOWED_HOSTS=["api.your-domain.com"]
```

### Frontend Environment Variables

Create `apps/web/.env.production`:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
```

---

## Database Migration

### Production Database Switch

Default: SQLite (file-based)
Production Recommendation: PostgreSQL

```bash
# Update DATABASE_URL in .env
PROCUREPILOT_DATABASE_URL=postgresql://user:password@host:5432/procurepilot

# Tables are auto-created on startup via SQLAlchemy
```

### Backup SQLite Database

```bash
# Copy database file
cp procurepilot.db procurepilot.db.backup

# Or with Docker
docker cp procurepilot-api:/app/data/procurepilot.db ./backup.db
```

---

## Monitoring & Health Checks

### Health Endpoints

Backend provides health check endpoints:

```bash
# Liveness probe (is service running?)
curl http://localhost:8000/api/v1/health/live

# Readiness probe (is service ready to accept requests?)
curl http://localhost:8000/api/v1/health/ready
```

### Docker Health Checks

Both containers include health checks:

```bash
# Check container health
docker ps  # See "(healthy)" status

# View health history
docker inspect procurepilot-api | grep -A 20 Health
```

### Logging

Backend logs to stdout (container-friendly):

```bash
# View logs
docker logs -f procurepilot-api

# With timestamps
docker logs -f --timestamps procurepilot-api
```

---

## Performance Optimization

### Backend Optimization

1. **Database**
   - Use PostgreSQL for production (SQLite single-writer limit)
   - Add indexes on frequently queried fields

2. **Caching**
   - Add Redis for session/response caching
   - Cache policy lookups

3. **Async**
   - All endpoints are async-ready
   - LangGraph uses async for concurrency

### Frontend Optimization

1. **Next.js Built-in**
   - Image optimization
   - Code splitting
   - Automatic minification

2. **Deployment**
   - Enable compression
   - Set cache headers
   - Use CDN

---

## Security Checklist

- [ ] Set strong `GROQ_API_KEY`
- [ ] Use HTTPS in production
- [ ] Configure CORS properly (`CORS_ORIGINS`)
- [ ] Set secure database credentials
- [ ] Enable database encryption
- [ ] Regular security updates
- [ ] Monitor error logs for vulnerabilities
- [ ] Use environment-specific secrets (not in git)
- [ ] Enable API rate limiting (future)
- [ ] Set up DDoS protection

---

## Troubleshooting

### Backend Issues

#### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
```

#### Database Locked

```bash
# Remove SQLite database
rm procurepilot.db
# Database will be recreated on next run
```

#### Import Errors

```bash
# Ensure you're in correct directory
cd apps/api

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Run with explicit module path
python -m uvicorn app.main:app --reload
```

### Frontend Issues

#### API Connection Error

1. Verify backend is running
2. Check `NEXT_PUBLIC_API_BASE_URL` is correct
3. Verify CORS configuration in backend
4. Check browser console for errors

#### Build Failure

```bash
# Clear build cache
rm -rf .next node_modules package-lock.json

# Reinstall and rebuild
npm install
npm run build
```

### Docker Issues

#### Container Won't Start

```bash
# Check logs
docker logs procurepilot-api

# Rebuild image
docker-compose build --no-cache

# Restart
docker-compose up
```

#### Port Conflict

```bash
# Change port in docker-compose.yml
# Or stop conflicting service
docker stop <container_name>
```

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database ready (SQLite or PostgreSQL)
- [ ] Groq API key obtained and set
- [ ] CORS origins configured
- [ ] Health checks passing
- [ ] Tests passing (`pytest` for backend)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] API connectivity tested
- [ ] Logging configured
- [ ] Backups scheduled
- [ ] Monitoring set up
- [ ] Documentation updated

---

## Rollback Strategy

### Using Docker

```bash
# Save current version
docker tag procurepilot-api:latest procurepilot-api:v1.0.0

# Rollback if needed
docker run procurepilot-api:v1.0.0
```

### Using Vercel

- Automatic rollback available in Vercel dashboard
- No manual action needed

---

## Next Steps

1. Obtain Groq API key from https://console.groq.com
2. Configure environment variables
3. Deploy backend (HuggingFace Spaces or Docker)
4. Deploy frontend (Vercel recommended)
5. Test end-to-end workflow
6. Monitor logs and health checks
7. Plan backup and recovery procedures

---

## Support

For issues:
1. Check logs: `docker logs procurepilot-api`
2. Review error responses from API
3. Verify environment variables
4. Check health endpoints
5. Review troubleshooting section above
