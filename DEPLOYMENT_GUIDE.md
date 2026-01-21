# Deployment Guide - Forex Trading Dashboard

Access your trading signals from anywhere! This guide covers deploying your full-stack application.

---

## 🚀 Recommended Platforms (Free Tier Available)

### Option 1: **Railway** (Recommended - Easiest)

**Why Railway?**
- ✅ Free $5/month credit (enough for small apps)
- ✅ Automatic deployments from GitHub
- ✅ Built-in MongoDB support
- ✅ Single command deployment
- ✅ Custom domains
- ✅ Environment variables management

**Steps:**

1. **Install Railway CLI**
   ```powershell
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```powershell
   railway login
   ```

3. **Initialize and Deploy**
   ```powershell
   cd c:\Users\rajpa\Desktop\Engine
   railway init
   railway up
   ```

4. **Add MongoDB (Optional)**
   ```powershell
   railway add --plugin mongodb
   ```

5. **Set Environment Variables** (in Railway dashboard)
   - Add all your API keys from `.env` file
   - Railway will automatically set `PORT`

6. **Get Your URL**
   - Railway will give you a URL like: `https://your-app.railway.app`
   - Access from anywhere!

---

### Option 2: **Render** (Great Alternative)

**Why Render?**
- ✅ 750 hours/month free (enough for 24/7)
- ✅ Easy MongoDB integration
- ✅ Auto-deploy from GitHub
- ✅ Free SSL certificates

**Steps:**

1. **Go to** https://render.com and sign up

2. **Create a New Web Service**
   - Connect your GitHub repository
   - Or upload code directly

3. **Configure:**
   ```
   Name: forex-trading-engine
   Environment: Python 3
   Build Command: pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
   Start Command: python web_dashboard.py
   ```

4. **Add Environment Variables:**
   - Copy all from your `.env` file
   - Add to Render dashboard

5. **Deploy!**
   - Render will build and deploy
   - Get URL: `https://forex-trading-engine.onrender.com`

---

### Option 3: **Vercel (Frontend) + Render (Backend)**

**Best for:** Production-grade deployments

**Frontend (Vercel):**
1. Go to https://vercel.com
2. Import `frontend` folder
3. Deploy (free, instant)

**Backend (Render):**
1. Deploy Flask app as above
2. Update frontend API endpoint to Render URL

---

## 📦 Pre-Deployment Checklist

Before deploying, ensure:

### 1. Build Frontend
```powershell
cd frontend
npm install
npm run build
```
This creates `dist` folder with production files.

### 2. Update `.dockerignore` and `.gitignore`
Make sure these don't exclude:
- `frontend/dist/` (needed for production)
- `.env` should be ignored (set vars in platform)

### 3. Database Choice

**Option A: SQLite (Current - Simple)**
- ✅ Works out of box
- ❌ Data lost on platform restart
- Good for: Testing

**Option B: MongoDB Atlas (Recommended)**
- ✅ Persistent data
- ✅ Free tier: 512MB
- ✅ Works from anywhere
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Add to environment variables as `MONGO_URI`

### 4. Environment Variables to Set

Copy these from your `.env` file to your deployment platform:

```
FMP_API_KEY=your_key
NEWS_API_KEY=your_key
TWELVE_DATA_KEY=your_key
ALPHA_VANTAGE_KEY=your_key
TAAPI_KEY=your_key
FINNHUB_API_KEY=your_key
POLYGON_API_KEY=your_key
MONGO_URI=your_mongodb_url (optional)
```

---

## 🔧 Files Already Configured for Deployment

✅ `Procfile` - Railway/Heroku deployment
✅ `runtime.txt` - Python version
✅ `requirements.txt` - Dependencies
✅ `Dockerfile` - Container deployment
✅ `web_dashboard.py` - Serves frontend + backend

---

## 🌐 After Deployment

Once deployed, you can:

1. **Access Dashboard:** `https://your-app-url.com`
2. **API Endpoints:**
   - Status: `/api/status`
   - Signals: `/api/signals`
   - News: `/api/news`
   - Market Data: `/api/data/EURUSD`

3. **Mobile Access:** Works on phone/tablet browser

4. **Bookmarks:** Add to home screen on mobile

---

## 💰 Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Railway** | $5/month credit | Full-stack apps |
| **Render** | 750 hrs/month | Python apps |
| **Vercel** | Unlimited | Frontend only |
| **MongoDB Atlas** | 512MB | Database |

**Total Cost: $0** if you use free tiers!

---

## 🔍 Testing Before Deployment

Test locally that everything works:

```powershell
# Build frontend
cd frontend
npm run build
cd ..

# Run production mode
python web_dashboard.py
```

Visit: http://localhost:5000

If it works locally, it will work deployed!

---

## 🆘 Troubleshooting

**Problem:** App crashes on deployment
- **Solution:** Check logs in platform dashboard
- Ensure all environment variables are set

**Problem:** Frontend shows but no data
- **Solution:** Check `/api/status` endpoint
- Verify MongoDB connection or SQLite permissions

**Problem:** Build fails
- **Solution:** Make sure `frontend/dist` exists
- Run `npm run build` in frontend folder first

---

## 📱 Quick Start (Fastest Method)

```powershell
# 1. Build frontend
cd frontend
npm run build
cd ..

# 2. Install Railway CLI
npm install -g @railway/cli

# 3. Deploy
railway login
railway init
railway up

# 4. Get your URL
railway open
```

Done! 🎉 Access from anywhere!

---

## 🔐 Security Notes

1. **Never commit `.env`** - Use platform environment variables
2. **Use MongoDB** - For production, avoid SQLite
3. **Enable CORS properly** - Already configured in `web_dashboard.py`
4. **API Keys** - Keep them secret in environment variables

---

Need help? Each platform has excellent documentation and support.

**Ready to deploy?** Start with Railway for the easiest experience!
