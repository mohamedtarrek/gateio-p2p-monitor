# 🔔 Gate.io P2P Monitor

Real-time P2P price monitoring application for Gate.io USDT/EGP trading with **Instapay** payment method. Automatically sends Telegram notifications when competitors list higher prices than yours.

## ✨ Features

- **Real-time Monitoring**: Checks Gate.io P2P marketplace every 5-300 seconds (configurable)
- **Smart Notifications**: Only alerts when competitors have higher prices AND sufficient quantity
- **Duplicate Prevention**: Won't spam you with the same price notification
- **Instant Updates**: Click "Save/Update" to apply new settings without restarting
- **Full Control**: Start/Stop monitoring with one click
- **Detailed History**: View all sent notifications with expandable details
- **Error Resilience**: Continues running even if individual checks fail
- **Production Ready**: Optimized for Railway deployment

## 🏗️ Architecture

```
┌─────────────┐      HTTP/REST      ┌──────────────┐
│   Next.js   │ ◄─────────────────► │   FastAPI    │
│  Frontend   │                     │   Backend    │
│  (Port 3000)│                     │  (Port 8000) │
└─────────────┘                     └──────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              ▼            ▼            ▼
                        ┌─────────┐  ┌──────────┐  ┌──────────┐
                        │ Gate.io │  │ Telegram │  │  Memory  │
                        │   API   │  │   Bot    │  │  State   │
                        └─────────┘  └──────────┘  └──────────┘
```

## 📁 Project Structure

```
gateio-p2p-monitor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── models.py            # Pydantic data models
│   │   ├── services/
│   │   │   ├── gateio_scraper.py   # Gate.io P2P API client
│   │   │   ├── telegram_service.py # Telegram Bot API integration
│   │   │   └── monitor_service.py  # Core monitoring engine
│   │   ├── routers/
│   │   │   └── api.py           # REST API endpoints
│   │   └── utils/
│   │       └── logger.py        # Structured logging
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard page
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Tailwind styles
│   ├── components/
│   │   ├── MonitorDashboard.tsx # Main orchestration
│   │   ├── SettingsForm.tsx     # Configuration form
│   │   ├── StatusPanel.tsx      # Status display
│   │   └── NotificationLog.tsx  # History viewer
│   ├── lib/
│   │   └── api.ts               # API client
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
├── docker-compose.yml           # Local development
├── railway.toml                 # Railway deployment config
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram Chat ID

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/gateio-p2p-monitor.git
cd gateio-p2p-monitor
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

**`.env` Configuration:**

```env
# Required: Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Your Gate.io trader name (exactly as shown on P2P page)
DEFAULT_TRADER_NAME=YourTraderName

# Minimum competitor quantity to trigger alerts
DEFAULT_MIN_QUANTITY=100

# How often to check prices (seconds, minimum 5)
POLLING_INTERVAL=10

# Server settings
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Get your Telegram Chat ID:**
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your Chat ID (e.g., `123456789`)
3. For groups, add the bot to the group and use [@RawDataBot](https://t.me/RawDataBot)

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# For local development, create .env.local:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Build for production
npm run build
```

### 4. Run Locally

**Option A: Using Python directly**

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option B: Using Docker Compose**

```bash
# From project root
docker-compose up --build
```

Access the application at `http://localhost:3000`

## 🚂 Deploy to Railway

Railway is the recommended platform for hosting this application.

### Step 1: Prepare Your Repository

Ensure your code is pushed to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/gateio-p2p-monitor.git
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `gateio-p2p-monitor` repository
4. Railway will detect the `railway.toml` and `Dockerfile`

### Step 3: Configure Environment Variables

1. In your Railway project, go to the service settings
2. Click **"Variables"** tab
3. Add the following variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | `123456:ABC...` | From @BotFather |
| `TELEGRAM_CHAT_ID` | `123456789` | Your Telegram Chat ID |
| `DEFAULT_TRADER_NAME` | `YourName` | Your Gate.io trader name |
| `DEFAULT_MIN_QUANTITY` | `100` | Minimum USDT quantity |
| `POLLING_INTERVAL` | `10` | Check interval (seconds) |
| `ENVIRONMENT` | `production` | Production mode |
| `LOG_LEVEL` | `INFO` | Logging level |

### Step 4: Deploy

1. Railway will automatically deploy when you push to GitHub
2. Or click **"Deploy"** in the dashboard
3. Your app will be available at `https://your-project.railway.app`

### Step 5: Add Custom Domain (Optional)

1. In Railway service settings, click **"Settings"** → **"Domains"**
2. Click **"Generate Domain"** or add your custom domain

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/settings` | Update monitor settings |
| `GET` | `/api/status` | Get system status |
| `POST` | `/api/start` | Start monitoring |
| `POST` | `/api/stop` | Stop monitoring |
| `POST` | `/api/test-telegram` | Send test message |
| `GET` | `/api/history` | Get notification history |
| `DELETE` | `/api/history` | Clear history |
| `GET` | `/api/health` | Health check |

### Example: Update Settings via API

```bash
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "trader_name": "MyTrader",
    "min_quantity": 150,
    "telegram_bot_token": "123456:ABC...",
    "telegram_chat_id": "123456789",
    "polling_interval": 15,
    "payment_method": "Instapay"
  }'
```

## 🔔 Notification Logic

The monitor sends a Telegram notification when **ALL** these conditions are met:

1. ✅ Payment method is **Instapay** (or your configured method)
2. ✅ Currency is **EGP**
3. ✅ Competitor's price is **higher** than your price
4. ✅ Competitor's **max quantity** ≥ your configured minimum
5. ✅ You haven't been notified for this exact price recently

### Telegram Message Format

```
🔔 Gate.io P2P Price Alert

Competitor: [Trader Name]
Competitor Price: [XX.XX EGP]
Your Price: [XX.XX EGP]
Difference: [+X.XX EGP] 🟢
Max Quantity: [XXX.XX USDT]
Payment: Instapay

🔗 Ad Link: [View on Gate.io]

⏰ 2024-01-15 14:30:45 UTC
```

## 🔧 Configuration Options

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| `trader_name` | - | Any string | Your exact Gate.io display name |
| `min_quantity` | 100 | ≥ 1 | Minimum competitor max quantity |
| `polling_interval` | 10 | 5-300 | Seconds between price checks |
| `payment_method` | Instapay | Instapay, Vodafone Cash, Bank Transfer | Filter payment methods |
| `telegram_bot_token` | - | Valid bot token | From @BotFather |
| `telegram_chat_id` | - | Valid chat ID | Your Telegram chat ID |

## 🛡️ Error Handling

The application is designed to be resilient:

- **Network errors**: Retries after 5 seconds, keeps running
- **Invalid Telegram token**: Detected on settings update, prevents start
- **Gate.io API down**: Logs error, continues polling
- **Missing trader ad**: Logs warning, retries next cycle
- **Memory leaks**: Notification history auto-limited to 1000 entries

## 📝 Logging

Structured logs are output to stdout in this format:

```
2024-01-15 14:30:45 | INFO     | app.services.monitor_service | Monitor started successfully
2024-01-15 14:30:55 | INFO     | app.services.gateio_scraper | Successfully fetched 15 advertisements
2024-01-15 14:31:00 | INFO     | app.services.telegram_service | Telegram notification sent: message_id=456
```

View logs on Railway:
```bash
railway logs
```

## 🔮 Future Enhancements

- [ ] Support multiple trader profiles
- [ ] Add more payment methods (Vodafone Cash, Etisalat, etc.)
- [ ] Price trend charts and analytics
- [ ] WebSocket for real-time frontend updates
- [ ] Multi-currency support (USD, EUR, etc.)
- [ ] Database persistence for long-term history
- [ ] Alert thresholds (e.g., only if difference > 0.5 EGP)

## 📄 License

MIT License - feel free to use for personal or commercial purposes.

## 🆘 Support

If you encounter issues:

1. Check logs: `railway logs` or backend console
2. Verify Telegram token with `curl` test
3. Ensure your Gate.io trader name is **exact**
4. Check that you're looking at **Sell** ads (not Buy)
5. Open an issue on GitHub with logs attached

---

**Built with ❤️ for the Egyptian crypto trading community**
