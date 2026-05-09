import telebot
from data import ProfileRepository
from utils import escape_markdown, split_long_text

def register_handlers(bot: telebot.TeleBot, profile_repo: ProfileRepository) -> None:
    """Register Phoun profile question handler"""
    
    @bot.message_handler(func=lambda message: profile_repo.is_about_profile(message.text))
    def handle_phoun_question(message):
        """Handle questions about Phoun using profile data"""
        answer = profile_repo.get_answer(message.text)
        
        if answer:
            # Escape markdown for safe Telegram sending
            safe_answer = escape_markdown(answer)
            
            # Split if too long
            chunks = split_long_text(safe_answer)
            
            for i, chunk in enumerate(chunks):
                if i == 0:
                    bot.send_message(
                        message.chat.id, 
                        chunk, 
                        parse_mode="MarkdownV2",
                        reply_to_message_id=message.message_id
                    )
                else:
                    cont_text = escape_markdown(f"(continued {i+1}/{len(chunks)})")
                    bot.send_message(
                        message.chat.id,
                        f"*{cont_text}*\n\n{chunk}",
                        parse_mode="MarkdownV2"
                    )
