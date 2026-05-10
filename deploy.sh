#!/bin/bash
# Deploy script - Run this on the server to update and restart the bot

set -e

echo "🚀 Starting deployment..."

# Go to project directory
cd ~/telegram-ai-bot

# Stop the bot service
echo "🛑 Stopping bot service..."
sudo systemctl stop telegram-bot || true

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Start the bot service
echo "▶️ Starting bot service..."
sudo systemctl start telegram-bot

# Check status
echo "✅ Deployment complete! Checking status..."
sudo systemctl status telegram-bot --no-pager

echo "🎉 Bot is running! Check logs with: sudo journalctl -u telegram-bot -f"
