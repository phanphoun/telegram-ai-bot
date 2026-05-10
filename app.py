import os
import telebot
from config import Settings
from data import ProfileRepository
from services import GeminiService, ImageService
from handlers import register_common, register_phoun, register_ai, register_image, register_code

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

def main():
    """Main entry point for the Telegram AI Bot"""
    
    # Validate configuration
    Settings.validate()
    
    # Initialize bot
    bot = telebot.TeleBot(Settings.TELEGRAM_BOT_TOKEN)
    
    # Initialize services
    profile_repo = ProfileRepository(Settings.PROFILE_CSV_PATH)
    gemini = GeminiService()
    image_service = ImageService()
    
    # Register handlers (order matters - specific handlers first)
    register_common(bot)
    register_code(bot, gemini)
    register_image(bot, image_service)
    register_phoun(bot, profile_repo)
    register_ai(bot, gemini)  # Fallback handler - must be last
    
    # Remove any existing webhook to prevent conflicts
    bot.remove_webhook()
    
    print("🤖 Bot is running...")
    print("Press Ctrl+C to stop")
    
    # Start polling
    bot.infinity_polling()

if __name__ == "__main__":
    main()
