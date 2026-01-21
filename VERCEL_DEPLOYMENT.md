# 🚀 Vercel Deployment Guide

## Complete Setup: Frontend on Vercel + Backend on Railway/Render

This guide shows you how to deploy your Forex Trading Dashboard so you can access it from anywhere.

---

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel         │ ───────▶ │  Railway/Render  │
│  (Frontend)     │  HTTPS   │  (Backend API)   │
│  React + Vite   │ ◀─────── │  Flask + Engine  │
└─────────────────┘         └──────────────────┘
     ↓                              ↓
   User                        MongoDB Atlas
```

---

## Step 1: Deploy Backend (Choose ONE)

### Option A: Railway (Recommended)

1. **Install Railway CLI**
   ```powershell
   npm install -g @railway/cli
   ```

2. **Login and Deploy**
   ```powershell
   cd c:\Users\rajpa\Desktop\Engine
   railway login
   railway init
   railway up
   ```

3. **Get Backend URL**
   - Run: `railway open`
   - Copy URL (e.g., `https://forex-engine-production.up.railway.app`)
   - **Save this URL - you'll need it for Step 2!**

4. **Add Environment Variables** (in Railway dashboard)
   ```
   FMP_API_KEY=your_key
   NEWS_API_KEY=your_key
   TWELVE_DATA_KEY=your_key
   ALPHA_VANTAGE_KEY=your_key
   TAAPI_KEY=your_key
   FINNHUB_API_KEY=your_key
   POLYGON_API_KEY=your_key
   MONGO_URI=your_mongodb_atlas_url
   ```

### Option B: Render

1. Go to https://render.com and sign up
2. Create New Web Service
3. Connect GitHub or upload code
4. Configure:
   - **Name**: forex-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_dashboard.py`
5. Add environment variables (same as Railway)
6. Deploy and copy the URL (e.g., `https://forex-backend.onrender.com`)

---

## Step 2: Deploy Frontend to Vercel

### Prerequisites
- GitHub account (optional but recommended)
- Backend deployed and URL copied from Step 1

### Method 1: Via GitHub (Recommended)

1. **Push to GitHub**
   ```powershell
   cd c:\Users\rajpa\Desktop\Engine
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/forex-engine.git
   git push -u origin main
   ```

2. **Deploy on Vercel**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - Click "Deploy"

3. **Add Environment Variable**
   - In Vercel dashboard → Settings → Environment Variables
   - Add:
     ```
     VITE_API_URL = https://your-backend-url.com
     ```
     (Use the URL from Step 1 WITHOUT trailing slash)
   - Redeploy

4. **Access Your App**
   - Vercel gives you: `https://forex-engine.vercel.app`
   - Open in any browser, phone, tablet!

### Method 2: Via Vercel CLI

1. **Install Vercel CLI**
   ```powershell
   npm install -g vercel
   ```

2. **Deploy**
   ```powershell
   cd c:\Users\rajpa\Desktop\Engine\frontend
   vercel
   ```

3. **Follow Prompts**
   - Set up and deploy?: Y
   - Scope: (your account)
   - Link to existing project?: N
   - Project name: forex-dashboard
   - Directory: `./`
   - Override settings?: N

4. **Set Environment Variable**
   ```powershell
   vercel env add VITE_API_URL
   ```
   - Enter your backend URL when prompted
   - Select Production + Preview
   - Redeploy: `vercel --prod`

5. **Done!**
   - URL shown in terminal

---

## Step 3: Setup MongoDB Atlas (For Persistent Data)

1. **Create Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up (free)

2. **Create Cluster**
   - Choose free tier (M0)
   - Select region closest to you
   - Click "Create Cluster"

3. **Create Database User**
   - Security → Database Access
   - Add new user
   - Save username/password

4. **Whitelist IP**
   - Security → Network Access
   - Add IP Address
   - Allow access from anywhere: `0.0.0.0/0` (for cloud deployment)

5. **Get Connection String**
   - Clusters → Connect
   - Connect your application
   - Copy connection string
   - Replace `<password>` with your password

6. **Add to Backend Environment Variables**
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/forex?retryWrites=true&w=majority
   ```

---

## Configuration Summary

### Your `.env.local` for Frontend (Vercel)
```
VITE_API_URL=https://your-backend-url.com
```

### Your Environment Variables for Backend (Railway/Render)
```
FMP_API_KEY=your_key
NEWS_API_KEY=your_key
TWELVE_DATA_KEY=your_key
ALPHA_VANTAGE_KEY=your_key
TAAPI_KEY=your_key
FINNHUB_API_KEY=your_key
POLYGON_API_KEY=your_key
MONGO_URI=mongodb+srv://...
PORT=5000
```

---

## Testing Your Deployment

1. **Test Backend**
   ```
   https://your-backend-url.com/api/status
   ```
   Should return: `{"status": "running", ...}`

2. **Test Frontend**
   - Open: `https://forex-engine.vercel.app`
   - Should see dashboard
   - Should load signals and news

3. **Common Issues**

   **Problem**: Frontend loads but no data
   - **Fix**: Check VITE_API_URL is set correctly in Vercel
   - **Fix**: Ensure backend CORS is enabled (already done in web_dashboard.py)

   **Problem**: CORS errors
   - **Fix**: Backend web_dashboard.py has CORS enabled
   - **Fix**: Make sure VITE_API_URL doesn't have trailing slash

   **Problem**: Backend crashes
   - **Fix**: Check logs in Railway/Render dashboard
   - **Fix**: Ensure all environment variables are set

---

## Local Testing Before Deployment

Test the production build locally:

```powershell
# 1. Set API URL
cd frontend
echo "VITE_API_URL=http://localhost:5000" > .env.local

# 2. Build frontend
npm run build

# 3. Test with local backend
cd ..
python web_dashboard.py

# 4. Visit http://localhost:5000
```

If it works locally, it will work deployed!

---

## Costs

| Service | Free Tier | Cost |
|---------|-----------|------|
| **Vercel** | Unlimited frontend deployments | $0 |
| **Railway** | $5/month credit | $0 (if under limit) |
| **MongoDB Atlas** | 512MB storage | $0 |
| **Total** | | **$0/month** |

---

## Access Your Dashboard

After deployment:
- **Frontend URL**: `https://forex-engine.vercel.app` (or custom domain)
- **Backend API**: `https://your-backend-url.com/api/status`

You can now:
- ✅ Check signals from your phone
- ✅ Monitor trades from anywhere
- ✅ No need to run terminal
- ✅ Always online (24/7)

---

## Quick Commands Reference

### Vercel (Frontend)
```powershell
cd frontend
vercel                    # Deploy
vercel --prod            # Deploy to production
vercel env add           # Add environment variable
vercel logs              # View logs
```

### Railway (Backend)
```powershell
railway login            # Login
railway init            # Initialize project
railway up              # Deploy
railway open            # Open dashboard
railway logs            # View logs
railway env              # Manage environment variables
```

---

## 🔒 Security Checklist

- ✅ Never commit `.env` files
- ✅ Use environment variables for all API keys
- ✅ MongoDB: Use password authentication
- ✅ MongoDB: Restrict IP access if possible
- ✅ HTTPS only (Vercel & Railway provide this)

---

## 🆘 Need Help?

**Backend not working?**
- Check Railway/Render logs
- Verify environment variables are set
- Test `/api/status` endpoint

**Frontend not connecting?**
- Verify `VITE_API_URL` in Vercel settings
- Check browser console for errors
- Ensure backend URL has no trailing slash

**Still stuck?**
- Check Railway docs: https://docs.railway.app
- Check Vercel docs: https://vercel.com/docs
- Check Render docs: https://render.com/docs

---

## 🎉 You're Done!

Your trading dashboard is now live and accessible from anywhere in the world!

**Frontend**: Beautiful, fast React app  
**Backend**: Python trading engine with ML  
**Database**: Persistent MongoDB storage  
**Cost**: $0 with free tiers  

Happy trading! 📈
