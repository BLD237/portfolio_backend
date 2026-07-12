# Portfolio Ecosystem - Deployment Guide

This documentation explains how to deploy the entire portfolio ecosystem, including the backend API, frontend website, admin console, and Nginx reverse proxy.

## Project Structure
* **Frontend Portfolio Website** (`/mufor-belmond`): Runs on port `3080` (accessible at `https://muforbelmond.tech`).
* **Admin Dashboard** (`/admin`): Runs on port `3081` (accessible at `https://admin.muforbelmond.tech`).
* **API Backend** (`/backend`): Runs on port `8085` (accessible at `https://api.muforbelmond.tech`).

---

## 🚀 Step 1: Backend Environment Setup
Create a production `.env` file inside `/backend/.env` containing:
```env
ENVIRONMENT=production
DATABASE_URL=sqlite:///./data/portfolio.db
SECRET_KEY=generate-a-strong-random-key-here
ADMIN_EMAIL=admin@muforbelmond.tech
ADMIN_PASSWORD=SetYourSecureAdminPasswordHere

# CORS Allowed Origins
CORS_ORIGINS=http://localhost:3080,http://localhost:3081,http://localhost:8085,http://127.0.0.1:3080,http://127.0.0.1:3081,http://127.0.0.1:8085,https://muforbelmond.tech,https://admin.muforbelmond.tech,https://api.muforbelmond.tech

# SMTP Notification Settings
CONTACT_RECIPIENT_EMAIL=muforbelmond20@gmail.com,muforbelmond@icloud.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=muforbelmond20@gmail.com
SMTP_PASSWORD=your-gmail-app-specific-password
SMTP_FROM_EMAIL=muforbelmond20@gmail.com
```

---

## 🐳 Step 2: Deployment Methods

Choose **one** of the following deployment paths depending on your infrastructure:

### Method A: Docker Compose (Recommended)
Each repository contains its own optimized production `Dockerfile` and `docker-compose.yml` for isolated service management.

1. **Start the API Backend**
   ```bash
   cd backend
   docker compose up --build -d
   ```
2. **Start the Admin Console**
   ```bash
   cd ../admin
   docker compose up --build -d
   ```
3. **Start the Frontend Portfolio**
   ```bash
   cd ../mufor-belmond
   docker compose up --build -d
   ```

### Method B: Manual PM2 Process Deployment
If you prefer running services directly on the host using PM2:

1. **Start Backend (FastAPI)**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Start Uvicorn
   pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8085" --name "portfolio-backend"
   ```
2. **Start Admin Console (Next.js)**
   ```bash
   cd ../admin
   npm ci
   NEXT_PUBLIC_API_URL=https://api.muforbelmond.tech/api PORT=3081 npm run build
   pm2 start "npm run start" --name "portfolio-admin"
   ```
3. **Start Frontend Portfolio (Next.js)**
   ```bash
   cd ../mufor-belmond
   npm ci
   NEXT_PUBLIC_API_URL=https://api.muforbelmond.tech/api PORT=3080 npm run build
   pm2 start "npm run start" --name "portfolio-frontend"
   ```

---

## 🔒 Step 3: Nginx Reverse Proxy & SSL Setup

Your backend repository is shipped with pre-defined Nginx site configuration blocks located in `backend/nginx/` and a deployment automation `Makefile` in `backend/Makefile`.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Deploy Nginx configuration blocks:**
   This copies the configurations to `/etc/nginx/sites-available`, sets up symlinks to `/etc/nginx/sites-enabled`, tests the syntax, and reloads Nginx.
   ```bash
   make deploy-nginx
   ```
3. **Install SSL certificates via Let's Encrypt Certbot:**
   This installs Certbot and configures certificates for `muforbelmond.tech`, `www.muforbelmond.tech`, `admin.muforbelmond.tech`, and `api.muforbelmond.tech`.
   ```bash
   make install-ssl
   ```

*(Alternatively, run `make deploy-all` to execute both Nginx and SSL setup in a single command).*

---

## 🛠️ Verification & Monitoring
* Public Frontend: `https://muforbelmond.tech`
* Admin panel: `https://admin.muforbelmond.tech`
* Health Check Endpoint: `https://api.muforbelmond.tech/health` (should return `{"status":"ok"}`)
* Logs check (Docker): `docker compose logs -f`
* Logs check (PM2): `pm2 logs`
