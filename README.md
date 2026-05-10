# Telegram AI Bot

A hybrid Telegram bot that combines personal profile data with AI-powered responses. It answers questions about Phoun using CSV-based training data, while leveraging Google Gemini AI for general knowledge queries on coding, world events, movies, music, games, and more.

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Training Data System](#training-data-system)
- [Deployment Options](#deployment-options)
  - [Option 1: Render (Free Cloud Hosting)](#option-1-render-free-cloud-hosting)
  - [Option 2: Linux VPS / Remote Server](#option-2-linux-vps--remote-server)
  - [Option 3: Local Development](#option-3-local-development)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Features

- **Phoun Profile Q&A**: Ask about skills, job, education, hobbies, languages, and more
- **AI Training Context**: Gemini AI is trained with Phoun's profile (skills, projects, education, portfolio) and answers as Phoun would
- **Privacy Protection**: Sensitive fields (age, email, phone, address) are blocked
- **Gemini AI Integration**: Answers any general question with styled, emoji-rich responses
- **AI Image Generation**: Use `/image <description>` to generate images via Pollinations AI
- **Smart Response Formatting**: Topic-aware headers (coding, science, movies, games, etc.)
- **Auto-Split Long Messages**: Responses over 4000 chars are split into multiple messages
- **MarkdownV2 Support**: Bold text, emojis, and clean formatting throughout

## Architecture Overview

```
User Message
     |
     v
[Phoun Keyword Check] ----Yes----> [CSV Data Lookup] ---> [Styled Response]
     |                                        |
    No                                        |
     |                                        |
     v                                        |
[Gemini AI API Call] <------------------------+
     | (with Phoun's profile context)
     v
[Response Styling] ---> [Send to Telegram]
```

The bot uses a hybrid approach:
1. First checks if the question is about Phoun (using keyword matching)
2. If yes: reads from the CSV "training data" file
3. If no: sends the question to Gemini AI with Phoun's profile context (skills, projects, education, portfolio) so it answers as Phoun would

## Training Data System

### What is the Training Data?

The `phoun.csv` file acts as the bot's **knowledge base** for all personal/profile-related questions. It is loaded when the bot starts and stored in memory for fast lookups.

### CSV Structure

The CSV file uses a **header row** with field names, followed by **one data row** containing the values:

```csv
name,job_title,skills,github,linkedin,company,age,email,phone,address,city,country,school,position,level,experience,languages,hobbies,interests,bio
Phoun Phan,Full-Stack Software Developer,"Vue.js; React; TypeScript; Node.js; Tailwind CSS; MongoDB; PostgreSQL",https://github.com/phanphoun,https://linkedin.com/in/phanphoun,Freelance,22,phanphoun855@gmail.com,0987654321,Phnom Penh,Phnom Penh,Cambodia,Passerelles Numeriques Cambodia,Student,Intermediate,2+ years,"Khmer; English; French; Chinese","Coding; Gaming; Music; Reading","Web Development; AI; Open Source","Full-stack developer specializing in Vue..."
```

### How It Works

When you ask a question like **"what is your name?"**, the bot:

1. **Keyword Matching**: Checks if the question matches any keywords in `PHOUN_KEYWORDS`
   - Example: `"name"` keyword matches `"what is your name"`

2. **Field Lookup**: Finds the corresponding field in the CSV (`name`)

3. **Response Generation**: Returns a styled, conversational answer:
   ```
   👤 Name: Phoun Phan
   ```

### Supported Fields & Keywords

| Field | Keywords Detected | Privacy |
|-------|-------------------|---------|
| `name` | "name", "who are you" | Public |
| `job_title` | "job", "work", "career" | Public |
| `skills` | "skill", "programming", "vue", "react" | Public |
| `school` | "school", "university", "education" | Public |
| `city` | "city", "live", "location" | Public |
| `country` | "country", "nationality" | Public |
| `experience` | "experience", "how long" | Public |
| `hobbies` | "hobby", "gaming", "music", "reading" | Public |
| `languages` | "language", "speak" | Public |
| `github` | "github", "projects" | Public |
| `linkedin` | "linkedin", "profile" | Public |
| `bio` | "bio", "about me" | Public |
| `age` | "age", "old", "year" | **Protected** |
| `email` | "email", "contact" | **Protected** |
| `phone` | "phone", "number" | **Protected** |
| `address` | "address" | **Protected** |

### Customizing Your Training Data

To add or update your information:

1. Open `phoun.csv` in any spreadsheet app (Excel, Google Sheets) or text editor
2. Modify the values in the second row (keep the first row as headers)
3. Save the file
4. Commit and push to GitHub, then pull on your server

**Example - Adding new fields:**

Simply add a new column to the CSV header and data row:
```csv
name,job_title,favorite_color
Phoun Phan,Developer,Blue
```

Then add keywords in `app.py`:
```python
PHOUN_KEYWORDS = {
    ...existing keywords...,
    'favorite_color': ['favorite color', 'like color', 'color']
}
```

And add the response formatter in `get_phoun_answer()`:
```python
elif field == 'favorite_color':
    responses.append(f"🎨 *Favorite Color:* {value}")
```

---

## Deployment Options

### Prerequisites

Before deploying, you need:
1. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
2. **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey)
3. **Git** installed locally

---

### Option 1: Render (Free Cloud Hosting)

Render provides free 24/7 hosting for web services. This is the easiest option.

#### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-ai-bot.git
git push -u origin main
```

#### Step 2: Sign Up on Render

1. Go to [render.com](https://render.com)
2. Sign up using your GitHub account
3. Verify your email

#### Step 3: Create a New Web Service

1. Click **New** in the top-right corner
2. Select **Web Service**
3. Connect your GitHub account and authorize Render
4. Find and select your `telegram-ai-bot` repository

#### Step 4: Configure the Service

Render should auto-detect settings from `render.yaml`, but verify these:

| Setting | Value |
|---------|-------|
| **Name** | telegram-ai-bot |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Plan** | Free |

#### Step 5: Add Environment Variables

1. Scroll down to **Environment Variables**
2. Add:
   - `TELEGRAM_BOT_TOKEN` = your token from BotFather
   - `GEMINI_API_KEY` = your key from Google AI Studio
3. Click **Create Web Service**

#### Step 6: Deploy

Render will build and deploy automatically. You can view logs in the dashboard.

**Note:** Render free tier apps may spin down after 15 minutes of inactivity, but will restart on the next message (takes ~30 seconds).

---

### Option 2: Linux VPS / Remote Server

This option gives you full control and keeps the bot running 24/7.

#### Prerequisites
- A Linux server (Ubuntu/Debian preferred)
- SSH access to the server
- Python 3.8+ installed

#### Step 1: Connect to Your Server

```bash
ssh user@your-server-ip
```

#### Step 2: Install Python & Git

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

#### Step 3: Clone the Repository

```bash
cd ~
git clone https://github.com/phanphoun/telegram-ai-bot.git
cd telegram-ai-bot
```

#### Step 4: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 6: Set Environment Variables

**Option A - Temporary (for testing):**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export GEMINI_API_KEY="your_key_here"
```

**Option B - Permanent (recommended):**
```bash
nano ~/.bashrc
```

Add these lines at the end of the file:
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export GEMINI_API_KEY="your_key_here"
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

Reload the file:
```bash
source ~/.bashrc
```

#### Step 7: Test the Bot

```bash
python app.py
```

You should see:
```
Loaded Phoun data: {...}
Bot is running...
```

Test it in Telegram, then stop it with `Ctrl+C`.

#### Step 8: Run 24/7 with nohup

```bash
nohup python app.py > bot.log 2>&1 &
```

This runs the bot in the background even after you disconnect SSH.

**Check if it's running:**
```bash
ps aux | grep "python app.py"
```

**View logs:**
```bash
tail -f bot.log
```

**Stop the bot:**
```bash
pkill -f "python app.py"
```

#### Step 9 (Optional): Auto-Start on Boot with systemd

Create a service file:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Paste this content:
```ini
[Unit]
Description=Telegram AI Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/telegram-ai-bot
ExecStart=/home/your_username/telegram-ai-bot/venv/bin/python /home/your_username/telegram-ai-bot/app.py
Restart=always
RestartSec=10
Environment=TELEGRAM_BOT_TOKEN=your_token_here
Environment=GEMINI_API_KEY=your_key_here

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `your_username` with your actual Linux username.

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

**Check status:**
```bash
sudo systemctl status telegram-bot
```

---

### Option 3: Local Development

For testing and development on your own machine.

#### Step 1: Install Python

Download Python 3.8+ from [python.org](https://python.org) if not already installed.

#### Step 2: Clone the Repository

```bash
git clone https://github.com/phanphoun/telegram-ai-bot.git
cd telegram-ai-bot
```

#### Step 3: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 5: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_token_here"
$env:GEMINI_API_KEY = "your_key_here"
```

**macOS/Linux:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export GEMINI_API_KEY="your_key_here"
```

#### Step 6: Run the Bot

```bash
python app.py
```

**Note:** When running locally, make sure no other instance (like on Render) is active, or you'll get a 409 Conflict error.

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

**Security Tip:** Never commit API keys to GitHub. Always use environment variables.

---

## Project Structure

```
telegram-ai-bot/
├── app.py              # Main bot application
├── phoun.csv           # Training data (Phoun's profile)
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### File Descriptions

- **`app.py`** (270+ lines)
  - Environment variable loading
  - CSV data loading (`load_phoun_data()`)
  - Keyword matching (`is_about_phoun()`, `PHOUN_KEYWORDS`)
  - Response generation (`get_phoun_answer()`)
  - Gemini API integration
  - Image generation via Pollinations
  - Markdown escaping and text splitting
  - Telegram message handlers

- **`phoun.csv`**
  - Single-row knowledge base
  - 20+ fields of personal/professional data
  - Loaded into memory at startup

- **`requirements.txt`**
  - `pyTelegramBotAPI` - Telegram Bot framework
  - `requests` - HTTP library for API calls

- **`render.yaml`**
  - Render.com deployment configuration
  - Specifies build/start commands
  - Declares environment variables (sync: false means manual entry)

---

## Customization

### Changing the Bot's Personality

Edit the `style_gemini_response()` function in `app.py` to change:
- Header emojis and text
- Footer messages
- Topic detection keywords

### Adding New Commands

Add a new handler:
```python
@bot.message_handler(commands=['mycommand'])
def handle_mycommand(message):
    bot.reply_to(message, "Your custom response here!")
```

### Updating Training Data

1. Edit `phoun.csv`
2. Add new columns/fields as needed
3. Update `PHOUN_KEYWORDS` in `app.py`
4. Add response formatting in `get_phoun_answer()`
5. Commit, push, and redeploy

---

## Troubleshooting

### Error: "Conflict: terminated by other getUpdates request"
**Cause:** Multiple bot instances running with the same token.
**Fix:** Stop the other instance. Only one bot can poll at a time.

### Error: "API key not valid" (403)
**Cause:** Gemini API key was revoked (leaked) or incorrect.
**Fix:** Generate a new key at [Google AI Studio](https://aistudio.google.com/app/apikey). Never commit keys to GitHub.

### Error: "message is too long" (400)
**Fix:** Already handled by `send_long_text()` which splits messages automatically.

### Bot not responding
1. Check if it's running: `ps aux | grep "python app.py"`
2. Check logs: `tail -f bot.log`
3. Verify environment variables are set correctly
4. Ensure no other instance is running

### Render deployment fails
1. Check Render dashboard logs for build errors
2. Verify `render.yaml` is correct
3. Make sure environment variables are set in Render dashboard
4. Ensure `requirements.txt` has all dependencies

---

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions, open an issue on GitHub or reach out on Telegram.
