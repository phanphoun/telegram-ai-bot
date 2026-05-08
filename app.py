import telebot
import requests
import csv
import re

# Replace 'YOUR_TOKEN_HERE' with the token from BotFather
API_TOKEN = '8606599772:AAHVunwuGVCwaa-JQ3g4h3GaWD8ZHVro7sI'

bot = telebot.TeleBot(API_TOKEN)
GEMINI_API_KEY = "AIzaSyAoai2XQxphd5a9Mc2zTUQkT5J1JrBguoE"

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
                         'where are you from', 'what do you do']
    for kw in identity_keywords:
        if kw in text_lower:
            return True
    return False

def get_phoun_answer(text):
    """Find relevant Phoun data based on keywords in the question"""
    text_lower = text.lower()
    answers = []
    
    for field, keywords in PHOUN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                value = PHOUN_DATA.get(field, '')
                if value and value not in [a[1] for a in answers]:
                    # Format field name for display
                    field_display = field.replace('_', ' ').title()
                    answers.append((field_display, value))
                    break
    
    if answers:
        response = "Here's what I found about *Phoun Phan*:\n\n"
        for field_display, value in answers:
            response += f"*{field_display}:* {value}\n"
        return response
    
    # If no specific match but asking about Phoun, return a summary
    if PHOUN_DATA:
        return (
            f"*{PHOUN_DATA.get('name', 'Phoun Phan')}* is a {PHOUN_DATA.get('job_title', 'developer')}.\n\n"
            f"*Skills:* {PHOUN_DATA.get('skills', '')}\n"
            f"*Experience:* {PHOUN_DATA.get('experience', '')}\n"
            f"*Education:* {PHOUN_DATA.get('school', '')}\n"
            f"*Location:* {PHOUN_DATA.get('city', '')}, {PHOUN_DATA.get('country', '')}\n\n"
            f"*{PHOUN_DATA.get('bio', '')}*\n\n"
            f"*GitHub:* {PHOUN_DATA.get('github', '')}\n"
            f"*LinkedIn:* {PHOUN_DATA.get('linkedin', '')}"
        )
    
    return "I don't have any information about Phoun yet."

# This handles the /start and /help commands
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    welcome_text = (
        "🤖 *Welcome to AI Bot!*\n\n"
        "I can help you with:\n"
        "• 💬 *Ask me anything* - I answer with AI-powered responses\n"
        "• 🖼️ */image* `<description>` - Generate AI images\n\n"
        "Long responses are automatically split into multiple messages."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

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
            
            # Send text response (split if too long)
            send_long_text(message.chat.id, response_text, message.message_id)
            
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
