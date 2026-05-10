import csv
import os
from typing import Dict, List, Optional, Tuple

class ProfileRepository:
    """Repository for managing user profile data from CSV files"""
    
    def __init__(self, csv_path: str = 'data/profiles/phoun.csv'):
        self.csv_path = csv_path
        self._data: Dict[str, str] = {}
        self._keywords: Dict[str, List[str]] = {
            'name': ['name', 'who are you', 'who is phoun', 'about phoun', 'introduce phoun'],
            'job_title': ['job', 'work', 'occupation', 'career', 'profession', 'do for a living', 'what do you do'],
            'skills': ['skill', 'tech stack', 'technology', 'programming', 'code', 'framework', 'language', 'vue', 'react', 'typescript', 'node', 'tailwind', 'mongodb', 'postgresql'],
            'github': ['github', 'git', 'repository', 'repo', 'source code', 'projects', 'project', 'your project', 'my project'],
            'linkedin': ['linkedin', 'social', 'profile'],
            'company': ['company', 'employer', 'work for', 'organization', 'freelance'],
            'portfolio': ['portfolio', 'website', 'your website', 'camdev', 'camdev.site'],
            'age': ['age', 'old', 'year', 'birth'],
            'email': ['email', 'mail', 'contact', 'reach'],
            'phone': ['phone', 'number', 'call', 'whatsapp', 'can i call you', 'can you speak', 'speak with you', 'contact'],
            'city': ['city', 'live', 'location', 'where are you', 'from', 'address'],
            'country': ['country', 'nationality', 'nation'],
            'school': ['school', 'university', 'college', 'study', 'education', 'learn', 'student'],
            'position': ['position', 'role', 'title', 'rank'],
            'level': ['level', 'experience level', 'junior', 'senior', 'intermediate'],
            'experience': ['experience', 'how long', 'year of experience', 'experienced'],
            'languages': ['language', 'speak', 'khmer', 'english', 'french', 'chinese'],
            'hobbies': ['hobby', 'hobbies', 'like to do', 'free time', 'fun', 'gaming', 'music', 'reading'],
            'interests': ['interest', 'passion', 'into', 'web development', 'ai', 'open source'],
            'bio': ['bio', 'about me', 'summary', 'description', 'overview'],
            'projects': ['project', 'projects', 'your project', 'my project', 'football', 'booking', 'student management', 'sms', 'dev review', 'dashboard', 'portfolio']
        }
        self._sensitive_fields = {'age', 'email', 'address'}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load profile data from CSV file"""
        try:
            # Try profile-specific path first, fall back to root
            paths_to_try = [self.csv_path, 'phoun.csv']
            
            for path in paths_to_try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            self._data = row
                            break
                    print(f"Loaded profile data from {path}")
                    return
            
            print(f"Warning: No profile CSV found at {self.csv_path}")
        except Exception as e:
            print(f"Error loading profile data: {e}")
    
    def is_about_profile(self, text: str) -> bool:
        """Check if text is asking about the profile owner"""
        text_lower = text.lower()
        
        # Skip image generation, prompt, and code requests
        negative_keywords = [
            'generate image', 'create image', 'make image', 'image of',
            'prompt for', 'prompt to', 'give me a prompt',
            'generate a', 'create a', 'write a',
            'code for', 'function to', 'how to code'
        ]
        if any(kw in text_lower for kw in negative_keywords):
            return False
        
        # Check if name is mentioned
        if 'phoun' in text_lower:
            return True
        
        # Check identity keywords
        identity_keywords = [
            'who are you', 'what is your name', 'tell me about you', 'about yourself',
            'your skill', 'your job', 'your work', 'your age', 'your email',
            'your school', 'your experience', 'your hobby', 'your language',
            'where are you from', 'what do you do', 'how old are you', 'how old'
        ]
        
        if any(kw in text_lower for kw in identity_keywords):
            return True
        
        # Check all profile keywords (projects, skills, etc.)
        for field, keywords in self._keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    return True
        
        return False
    
    def get_answer(self, text: str) -> Optional[str]:
        """Get styled answer for a question about the profile"""
        text_lower = text.lower()
        matched_fields: List[Tuple[str, str]] = []
        
        # Find matching fields based on keywords
        for field, keywords in self._keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    value = self._data.get(field, '')
                    if value and not any(f == field for f, _ in matched_fields):
                        matched_fields.append((field, value))
                    break
        
        # Check for sensitive fields
        for field, _ in matched_fields:
            if field in self._sensitive_fields:
                return "🔒 *Privacy Protected*\n\nSorry, I can't share my personal information. 🙅‍♂️"
        
        # Build styled response
        if matched_fields:
            return self._format_fields(matched_fields)
        
        # Return summary if asking about profile but no specific match
        if self._data:
            return self._format_summary()
        
        return None
    
    def _format_fields(self, fields: List[Tuple[str, str]]) -> str:
        """Format matched fields into styled response"""
        responses = []
        
        emoji_map = {
            'name': '👤', 'job_title': '💼', 'skills': '🛠️', 'school': '🎓',
            'city': '📍', 'country': '🌍', 'company': '🏢', 'experience': '⭐',
            'hobbies': '🎮', 'languages': '🗣️', 'github': '🐙', 'linkedin': '💼',
            'bio': '📝', 'position': '📋', 'level': '📊', 'interests': '💡',
            'portfolio': '🌐', 'projects': '🚀'
        }
        
        for field, value in fields:
            emoji = emoji_map.get(field, '•')
            field_display = field.replace('_', ' ').title()
            responses.append(f"{emoji} *{field_display}:* {value}")
        
        header = "👋 *Hey there! Here's a bit about me:*\n\n"
        return header + "\n".join(responses) + "\n\n🚀 Feel free to ask more!"
    
    def _format_summary(self) -> str:
        """Format a summary of all public profile data"""
        return (
            f"👋 *Hello! I'm {self._data.get('name', 'Phoun Phan')}* 🚀\n\n"
            f"💼 *Role:* {self._data.get('job_title', 'developer')}\n"
            f"🛠️ *Skills:* {self._data.get('skills', '')}\n"
            f"⭐ *Experience:* {self._data.get('experience', '')}\n"
            f"🎓 *Education:* {self._data.get('school', '')}\n"
            f"📍 *Location:* {self._data.get('city', '')}, {self._data.get('country', '')}\n\n"
            f"📝 {self._data.get('bio', '')}\n\n"
            f"🔗 *Connect with me:*\n"
            f"🌐 Portfolio: https://camdev.site\n"
            f"🐙 GitHub: {self._data.get('github', '')}\n"
            f"💼 LinkedIn: {self._data.get('linkedin', '')}\n\n"
            "Ask me anything else! 💬"
        )
    
    def get_data(self) -> Dict[str, str]:
        """Get raw profile data"""
        return self._data.copy()
