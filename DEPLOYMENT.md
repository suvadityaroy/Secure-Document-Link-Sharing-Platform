# 🚀 Railway Deployment Guide

## ✅ What's Already Done
- ✓ Railway configuration file (`railway.toml`) with proper settings
- ✓ Database URL format converter (handles Railway's postgres:// format)
- ✓ CORS configured for Railway, Vercel, and Netlify deployments
- ✓ Procfile with correct uvicorn start command
- ✓ Environment variables configured in railway.toml
- ✓ All code pushed to GitHub main branch

## 📋 Steps to Deploy on Railway

### 1. Connect Railway to GitHub
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click on your project (pleasant-prosperity or similar)
3. Click the API service
4. Go to **Settings** tab
5. Under **Source**, connect to your GitHub repository: `suvadityaroy/Secure-Document-Link-Sharing-Platform`
6. Select branch: `main`
7. Railway will automatically detect the `railway.toml` configuration

### 2. Verify Environment Variables
Railway should auto-configure these from `railway.toml`:
- ✓ `JWT_SECRET` - Pre-configured (you can change it)
- ✓ `FILE_SERVICE_URL` - Set to localhost:8081 (update after deploying file-service)
- ✓ `DATABASE_URL` - Auto-linked to your Postgres service

To update:
1. Go to **Variables** tab in your service
2. Modify `JWT_SECRET` to a secure random string (32+ chars)
3. Update `FILE_SERVICE_URL` once you deploy the file-service

### 3. Deploy!
Railway will automatically:
1. Build from the `/api` directory
2. Install dependencies from `requirements.txt`
3. Run database migrations (auto-create tables)
4. Seed the demo user
5. Start the API with uvicorn

### 4. Check Deployment Status
1. Go to **Deployments** tab
2. Click the latest deployment
3. Watch the logs for:
   ```
   Creating database tables...
   Seeded demo user for quick access
   Uvicorn running on http://0.0.0.0:$PORT
   ```

### 5. Test Your API
Once deployed, Railway will give you a public URL like:
`https://your-service.railway.app`

Test endpoints:
- Health check: `https://your-service.railway.app/health`
- API docs: `https://your-service.railway.app/docs`
- Demo login: POST to `/api/auth/login` with:
  ```json
  {
    "email": "demo@secureshare.com",
    "password": "DemoPass123!"
  }
  ```

## 🌐 Frontend Deployment (Next Step)

### Option 1: Vercel (Recommended for Static Sites)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel

# Set environment variable in Vercel dashboard:
# VITE_API_URL = https://your-railway-api.railway.app/api
```

### Option 2: Netlify
1. Go to [Netlify](https://netlify.com)
2. Connect your GitHub repo
3. Set publish directory: `frontend`
4. Add environment variable:
   - `VITE_API_URL` = `https://your-railway-api.railway.app/api`

### Option 3: Railway Static Service
1. Add new service in Railway
2. Connect same GitHub repo
3. Set Root Directory: `/frontend`
4. Railway will serve static files

## ⚙️ After Deployment

### Update Frontend API URL
In `frontend/index.html`, change:
```javascript
const API_BASE = 'https://your-railway-api.railway.app/api';
```

### Deploy File Service (Java)
1. Create another Railway service for `file-service`
2. Set Root Directory: `/file-service`
3. Note the deployed URL
4. Update `FILE_SERVICE_URL` environment variable in API service

## 🔍 Troubleshooting

### Build Fails
- Check Railway logs in **Deployments** tab
- Verify `railway.toml` is in root directory
- Ensure `requirements.txt` has all dependencies

### Database Connection Error
- Verify `DATABASE_URL` is linked to Postgres service
- Check Postgres service is running in Railway dashboard

### CORS Errors
- Add your frontend domain to `ALLOWED_ORIGINS` in `api/app/core/config.py`
- Commit and push changes

## 📝 Important Notes
- Demo user is auto-seeded: `demo@secureshare.com` / `DemoPass123!`
- JWT tokens expire after 30 minutes (configurable in config.py)
- Database uses PostgreSQL in production (auto-configured by Railway)
- All file uploads require the file-service to be running

---

🎉 Your API should now be live on Railway! Check the logs and test the endpoints.
