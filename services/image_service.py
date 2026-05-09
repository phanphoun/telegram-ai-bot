import requests

class ImageService:
    """Service for generating AI images using Pollinations"""
    
    BASE_URL = "https://image.pollinations.ai/prompt/"
    
    def generate_image_url(self, prompt: str, width: int = 1024, height: int = 1024) -> str:
        """Generate image URL from text prompt"""
        encoded_prompt = requests.utils.quote(prompt[:200])
        return f"{self.BASE_URL}{encoded_prompt}?width={width}&height={height}&nologo=true"
