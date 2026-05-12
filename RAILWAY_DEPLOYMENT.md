# 🚂 Railway Deployment Guide

## Step-by-Step Instructions

### 1. Prepare Your Code

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Gate.io P2P Monitor v1.0"

# Create GitHub repository and push
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/gateio-p2p-monitor.git
git push -u origin main
```

### 2. Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub
3. Verify your email

### 3. Deploy Backend Service

1. **New Project**: Click "New" → "Project"
2. **Deploy from GitHub**: Select "Deploy from GitHub repo"
3. **Select Repository**: Choose `gateio-p2p-monitor`
4. **Service Detection**: Railway will auto-detect the Dockerfile

### 4. Configure Environment Variables

Click on your service → "Variables" tab → "New Variable":

```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
DEFAULT_TRADER_NAME=YourExactGateIOTraderName
DEFAULT_MIN_QUANTITY=100
POLLING_INTERVAL=10
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. Deploy Frontend (Optional)

If you want a separate frontend service:

1. In the same project, click "New" → "Service"
2. Select "GitHub Repo" again
3. In service settings, set Root Directory to `frontend`
4. Add variable: `NEXT_PUBLIC_API_URL=https://your-backend-service.railway.app`

### 6. Generate Domain

1. Click on backend service
2. Go to "Settings" → "Domains"
3. Click "Generate Domain"
4. Your API is now at `https://your-domain.railway.app`

### 7. Verify Deployment

```bash
# Test health endpoint
curl https://your-domain.railway.app/api/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00","monitor_status":"Stopped"}
```

### 8. Configure Telegram Webhook (Optional)

If using webhooks instead of polling:

```bash
curl -F "url=https://your-domain.railway.app/api/telegram-webhook" \
  https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

## 🔄 Auto-Deploy on Git Push

Railway automatically redeploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update settings"
git push origin main
# Railway will auto-deploy!
```

## 📊 Monitoring on Railway

### View Logs
```bash
# Using Railway CLI
railway logs

# Or in Dashboard: Service → Deployments → View Logs
```

### Metrics
- CPU/RAM: Service → Metrics
- Requests: Service → Usage

## 🛠️ Troubleshooting

### Issue: "Build Failed"
**Solution**: Check Dockerfile syntax, ensure requirements.txt has no conflicts

### Issue: "Cannot connect to Telegram"
**Solution**: Verify TELEGRAM_BOT_TOKEN is correct (test with curl)

### Issue: "No notifications sent"
**Solution**: 
1. Check if your trader name is EXACT
2. Verify you're monitoring SELL ads (not BUY)
3. Check logs for "Could not find your ad"

### Issue: "CORS errors in browser"
**Solution**: Ensure `allow_origins=["*"]` in backend/main.py or set specific origin

## 💰 Railway Pricing

- **Free Tier**: $5/month credit, 512MB RAM, shared CPU
- **Starter**: $5/month, 1GB RAM
- **Pro**: $10/month, 2GB RAM

This app runs comfortably on the Free Tier for personal use.

## 🔒 Security Best Practices

1. **Never commit .env files**
2. **Use Railway Variables** for secrets (not hardcoded)
3. **Restrict CORS** in production:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```
4. **Enable Railway Authentication** for dashboard access

## 📞 Getting Help

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Telegram Bot API: https://core.telegram.org/bots/api
