#!/bin/bash
set -e

# Senior Dental AI Chatbot - Deployment Script
# This script sets up the chatbot service on Ubuntu 24.04

APP_DIR="/opt/senior-dental-ai-chatbot"
SERVICE_USER="www-data"
PYTHON_VERSION="3.11"

echo "======================================"
echo "Senior Dental AI Chatbot Deployment"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Check Python version
if ! command -v python${PYTHON_VERSION} &> /dev/null; then
    echo "Python ${PYTHON_VERSION} not found. Installing..."
    apt update
    apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev
fi

# Create application directory
echo "=== Creating application directory ==="
mkdir -p ${APP_DIR}
chown ${SERVICE_USER}:${SERVICE_USER} ${APP_DIR}

# Copy application files (if not already deployed via git)
if [ ! -f "${APP_DIR}/requirements.txt" ]; then
    echo "=== Copying application files ==="
    cp -r ./* ${APP_DIR}/
    chown -R ${SERVICE_USER}:${SERVICE_USER} ${APP_DIR}
fi

# Create virtual environment
echo "=== Creating virtual environment ==="
cd ${APP_DIR}
python${PYTHON_VERSION} -m venv venv
chown -R ${SERVICE_USER}:${SERVICE_USER} venv

# Install dependencies
echo "=== Installing dependencies ==="
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create HuggingFace cache directory
echo "=== Creating model cache directory ==="
mkdir -p ${APP_DIR}/.cache/huggingface
chown -R ${SERVICE_USER}:${SERVICE_USER} ${APP_DIR}/.cache

# Create .env file if not exists
if [ ! -f "${APP_DIR}/.env" ]; then
    echo "=== Creating .env file ==="
    cp ${APP_DIR}/.env.example ${APP_DIR}/.env
    echo "IMPORTANT: Edit ${APP_DIR}/.env with your configuration"
fi

# Create systemd service file
echo "=== Creating systemd service ==="
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

# Reload systemd and enable service
echo "=== Enabling and starting service ==="
systemctl daemon-reload
systemctl enable chatbot
systemctl start chatbot

# Wait for service to start
echo "=== Waiting for service to initialize ==="
sleep 15

# Check service status
echo "=== Service status ==="
systemctl status chatbot --no-pager

# Health check
echo "=== Running health check ==="
for i in {1..12}; do
    if curl -sf http://localhost:8001/api/v1/health/ready > /dev/null 2>&1; then
        echo "Health check PASSED!"
        curl -s http://localhost:8001/api/v1/health | python3 -m json.tool
        break
    fi
    if [ $i -eq 12 ]; then
        echo "Health check FAILED after 12 attempts"
        echo "=== Recent logs ==="
        journalctl -u chatbot --no-pager -n 100
        exit 1
    fi
    echo "Waiting for service to be ready... (attempt $i/12)"
    sleep 10
done

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Service URL: http://localhost:8001"
echo "Health Check: http://localhost:8001/api/v1/health"
echo ""
echo "Commands:"
echo "  Status:  sudo systemctl status chatbot"
echo "  Logs:    sudo journalctl -u chatbot -f"
echo "  Restart: sudo systemctl restart chatbot"
echo "  Stop:    sudo systemctl stop chatbot"
echo ""
