# ⚡ Quick Reference Card

## Start Development
```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Frontend (new terminal)
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev

# 3. Open http://localhost:3000
```

## API Quick Calls
```bash
# Health check
curl http://localhost:8000/api/health

# Update settings
curl -X POST http://localhost:8000/api/settings   -H "Content-Type: application/json"   -d '{
    "trader_name": "MyTrader",
    "min_quantity": 100,
    "telegram_bot_token": "YOUR_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "polling_interval": 10,
    "payment_method": "Instapay"
  }'

# Start monitoring
curl -X POST http://localhost:8000/api/start

# Stop monitoring
curl -X POST http://localhost:8000/api/stop

# Check status
curl http://localhost:8000/api/status

# Test Telegram
curl -X POST http://localhost:8000/api/test-telegram   -H "Content-Type: application/json"   -d '{"trader_name":"test","min_quantity":1,"telegram_bot_token":"TOKEN","telegram_chat_id":"ID","polling_interval":10,"payment_method":"Instapay"}'
```

## Telegram Setup
1. Message @BotFather → /newbot → copy token
2. Message @userinfobot → copy chat ID
3. Test with: curl https://api.telegram.org/bot<TOKEN>/getMe

## Railway Deploy
1. Push to GitHub
2. Railway Dashboard → New Project → GitHub Repo
3. Add Environment Variables
4. Generate Domain
5. Done!

## File Purposes
| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI server entry |
| `backend/app/services/monitor_service.py` | Core monitoring loop |
| `backend/app/services/gateio_scraper.py` | Gate.io API client |
| `backend/app/services/telegram_service.py` | Telegram notifications |
| `frontend/components/MonitorDashboard.tsx` | Main UI |
| `railway.toml` | Railway deployment config |

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| TELEGRAM_BOT_TOKEN | Yes | From @BotFather |
| TELEGRAM_CHAT_ID | Yes | From @userinfobot |
| DEFAULT_TRADER_NAME | Yes | Your Gate.io name |
| DEFAULT_MIN_QUANTITY | No | Default: 100 |
| POLLING_INTERVAL | No | Default: 10s |
| PORT | No | Default: 8000 |
