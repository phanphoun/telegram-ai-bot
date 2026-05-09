import telebot
from services import GeminiService
from utils import escape_markdown, split_long_text, style_gemini_response

def register_handlers(bot: telebot.TeleBot, gemini: GeminiService) -> None:
    """Register general AI question handler (fallback)"""
    
    @bot.message_handler(func=lambda message: True)
    def handle_ai_question(message):
        """Handle general questions using Gemini AI"""
        try:
            response_text = gemini.generate_response(message.text)
            
            if response_text:
                # Style the response
                styled = style_gemini_response(response_text)
                
                # Escape markdown
                safe_text = escape_markdown(styled)
                
                # Split if too long
                chunks = split_long_text(safe_text)
                
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
            else:
                bot.reply_to(
                    message, 
                    "🤔 I'm having trouble connecting to my brain right now. Please try again in a moment!"
                )
                
        except Exception as e:
            print(f"Error in AI handler: {e}")
            bot.reply_to(
                message,
                "😅 Oops! Something went wrong. Please try again!"
            )
