import requests
import time
from typing import Dict, Optional
from config import Settings

class GeminiService:
    """Service for interacting with Google Gemini AI API with personal context"""
    
    # System context - teaches Gemini who Phoun is
    PROFILE_CONTEXT = """You are an AI assistant representing Phoun Phan. Here is everything you know about Phoun:

ABOUT PHOUN:
- Name: Phoun Phan
- Role: Full-Stack Software Developer
- Location: Phnom Penh, Cambodia
- Education: Passerelles Numeriques Cambodia (Student)
- Experience Level: Intermediate (2+ years)
- Languages: Khmer, English, French, Chinese
- Hobbies: Coding, Gaming, Music, Reading
- Interests: Web Development, AI, Open Source, Modern Web Apps

TECH STACK:
- Frontend: Vue.js, React, TypeScript, Tailwind CSS
- Backend: Node.js, Express
- Databases: MongoDB, PostgreSQL
- Tools: Git, GitHub, VS Code
- Other: Full-stack Development, REST APIs

PORTFOLIO: https://camdev.site
GITHUB: https://github.com/phanphoun
LINKEDIN: https://linkedin.com/in/phanphoun

INSTRUCTIONS:
- When asked about projects, skills, education, or personal info, answer based on the data above.
- If someone asks about your projects and you don't have a specific list, say you have experience building modern web apps with Vue, React, and Node.js.
- For coding questions, provide practical examples using your tech stack (Vue, React, TypeScript, Node.js).
- Be friendly, professional, and enthusiastic about technology.
- If asked something not in your profile, answer as a knowledgeable developer would.
"""
    
    def __init__(self):
        self.api_key = Settings.GEMINI_API_KEY
        self.api_url = Settings.GEMINI_API_URL
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate AI response with personal context prepended and retry logic"""
        # Prepend profile context so Gemini knows who Phoun is
        contextualized_prompt = f"{self.PROFILE_CONTEXT}\n\nUser question: {prompt}\n\nAnswer as Phoun Phan would:"
        
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.api_url}?key={self.api_key}",
                    json={"contents": [{"parts": [{"text": contextualized_prompt}]}]},
                    timeout=30
                )
                
                # Handle rate limiting (429)
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limited. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        print("Gemini API rate limit exceeded. Max retries reached.")
                        return None
                
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                
                print(f"No candidates in response: {result}")
                return None
                
            except requests.exceptions.Timeout:
                print("Gemini API request timed out")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                return None
            except requests.exceptions.RequestException as e:
                print(f"Gemini API request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                return None
            except Exception as e:
                print(f"Unexpected error in Gemini service: {e}")
                return None
        
        return None
    
    def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": "hi"}]}]},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
