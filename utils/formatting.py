import re

def escape_markdown(text: str) -> str:
    """Escape special Markdown characters for Telegram MarkdownV2"""
    chars_to_escape = r'\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!'
    return re.sub(f'([{chars_to_escape}])', r'\\\1', text)

def split_long_text(text: str, max_length: int = 4000) -> list:
    """Split long text into chunks that fit Telegram's message limit"""
    if len(text) <= max_length:
        return [text]
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_length:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            if len(para) > max_length:
                # Split single long paragraph by sentences
                sentences = para.split('. ')
                current_chunk = ""
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 2 <= max_length:
                        current_chunk += sent + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sent + ". "
            else:
                current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def style_gemini_response(text: str) -> str:
    """Add emojis and formatting to Gemini AI responses"""
    text_lower = text.lower()
    
    # Detect topic and add appropriate header
    topic_headers = [
        (['code', 'programming', 'python', 'javascript', 'developer', 'function', 'class'], "💻 *Here's what I found for you!*\n\n"),
        (['science', 'physics', 'chemistry', 'biology', 'quantum', 'space'], "🔬 *Science Time!*\n\n"),
        (['history', 'war', 'ancient', 'empire', 'civilization'], "📜 *History Lesson!*\n\n"),
        (['movie', 'film', 'actor', 'director', 'cinema'], "🎬 *Movie Talk!*\n\n"),
        (['song', 'music', 'album', 'artist', 'band', 'genre'], "🎵 *Music Vibes!*\n\n"),
        (['game', 'gaming', 'player', 'video game', 'rpg'], "🎮 *Gaming Zone!*\n\n"),
        (['food', 'recipe', 'cook', 'cuisine', 'restaurant'], "🍽️ *Food for Thought!*\n\n"),
        (['travel', 'country', 'city', 'tourism', 'vacation'], "✈️ *Travel Guide!*\n\n"),
        (['help', 'assist', 'support', 'question'], "🙌 *Happy to Help!*\n\n"),
    ]
    
    header = "✨ *Here's your answer!*\n\n"  # default
    for keywords, topic_header in topic_headers:
        if any(kw in text_lower for kw in keywords):
            header = topic_header
            break
    
    footer = "\n\n💡 *Tip:* Feel free to ask follow-up questions or try `/image` for visuals! 🎨"
    
    return header + text + footer
