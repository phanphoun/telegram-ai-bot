# Telegram AI Bot

A hybrid Telegram bot that answers questions about Phoun (from CSV data) and general questions using Gemini AI.

## Features
- **Phoun Q&A**: Asks about Phoun's skills, job, education, hobbies, etc.
- **General AI**: Ask anything about coding, world events, movies, songs, games
- **Image Generation**: Use `/image <description>` to generate AI images

## Deploy to Render (Free)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-ai-bot.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up (free)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` config
5. Click **Deploy**

The bot will run 24/7 on Render's free tier.

## Local Development
```bash
pip install -r requirements.txt
python app.py
```
