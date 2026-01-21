# Railway Deployment Guide

## Environment Variables Required on Railway

Set these environment variables in your Railway project settings:

### Required:
```
MONGO_URI=mongodb+srv://your-username:your-password@cluster.mongodb.net/forex_engine?retryWrites=true&w=majority
PORT=5000
```

### API Keys (Set your actual keys):
```
API_KEY_FMP=your_fmp_key
API_KEY_NEWSAPI=your_newsapi_key
API_KEY_TWELVEDATA=your_twelvedata_key
API_KEY_ALPHAVANTAGE=your_alphavantage_key
API_KEY_TAAPI=your_taapi_key
API_KEY_FINNHUB=your_finnhub_key
API_KEY_POLYGON=your_polygon_key
```

## Deployment Steps

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Update CORS and deployment config"
   git push origin main
   ```

2. **In Railway Dashboard:**
   - Connect your GitHub repository
   - Add all environment variables listed above
   - Deploy!

3. **Test your deployment:**
   - Health check: `https://your-app.railway.app/api/health`
   - Status: `https://your-app.railway.app/api/status`
   - Signals: `https://your-app.railway.app/api/signals`

## CORS Configuration

The backend is configured to accept requests from:
- `https://trading-engine-frontend-yhhs.vercel.app`
- `https://*.vercel.app` (any Vercel subdomain)
- Local development servers

## Troubleshooting

### 502 Bad Gateway
- Check that all environment variables are set
- Verify MongoDB URI is correct and accessible
- Check Railway logs for errors

### CORS Errors
- Verify your frontend URL matches the configured origins
- Check that requests include proper headers

### Database Connection Issues
- Ensure MONGO_URI is set correctly
- Whitelist Railway's IP addresses in MongoDB Atlas (or use 0.0.0.0/0)
