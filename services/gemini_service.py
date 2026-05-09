import requests
from typing import Dict, Optional
from config import Settings

class GeminiService:
    """Service for interacting with Google Gemini AI API"""
    
    def __init__(self):
        self.api_key = Settings.GEMINI_API_KEY
        self.api_url = Settings.GEMINI_API_URL
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate AI response for a given prompt"""
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            
            print(f"No candidates in response: {result}")
            return None
            
        except requests.exceptions.Timeout:
            print("Gemini API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Gemini API request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in Gemini service: {e}")
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
