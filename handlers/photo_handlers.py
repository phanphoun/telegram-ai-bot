import telebot
import base64
import requests
from services import GeminiService, ImageService
from config import Settings
from utils import escape_markdown, split_long_text

class PhotoAnalyzer:
    """Service for analyzing uploaded photos and generating similar images"""
    
    def __init__(self, gemini: GeminiService, image_service: ImageService):
        self.gemini = gemini
        self.image_service = image_service
    
    def analyze_photo(self, bot: telebot.TeleBot, message):
        """Download photo, analyze with Gemini, and send description or generate similar"""
        
        caption = message.caption or ""
        caption_lower = caption.lower()
        
        # Check if user wants to generate a similar image
        wants_generate = any(kw in caption_lower for kw in [
            'generate', 'create', 'make', 'like this', 'similar', 'same style',
            'recreate', 'copy this', 'do like this'
        ])
        
        # Send loading message
        loading_text = "🎨 *Generating similar image...*" if wants_generate else "🔍 *Analyzing image...* 🖼️"
        loading_msg = bot.reply_to(message, loading_text, parse_mode="Markdown")
        
        try:
            # Get the largest photo
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Determine MIME type
            mime_type = "image/jpeg"
            if file_info.file_path and '.' in file_info.file_path:
                ext = file_info.file_path.split('.')[-1].lower()
                mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
                mime_type = mime_map.get(ext, 'image/jpeg')
            
            image_b64 = base64.b64encode(downloaded_file).decode('utf-8')
            
            if wants_generate:
                # Analyze then generate similar image
                self._handle_generate_request(bot, message, loading_msg, image_b64, mime_type, caption)
            else:
                # Just analyze the image
                self._handle_analyze_request(bot, message, loading_msg, image_b64, mime_type)
                
        except Exception as e:
            print(f"Photo handler error: {e}")
            try:
                bot.edit_message_text(
                    f"❌ Error: {str(e)}",
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id
                )
            except:
                bot.reply_to(message, "😅 Oops! Something went wrong. Please try again.")
    
    def _handle_generate_request(self, bot, message, loading_msg, image_b64, mime_type, caption):
        """Analyze image and generate a similar one"""
        try:
            # Step 1: Analyze the image to get a description
            analysis_prompt = (
                "Describe this image in detail for image generation. "
                "Focus on: style, colors, composition, objects, layout, text elements, "
                "background, and overall mood. Write it as a concise image generation prompt "
                "(max 150 words). Start directly with the description."
            )
            
            description = self._analyze_with_gemini(analysis_prompt, image_b64, mime_type)
            
            if not description:
                bot.edit_message_text(
                    "🤔 Could not analyze the image. Please try with a clearer image!",
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id
                )
                return
            
            # Step 2: Generate image from description
            bot.edit_message_text(
                f"🎨 *Analyzed! Now generating...*\n\n📋 Prompt: {description[:200]}...",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id,
                parse_mode="Markdown"
            )
            
            image_url = self.image_service.generate_image_url(description)
            
            # Step 3: Send generated image
            bot.delete_message(message.chat.id, loading_msg.message_id)
            
            bot.send_photo(
                message.chat.id,
                image_url,
                caption=f"🖼️ *Generated based on your image*\n\n📋 *Prompt:* {description[:300]}\n\n🔗 [View Full Image]({image_url})",
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
            
        except Exception as e:
            print(f"Generate error: {e}")
            bot.edit_message_text(
                f"❌ Failed to generate image: {str(e)}",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
    
    def _handle_analyze_request(self, bot, message, loading_msg, image_b64, mime_type):
        """Analyze image and send description"""
        try:
            prompt = (
                "Analyze this image and describe it in a friendly, engaging way. "
                "Be specific about: what's in the image, any text visible, colors, "
                "objects, people, context, and mood. If it's code/screenshot, explain it. "
                "If it's a person, describe them. Keep it conversational."
            )
            
            description = self._analyze_with_gemini(prompt, image_b64, mime_type)
            
            bot.delete_message(message.chat.id, loading_msg.message_id)
            
            if description:
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
                bot.send_message(
                    message.chat.id,
                    "🤔 I couldn't analyze this image. The vision API may be temporarily unavailable.",
                    reply_to_message_id=message.message_id
                )
                
        except Exception as e:
            print(f"Analysis error: {e}")
            bot.edit_message_text(
                f"❌ Error: {str(e)}",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
    
    def _analyze_with_gemini(self, prompt: str, image_b64: str, mime_type: str) -> str:
        """Send image and prompt to Gemini API for analysis"""
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
            print(f"Gemini vision response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API error: {result}")
                return None
            
            if "candidates" in result and len(result["candidates"]) > 0:
                parts = result["candidates"][0]["content"]["parts"]
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
            
            if "error" in result:
                print(f"Gemini API error: {result['error']}")
                
            return None
            
        except Exception as e:
            print(f"Vision API error: {e}")
            return None


def register_handlers(bot: telebot.TeleBot, gemini: GeminiService) -> None:
    """Register photo analysis handler"""
    
    image_service = ImageService()
    analyzer = PhotoAnalyzer(gemini, image_service)
    
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        """Handle uploaded photos - analyze or generate similar"""
        analyzer.analyze_photo(bot, message)
