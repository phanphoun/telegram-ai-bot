import telebot
from services import GeminiService
from utils import escape_markdown, split_long_text

# Supported programming languages
SUPPORTED_LANGUAGES = {
    'python': 'Python',
    'html': 'HTML',
    'css': 'CSS',
    'javascript': 'JavaScript',
    'js': 'JavaScript',
    'typescript': 'TypeScript',
    'ts': 'TypeScript',
    'react': 'React',
    'jsx': 'React JSX',
    'tsx': 'React TSX',
    'vue': 'Vue.js',
    'node': 'Node.js',
    'nodejs': 'Node.js',
    'sql': 'SQL',
    'json': 'JSON',
    'bash': 'Bash/Shell',
    'shell': 'Bash/Shell',
    'dockerfile': 'Dockerfile',
    'yaml': 'YAML',
    'markdown': 'Markdown',
    'c': 'C',
    'cpp': 'C++',
    'java': 'Java',
    'go': 'Go',
    'rust': 'Rust',
    'php': 'PHP',
    'ruby': 'Ruby',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
}

def register_handlers(bot: telebot.TeleBot, gemini: GeminiService) -> None:
    """Register code generation command handler"""
    
    @bot.message_handler(commands=['code'])
    def handle_code_command(message):
        """Generate code in specified language"""
        args = message.text.replace('/code', '').strip()
        
        if not args:
            languages_list = ', '.join(sorted(set(SUPPORTED_LANGUAGES.values())))
            bot.reply_to(
                message,
                f"💻 *Code Generator*\n\n"
                f"Usage: `/code <language> <description>`\n\n"
                f"*Examples:*\n"
                f"• `/code python function to sort list`\n"
                f"• `/code react login component`\n"
                f"• `/code html responsive navbar`\n"
                f"• `/code javascript fetch API`\n\n"
                f"*Supported languages:* {languages_list}",
                parse_mode="Markdown"
            )
            return
        
        # Parse language and description
        parts = args.split(' ', 1)
        lang = parts[0].lower()
        description = parts[1] if len(parts) > 1 else ""
        
        if not description:
            bot.reply_to(
                message,
                "❌ Please provide a description of what code you want.\n"
                "Example: `/code python calculate factorial`",
                parse_mode="Markdown"
            )
            return
        
        # Map language alias to full name
        lang_name = SUPPORTED_LANGUAGES.get(lang, lang.title())
        
        # Send loading message
        loading_msg = bot.reply_to(
            message,
            f"⌨️ *Generating {lang_name} code...*",
            parse_mode="Markdown"
        )
        
        try:
            # Build prompt for code generation
            prompt = (
                f"Generate clean, well-commented {lang_name} code for: {description}\n\n"
                f"Requirements:\n"
                f"- Use best practices for {lang_name}\n"
                f"- Include comments explaining the code\n"
                f"- Make it production-ready\n"
                f"- Wrap the code in markdown code blocks with language identifier\n"
                f"- Briefly explain how the code works after the code block"
            )
            
            response = gemini.generate_response(prompt)
            
            if response:
                # Escape markdown for safe sending
                safe_code = escape_markdown(response)
                
                # Split if too long
                chunks = split_long_text(safe_code)
                
                # Delete loading message
                bot.delete_message(message.chat.id, loading_msg.message_id)
                
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        bot.send_message(
                            message.chat.id,
                            f"💻 *Generated {lang_name} Code*\n\n{chunk}",
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
                    "🤔 Sorry, I couldn't generate the code. Please try again!",
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id
                )
                
        except Exception as e:
            print(f"Code generation error: {e}")
            bot.edit_message_text(
                f"❌ Error generating code: {str(e)}",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
