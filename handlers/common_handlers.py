import telebot
from config import Settings

def register_handlers(bot: telebot.TeleBot) -> None:
    """Register common command handlers (start, help)"""
    
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
