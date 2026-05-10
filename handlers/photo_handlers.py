import telebot
import base64
import io
from services import GeminiService
from utils import escape_markdown, split_long_text

class PhotoAnalyzer:
    """Service for analyzing uploaded photos using Gemini Vision"""
    
    def __init__(self, gemini: GeminiService):
        self.gemini = gemini
    
    def analyze_photo(self, bot: telebot.TeleBot, message):
        """Download photo, analyze with Gemini, and send description"""
        
        # Send loading message
        loading_msg = bot.reply_to(
            message,
            "🔍 *Analyzing image...* 🖼️",
            parse_mode="Markdown"
        )
        
        try:
            # Get the largest photo (best quality)
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Determine MIME type from file extension
            mime_type = "image/jpeg"  # default
            if file_info.file_path:
                ext = file_info.file_path.split('.')[-1].lower() if '.' in file_info.file_path else 'jpg'
                mime_map = {
                    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'webp': 'image/webp'
                }
                mime_type = mime_map.get(ext, 'image/jpeg')
            
            # Base64 encode the image
            image_b64 = base64.b64encode(downloaded_file).decode('utf-8')
            
            # Build the multimodal prompt for Gemini
            prompt = (
                "You are Phoun Phan's AI assistant. Analyze this image and describe it "
                "in a friendly, engaging way. Be specific about what's in the image, "
                "any text visible, colors, objects, people, context, and mood. "
                "If it's a screenshot of code, explain what the code does. "
                "If it's a photo of a person, describe them (if appropriate). "
                "If it's a landscape, describe the scene. "
                "Keep it conversational and interesting."
            )
            
            # Call Gemini with image
            description = self._analyze_with_gemini(prompt, image_b64, mime_type)
            
            # Delete loading message
            bot.delete_message(message.chat.id, loading_msg.message_id)
            
            if description:
                # Escape markdown and split if too long
                safe_desc = escape_markdown(description)
                chunks = split_long_text(safe_desc)
                
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        bot.send_message(
                            message.chat.id,
                            f"🖼️ *Image Analysis*\n\n{chunk}",
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
                bot.edit_message_text(
                    "🤔 Sorry, I couldn't analyze this image. Please try again!",
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id
                )
                
        except Exception as e:
            print(f"Photo analysis error: {e}")
            try:
                bot.edit_message_text(
                    f"❌ Error analyzing image: {str(e)}",
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id
                )
            except:
                bot.reply_to(message, "😅 Oops! Something went wrong analyzing the image.")
    
    def _analyze_with_gemini(self, prompt: str, image_b64: str, mime_type: str) -> str:
        """Send image and prompt to Gemini API for analysis"""
        import requests
        from config import Settings
        
        try:
            response = requests.post(
                f"{Settings.GEMINI_API_URL}?key={Settings.GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_b64
                                }
                            }
                        ]
                    }]
                },
                timeout=60
            )
            
            result = response.json()
            print(f"Gemini vision response: {result}")
            
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            
            if "error" in result:
                print(f"Gemini API error: {result['error']}")
                return None
                
            return None
            
        except Exception as e:
            print(f"Vision API error: {e}")
            return None


def register_handlers(bot: telebot.TeleBot, gemini: GeminiService) -> None:
    """Register photo analysis handler"""
    
    analyzer = PhotoAnalyzer(gemini)
    
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        """Handle uploaded photos"""
        analyzer.analyze_photo(bot, message)
