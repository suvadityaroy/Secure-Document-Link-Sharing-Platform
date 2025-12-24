# 🔒 Secure Document & Link Sharing Platform
🚀 [Live Demo](https://secure-document-link-sharing-platform-production-5bdd.up.railway.app/)

Secure uploads, share links with expiry/one-time options, and public downloads via token. Includes a demo login so reviewers can try the real flow quickly.

## 📋 What It Is
- ⚡ FastAPI backend with JWT auth and seeded demo user.
- 🔗 Share links with optional one-time access and configurable expiry (exact datetime or no-expiry).
- 📥 Public downloads via token, with access logs and download counts.
- 🎨 Frontend: static HTML/CSS/JS dashboard with upload, share, and copy/open actions.

## 🏗️ Architecture

```
Frontend (static HTML/JS)
	   |
	   v
   FastAPI API  <----->  Postgres (prod) / SQLite (local)
	   |
	   v
   File-Service (Java, 8081)
```

- 🐍 Backend: FastAPI (Python)
- 💾 Storage service: Java file-service on 8081 (or your own file store)
- 🔐 Auth: JWT, pbkdf2 password hashing
- 🗄️ Data: SQLite locally (swap to Postgres for production)

## ✨ Features
- 🔑 Login (email or username) → JWT
- 📤 Upload → share link (one-time, exact expiry, or no-expiry)
- 🌐 Public download by token; disable share to revoke
- 📊 Dashboard shows shares, expiry, downloads, and copy/open actions

## 🚀 Install & Run (Local)
- 🔧 API: `cd api && pip install -r requirements.txt && python run.py` (seeds demo user `demo@secureshare.com / DemoPass123!`).
- 🌐 Frontend: `cd frontend && python -m http.server 3000` then open http://localhost:3000.
- 📦 File service: run `file-service` on port 8081 or set `FILE_SERVICE_URL` to your deployed service for uploads/downloads.

## 🔄 How It Works
- 1️⃣ Login (or use Demo Login) to get a JWT stored locally.
- 2️⃣ Upload a file; backend returns metadata.
- 3️⃣ Pick expiry (days, exact datetime, or no-expiry) and optional one-time access, then generate a share link.
- 4️⃣ Share link is public; recipients download via token. Disable the share to revoke.
- 5️⃣ Dashboard lists your shares, expiry status, and download counts with copy/open actions.

---

👨‍💻 Created by Suvaditya Roy