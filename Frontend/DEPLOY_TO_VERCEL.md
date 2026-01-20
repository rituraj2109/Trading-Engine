# 🚀 Your Frontend Deployment Steps

Your frontend repository is ready at:
**https://github.com/rituraj2109/Trading-Engine-Frontend**

---

## ✅ Already Done

✅ Frontend code pushed to GitHub
✅ Vercel configuration added (`vercel.json`)
✅ API configuration ready (`src/config.js`)
✅ Environment variable example created (`.env.example`)

---

## 🎯 Deploy to Vercel (2 Methods)

### Method 1: Via Vercel Website (Easiest)

1. **Go to Vercel**
   - Visit: https://vercel.com
   - Sign up/Login with GitHub

2. **Import Project**
   - Click "New Project"
   - Select **"Trading-Engine-Frontend"** repository
   - Click "Import"

3. **Configure Project**
   ```
   Framework Preset: Vite
   Root Directory: ./
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```
   (Vercel auto-detects these, just verify)

4. **Add Environment Variable**
   - Before deploying, click "Environment Variables"
   - Add:
     ```
     Name: VITE_API_URL
     Value: (leave empty for now, add backend URL later)
     ```
   - Click "Deploy"

5. **Get Your URL**
   - Wait for deployment (1-2 minutes)
   - Copy URL: `https://trading-engine-frontend.vercel.app`

---

### Method 2: Via Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend repo
cd c:\Users\rajpa\Desktop\Engine\frontend

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Scope: (your account)
# - Link to existing project? No
# - Project name: trading-engine-frontend
# - Directory: ./
# - Override settings? No

# Your app is now deployed!
```

---

## 🔗 Connect to Backend

### Option A: Deploy Backend First (Recommended)

1. **Deploy Backend to Railway**
   ```powershell
   # In project root (not frontend folder)
   cd c:\Users\rajpa\Desktop\Engine
   
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   
   # Get URL
   railway open
   ```

2. **Copy Backend URL**
   - Example: `https://forex-engine-production-xxxx.up.railway.app`

3. **Add to Vercel**
   - Go to Vercel Dashboard → Your Project
   - Settings → Environment Variables
   - Add new:
     ```
     VITE_API_URL = https://your-backend-url.railway.app
     ```
   - Redeploy (Deployments → Click "..." → Redeploy)

### Option B: Use Local Backend (Testing)

For testing only:
```
VITE_API_URL = http://localhost:5000
```
(This won't work for remote access)

---

## 📋 Backend Environment Variables (Railway/Render)

When deploying backend, add these in Railway dashboard:

```
FMP_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
TWELVE_DATA_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_key_here
TAAPI_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/forex
```

---

## 🧪 Testing Your Deployment

### 1. Test Backend Separately
```
https://your-backend-url.com/api/status
```
Should return: `{"status": "running", "version": "1.2", ...}`

### 2. Test Frontend
- Visit: `https://trading-engine-frontend.vercel.app`
- Should see the dashboard
- Should load signals and news (if backend is running)

### 3. Test API Connection
- Open browser console (F12)
- Check Network tab
- Should see API calls to your backend URL

---

## 🔧 Troubleshooting

**Frontend builds but shows no data:**
- Check if `VITE_API_URL` is set in Vercel
- Verify backend is running: visit `/api/status`
- Check browser console for CORS errors

**Build fails on Vercel:**
- Check build logs in Vercel dashboard
- Ensure `package.json` has all dependencies
- Try building locally: `npm run build`

**CORS errors:**
- Backend has CORS enabled (already done)
- Make sure `VITE_API_URL` doesn't have trailing slash
- Example: ✅ `https://api.com` ❌ `https://api.com/`

---

## 🎨 Custom Domain (Optional)

1. Go to Vercel → Your Project → Settings → Domains
2. Add your domain (e.g., `forex-engine.com`)
3. Update DNS records (Vercel shows instructions)
4. Done!

---

## 🔄 Update Your App

### Via GitHub (Automatic)
```powershell
cd c:\Users\rajpa\Desktop\Engine\frontend
git add .
git commit -m "Updated features"
git push
```
Vercel auto-deploys on every push!

### Via Vercel CLI
```powershell
cd c:\Users\rajpa\Desktop\Engine\frontend
vercel --prod
```

---

## 📱 What You Get

After full deployment:

✅ **Frontend**: `https://trading-engine-frontend.vercel.app`
  - Fast, global CDN
  - Auto-updates on git push
  - Free SSL certificate

✅ **Backend**: `https://your-app.railway.app`
  - 24/7 running
  - Trading engine active
  - API endpoints

✅ **Access from anywhere**:
  - Desktop browser
  - Mobile phone
  - Tablet
  - Any device with internet!

✅ **Cost**: $0/month (with free tiers)

---

## 🚀 Next Steps

1. **Now**: Deploy backend to Railway
   ```powershell
   cd c:\Users\rajpa\Desktop\Engine
   railway login
   railway up
   ```

2. **Then**: Add backend URL to Vercel environment variables

3. **Finally**: Visit your Vercel URL and check signals!

---

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Your Frontend Repo**: https://github.com/rituraj2109/Trading-Engine-Frontend

---

**Ready to deploy?** Start with backend deployment, then connect it to your frontend!

Happy trading! 📈
