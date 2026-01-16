# AI Chatbot Deployment Guide

This guide covers deploying the Senior Dental AI Chatbot to production server.

## Server Requirements

- **OS**: Ubuntu 24.04
- **RAM**: 8GB minimum (16GB recommended for faster model loading)
- **CPU**: 4+ cores
- **Storage**: 20GB+ free space (for models)
- **Python**: 3.11+

## Deployment Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SSH to Server                                                │
│         │                                                        │
│         ▼                                                        │
│  2. Install Python 3.11                                          │
│         │                                                        │
│         ▼                                                        │
│  3. Clone Repository to /opt/senior-dental-ai-chatbot           │
│         │                                                        │
│         ▼                                                        │
│  4. Create Virtual Environment                                   │
│         │                                                        │
│         ▼                                                        │
│  5. Install Dependencies                                         │
│         │                                                        │
│         ▼                                                        │
│  6. Configure Environment (.env)                                 │
│         │                                                        │
│         ▼                                                        │
│  7. Create systemd Service                                       │
│         │                                                        │
│         ▼                                                        │
│  8. Start Service & Verify Health                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Deployment

### Step 1: Connect to Server

```bash
ssh -i ~/.ssh/id_ed25519 root@46.224.222.138
```

### Step 2: Install Python 3.11

```bash
# Update package list
apt update

# Install Python 3.11 and dependencies
apt install -y python3.11 python3.11-venv python3.11-dev build-essential
```

### Step 3: Create Application Directory

```bash
# Create the application directory
mkdir -p /opt/senior-dental-ai-chatbot
cd /opt/senior-dental-ai-chatbot
```

### Step 4: Transfer Files (Option A: Git Clone)

If you've pushed to GitHub:
```bash
git clone https://github.com/YOUR_ORG/senior-dental-ai-chatbot.git .
```

**Option B: SCP Transfer (without GitHub)**
From your local machine:
```bash
cd /Users/ringstechnology/Desktop/senior-dental-ai-chatbot
scp -i ~/.ssh/id_ed25519 -r ./* root@46.224.222.138:/opt/senior-dental-ai-chatbot/
```

### Step 5: Create Virtual Environment

```bash
cd /opt/senior-dental-ai-chatbot

# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 6: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies (this takes 5-10 minutes)
pip install -r requirements.txt
```

### Step 7: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Key settings to verify:**
```ini
API_HOST=127.0.0.1    # Bind to localhost only!
API_PORT=8001
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DEVICE=cpu            # Or 'cuda' if GPU available
```

### Step 8: Create HuggingFace Cache Directory

```bash
mkdir -p /opt/senior-dental-ai-chatbot/.cache/huggingface
chown -R www-data:www-data /opt/senior-dental-ai-chatbot
```

### Step 9: Create systemd Service

```bash
cat > /etc/systemd/system/chatbot.service << 'EOF'
[Unit]
Description=Senior Dental AI Chatbot
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/senior-dental-ai-chatbot
Environment="PATH=/opt/senior-dental-ai-chatbot/venv/bin:/usr/local/bin:/usr/bin"
Environment="HF_HOME=/opt/senior-dental-ai-chatbot/.cache/huggingface"
Environment="TRANSFORMERS_CACHE=/opt/senior-dental-ai-chatbot/.cache/huggingface"
ExecStart=/opt/senior-dental-ai-chatbot/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 1
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/senior-dental-ai-chatbot

# Resource limits
MemoryMax=8G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
EOF
```

### Step 10: Enable and Start Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable chatbot

# Start the service
systemctl start chatbot

# Check status
systemctl status chatbot
```

### Step 11: Verify Deployment

```bash
# Wait for model to load (1-3 minutes on first start)
sleep 120

# Check health endpoint
curl http://localhost:8001/api/v1/health
curl http://localhost:8001/api/v1/health/ready

# Test chat endpoint
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ByteDent?"}'
```

### Step 12: View Logs

```bash
# Follow logs in real-time
journalctl -u chatbot -f

# View last 100 lines
journalctl -u chatbot -n 100
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
journalctl -u chatbot -n 200 --no-pager

# Common issues:
# 1. Permission denied - fix ownership
chown -R www-data:www-data /opt/senior-dental-ai-chatbot

# 2. Memory issues - check available RAM
free -h

# 3. Port already in use
lsof -i :8001
```

### Model Loading Slow

First startup downloads models (~6GB). Subsequent starts are faster.

```bash
# Check download progress
ls -la /opt/senior-dental-ai-chatbot/.cache/huggingface/
```

### Out of Memory

Edit the service file to reduce workers:
```bash
# Edit service
nano /etc/systemd/system/chatbot.service

# Change workers from 1 to 1 (already set)
# Reduce MemoryMax if needed

# Reload and restart
systemctl daemon-reload
systemctl restart chatbot
```

## Useful Commands

```bash
# Service management
sudo systemctl start chatbot
sudo systemctl stop chatbot
sudo systemctl restart chatbot
sudo systemctl status chatbot

# Logs
sudo journalctl -u chatbot -f          # Follow logs
sudo journalctl -u chatbot -n 100      # Last 100 lines
sudo journalctl -u chatbot --since "1 hour ago"

# Health checks
curl http://localhost:8001/api/v1/health
curl http://localhost:8001/api/v1/health/ready
curl http://localhost:8001/api/v1/metrics
```

## Security Notes

1. **The chatbot binds to localhost (127.0.0.1) only** - it's not exposed to the internet
2. The Laravel backend will communicate with it via `http://localhost:8001`
3. UFW firewall should NOT have port 8001 open
4. Service runs as `www-data` user (non-root)

## Next Steps

After the chatbot is running:
1. Deploy the Laravel backend
2. Configure Laravel's `.env` with `CHATBOT_SERVICE_URL=http://localhost:8001`
3. The Laravel backend will handle all external requests and proxy chat requests internally
