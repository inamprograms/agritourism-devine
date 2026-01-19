# services/story_service.py

from groq import Groq
from config import Config

class AIStoryService:
    """
    Generates visitor-friendly stories for farm experiences.
    """

    def __init__(self):
        self.client = Groq(api_key=Config.AI_API_KEY)

    def generate_story(self, experience_details, language="en"):
        """
        Generate short, engaging, visitor-facing story for a single experience.
        """
        prompt = self._build_prompt(experience_details, language)

        response = self.client.chat.completions.create(
            model=Config.AI_MODEL,
            messages=[
                {"role": "system", "content": self._system_prompt(language)},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        return {
            "story_response": response.choices[0].message.content
        }

    def _system_prompt(self, language):
        return f"""
            You are an AI Story Generator for farm visitors.
            Rules:
            - Explain experiences in simple, engaging, visitor-friendly language.
            - Do NOT change the experience type or level.
            - Make it concise and appealing.
            - Language: {language}
        """

    def _build_prompt(self, experience_details, language):
        return f"""
        Experience details:
        {experience_details}

        Task:
        - Write a short, engaging story for visitors about this experience.
        - Highlight what they will see, do, and enjoy.
        - Keep it simple, fun, and clear.
        - Return in JSON with key 'story' only.
        """

# Singleton instance
story_service = AIStoryService()
