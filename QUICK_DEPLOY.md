# ⚡ Quick Deployment Guide

## Fastest Way to Deploy (5 Minutes)

### Step 1: Deploy Backend to Railway

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy (from project root)
cd c:\Users\rajpa\Desktop\Engine
railway init
railway up

# Get your URL
railway open
```

**Copy the URL shown (e.g., `https://forex-engine-production.up.railway.app`)**

### Step 2: Deploy Frontend to Vercel

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy
cd c:\Users\rajpa\Desktop\Engine\frontend
vercel

# Follow prompts (accept defaults)
```

### Step 3: Connect Frontend to Backend

```powershell
# Add environment variable
vercel env add VITE_API_URL

# Paste your Railway URL from Step 1
# Select: Production + Preview

# Redeploy
vercel --prod
```

### Done! 🎉

Your app is live at the URL shown by Vercel!

---

## What You Get

- ✅ **Frontend**: `https://your-app.vercel.app` - Access from anywhere
- ✅ **Backend**: Runs on Railway 24/7
- ✅ **Database**: MongoDB for persistent data
- ✅ **Cost**: $0 (free tiers)
- ✅ **Updates**: `git push` to deploy (if using GitHub)

---

## Environment Variables to Set

### In Railway (Backend)
```
FMP_API_KEY=your_key
NEWS_API_KEY=your_key
TWELVE_DATA_KEY=your_key
ALPHA_VANTAGE_KEY=your_key
TAAPI_KEY=your_key
FINNHUB_API_KEY=your_key
POLYGON_API_KEY=your_key
MONGO_URI=mongodb+srv://...  (optional but recommended)
```

### In Vercel (Frontend)
```
VITE_API_URL=https://your-railway-url.com
```

---

## Testing

**Test Backend:**
```
https://your-railway-url.com/api/status
```

**Test Frontend:**
```
https://your-app.vercel.app
```

---

## Troubleshooting

**No data showing?**
- Check `VITE_API_URL` is set in Vercel
- Check Railway logs: `railway logs`
- Ensure backend is running: Visit `/api/status`

**Build failed?**
- Run `npm run build` locally first
- Check error in Vercel deployment logs
- Ensure all dependencies in `package.json`

---

## Alternative: Single Platform Deployment

If you want everything in one place:

### Railway Only (Frontend + Backend)

Railway can serve both:
1. Build frontend: `cd frontend && npm run build`
2. Deploy: `railway up`
3. Flask serves frontend from `dist/` folder

No separate Vercel needed, but less optimized for frontend.

---

## Next Steps

1. **Add MongoDB**: Get free cluster at mongodb.com/cloud/atlas
2. **Custom Domain**: Add in Vercel settings
3. **Monitor**: Check Railway/Vercel dashboards
4. **Scale**: Upgrade plans when needed

Read `VERCEL_DEPLOYMENT.md` for detailed guide.
