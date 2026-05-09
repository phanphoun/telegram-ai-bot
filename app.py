import os
import telebot
import requests
import csv
import re

# Get API keys from environment variables
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

bot = telebot.TeleBot(API_TOKEN)

# Load Phoun's data from CSV
def load_phoun_data():
    data = {}
    try:
        with open('phoun.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data = row
                break
        print(f"Loaded Phoun data: {data}")
    except Exception as e:
        print(f"Error loading phoun.csv: {e}")
    return data

PHOUN_DATA = load_phoun_data()

# Keyword mapping for Phoun-related questions
PHOUN_KEYWORDS = {
    'name': ['name', 'who are you', 'who is phoun', 'about phoun', 'introduce phoun'],
    'job_title': ['job', 'work', 'occupation', 'career', 'profession', 'do for a living', 'what do you do'],
    'skills': ['skill', 'tech stack', 'technology', 'programming', 'code', 'framework', 'language', 'vue', 'react', 'typescript', 'node', 'tailwind', 'mongodb', 'postgresql'],
    'github': ['github', 'git', 'repository', 'repo', 'source code', 'projects'],
    'linkedin': ['linkedin', 'social', 'profile'],
    'company': ['company', 'employer', 'work for', 'organization', 'freelance'],
    'age': ['age', 'old', 'year', 'birth'],
    'email': ['email', 'mail', 'contact', 'reach'],
    'phone': ['phone', 'number', 'call', 'whatsapp'],
    'city': ['city', 'live', 'location', 'where are you', 'from', 'address'],
    'country': ['country', 'nationality', 'nation'],
    'school': ['school', 'university', 'college', 'study', 'education', 'learn', 'student'],
    'position': ['position', 'role', 'title', 'rank'],
    'level': ['level', 'experience level', 'junior', 'senior', 'intermediate'],
    'experience': ['experience', 'how long', 'year of experience', 'experienced'],
    'languages': ['language', 'speak', 'khmer', 'english', 'french', 'chinese'],
    'hobbies': ['hobby', 'hobbies', 'like to do', 'free time', 'fun', 'gaming', 'music', 'reading'],
    'interests': ['interest', 'passion', 'into', 'web development', 'ai', 'open source'],
    'bio': ['bio', 'about me', 'summary', 'description', 'overview', 'portfolio']
}

def is_about_phoun(text):
    """Check if user is asking about Phoun"""
    text_lower = text.lower()
    # Check if any Phoun keyword is in the text
    if 'phoun' in text_lower:
        return True
    # Check if asking about the bot's identity/skills directly (without saying Phoun)
    identity_keywords = ['who are you', 'what is your name', 'tell me about you', 'about yourself',
                         'your skill', 'your job', 'your work', 'your age', 'your email',
                         'your school', 'your experience', 'your hobby', 'your language',
                         'where are you from', 'what do you do', 'how old are you', 'how old']
    for kw in identity_keywords:
        if kw in text_lower:
            return True
    return False

def get_phoun_answer(text):
    """Find relevant Phoun data based on keywords in the question with styled responses"""
    text_lower = text.lower()
    answers = []

    for field, keywords in PHOUN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                value = PHOUN_DATA.get(field, '')
                if value and value not in [a[1] for a in answers]:
                    answers.append((field, value))
                    break

    # Sensitive fields that should be private
    SENSITIVE_FIELDS = {'age', 'email', 'phone', 'address'}

    if answers:
        # Check if any sensitive field was asked
        for field, value in answers:
            if field in SENSITIVE_FIELDS:
                return "🔒 *Privacy Protected*\n\nSorry, I can't share my personal information. 🙅‍♂️"

        # Build a styled response with emojis for non-sensitive fields
        responses = []
        for field, value in answers:
            if field == 'name':
                responses.append(f"👤 *Name:* {value}")
            elif field == 'job_title':
                responses.append(f"💼 *Job:* {value}")
            elif field == 'skills':
                responses.append(f"🛠️ *Skills:* {value}")
            elif field == 'school':
                responses.append(f"🎓 *Education:* {value}")
            elif field == 'city':
                responses.append(f"📍 *Location:* {value}")
            elif field == 'country':
                responses.append(f"🌍 *Country:* {value}")
            elif field == 'company':
                responses.append(f"🏢 *Company:* {value}")
            elif field == 'experience':
                responses.append(f"⭐ *Experience:* {value}")
            elif field == 'hobbies':
                responses.append(f"🎮 *Hobbies:* {value}")
            elif field == 'languages':
                responses.append(f"🗣️ *Languages:* {value}")
            elif field == 'github':
                responses.append(f"🐙 *GitHub:* {value}")
            elif field == 'linkedin':
                responses.append(f"💼 *LinkedIn:* {value}")
            elif field == 'bio':
                responses.append(f"📝 *Bio:* {value}")
            else:
                field_display = field.replace('_', ' ').title()
                responses.append(f"• *{field_display}:* {value}")

        header = "👋 *Hey there! Here's a bit about me:*\n\n"
        return header + "\n".join(responses) + "\n\n🚀 Feel free to ask more!"

    # If no specific match but asking about Phoun, return a styled summary
    if PHOUN_DATA:
        return (
            "👋 *Hello! I'm Phoun Phan* 🚀\n\n"
            f"💼 *Role:* {PHOUN_DATA.get('job_title', 'developer')}\n"
            f"🛠️ *Skills:* {PHOUN_DATA.get('skills', '')}\n"
            f"⭐ *Experience:* {PHOUN_DATA.get('experience', '')}\n"
            f"🎓 *Education:* {PHOUN_DATA.get('school', '')}\n"
            f"📍 *Location:* {PHOUN_DATA.get('city', '')}, {PHOUN_DATA.get('country', '')}\n\n"
            f"📝 {PHOUN_DATA.get('bio', '')}\n\n"
            f"🔗 *Connect with me:*\n"
            f"🐙 GitHub: {PHOUN_DATA.get('github', '')}\n"
            f"💼 LinkedIn: {PHOUN_DATA.get('linkedin', '')}\n\n"
            "Ask me anything else! 💬"
        )

    return "I don't have any information about Phoun yet. 😕"

# This handles the /start and /help commands
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    welcome_text = (
        "✨ *Welcome! I'm your AI Assistant* ✨\n\n"
        "🎉 Hey there! I'm ready to help you with all sorts of cool stuff:\n\n"
        "🧠 *Ask Me Anything*\n"
        "   Coding, world events, movies, music, games, science... you name it!\n\n"
        "🎨 *Generate Images*\n"
        "   Type `/image <description>` to create amazing AI art!\n\n"
        "👤 *About Phoun*\n"
        "   Ask about skills, projects, education, and more!\n\n"
        "⚡ *Features*\n"
        "   • Smart responses with Markdown formatting\n"
        "   • Auto-split long messages\n"
        "   • Fast and friendly replies\n\n"
        "💡 *Try these:*\n"
        "   • `What can you help me with?`\n"
        "   • `/image a cyberpunk city`\n"
        "   • `Explain quantum computing`\n\n"
        "Let's get started! 🚀"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

def style_gemini_response(text):
    """Add emojis and formatting to Gemini responses to make them more engaging"""
    # Add a fun header based on response content
    text_lower = text.lower()

    # Detect topic and add appropriate header
    if any(word in text_lower for word in ['code', 'programming', 'python', 'javascript', 'developer', 'function', 'class', 'variable']):
        header = "💻 *Here's what I found for you!*\n\n"
    elif any(word in text_lower for word in ['science', 'physics', 'chemistry', 'biology', 'quantum', 'space']):
        header = "🔬 *Science Time!*\n\n"
    elif any(word in text_lower for word in ['history', 'war', 'ancient', 'empire', 'civilization']):
        header = "📜 *History Lesson!*\n\n"
    elif any(word in text_lower for word in ['movie', 'film', 'actor', 'director', 'cinema']):
        header = "🎬 *Movie Talk!*\n\n"
    elif any(word in text_lower for word in ['song', 'music', 'album', 'artist', 'band', 'genre']):
        header = "🎵 *Music Vibes!*\n\n"
    elif any(word in text_lower for word in ['game', 'gaming', 'player', 'video game', 'rpg']):
        header = "🎮 *Gaming Zone!*\n\n"
    elif any(word in text_lower for word in ['food', 'recipe', 'cook', 'cuisine', 'restaurant']):
        header = "🍽️ *Food for Thought!*\n\n"
    elif any(word in text_lower for word in ['travel', 'country', 'city', 'tourism', 'vacation']):
        header = "✈️ *Travel Guide!*\n\n"
    elif any(word in text_lower for word in ['help', 'assist', 'support', 'question']):
        header = "🙌 *Happy to Help!*\n\n"
    else:
        header = "✨ *Here's your answer!*\n\n"

    # Add a friendly footer
    footer = "\n\n💡 *Tip:* Feel free to ask follow-up questions or try `/image` for visuals! 🎨"

    return header + text + footer

def escape_markdown(text):
    """Escape special Markdown characters for Telegram"""
    # Characters that need escaping in Markdown mode: _ * [ ] ( ) ~ ` > # + - = | { } . !
    chars_to_escape = r'\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!'
    return re.sub(f'([{chars_to_escape}])', r'\\\1', text)

def send_long_text(chat_id, text, reply_to_message_id=None):
    """Split long text into chunks and send as multiple messages"""
    MAX_LENGTH = 4000
    
    # Escape markdown to prevent parsing errors
    safe_text = escape_markdown(text)
    
    if len(safe_text) <= MAX_LENGTH:
        bot.send_message(chat_id, safe_text, parse_mode="MarkdownV2", reply_to_message_id=reply_to_message_id)
        return
    
    # Split by paragraphs first, then by sentences if needed
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= MAX_LENGTH:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If single paragraph is too long, split it
            if len(para) > MAX_LENGTH:
                sentences = para.split('. ')
                current_chunk = ""
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 2 <= MAX_LENGTH:
                        current_chunk += sent + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sent + ". "
            else:
                current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Send chunks
    for i, chunk in enumerate(chunks):
        safe_chunk = escape_markdown(chunk)
        if i == 0:
            bot.send_message(chat_id, safe_chunk, parse_mode="MarkdownV2", reply_to_message_id=reply_to_message_id)
        else:
            cont_text = escape_markdown(f"(continued {i+1}/{len(chunks)})")
            bot.send_message(chat_id, f"*{cont_text}*\n\n{safe_chunk}", parse_mode="MarkdownV2")

# Generate AI image using Pollinations (free, no API key needed)
def generate_image(prompt):
    """Generate image URL from text prompt"""
    encoded_prompt = requests.utils.quote(prompt[:200])  # Limit prompt length
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

# This handles the /image command
@bot.message_handler(commands=['image'])
def handle_image_command(message):
    prompt = message.text.replace('/image', '').strip()
    if not prompt:
        bot.reply_to(message, "Please provide a description. Example: `/image a cat in space`", parse_mode="Markdown")
        return
    
    bot.reply_to(message, "🎨 Generating image...")
    try:
        image_url = generate_image(prompt)
        bot.send_photo(message.chat.id, image_url, caption=f"🖼️ Prompt: {prompt}", reply_to_message_id=message.message_id)
    except Exception as e:
        bot.reply_to(message, f"Failed to generate image: {str(e)}")

# This handles all other text messages - hybrid Phoun data + Gemini AI
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    
    # Check if asking about Phoun - use CSV data
    if is_about_phoun(user_text):
        phoun_answer = get_phoun_answer(user_text)
        send_long_text(message.chat.id, phoun_answer, message.message_id)
        return
    
    # Otherwise use Gemini AI for general questions (coding, world, movies, songs, games, etc.)
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": user_text}]}]}
        )
        result = response.json()
        print(f"API Response: {result}")
        
        if "candidates" in result and len(result["candidates"]) > 0:
            response_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Style the response with emojis and formatting
            styled_response = style_gemini_response(response_text)
            # Send text response (split if too long)
            send_long_text(message.chat.id, styled_response, message.message_id)
            
            # Optionally generate a related image for certain topics
            # Uncomment below if you want automatic images for every response
            # try:
            #     image_url = generate_image(message.text[:100])
            #     bot.send_photo(message.chat.id, image_url, reply_to_message_id=message.message_id)
            # except:
            #     pass
        else:
            bot.reply_to(message, f"No response from API. Response: {result}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        bot.reply_to(message, f"Sorry, I encountered an error: {str(e)}")

print("Bot is running...")
# Remove any existing webhook to prevent conflicts
bot.remove_webhook()
bot.infinity_polling()
