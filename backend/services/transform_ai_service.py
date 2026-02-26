import json
from services.ai.factory import get_ai_provider
from services.ai.prompts.system_prompts import (
    farm_advisor_system_prompt,
    experience_advisor_system_prompt,
    story_generator_system_prompt,
)
from services.ai.prompts.user_prompts import (
    farm_advisory_prompt,
    experience_advisory_prompt,
    story_generation_prompt,
)
from config import Config

class TransformAIBase:
    """Shared base for all Transform AI services."""

    def __init__(self):
        self.provider = get_ai_provider()
        self.temperature = Config.AI_TEMPERATURE

    def _parse_json_response(self, text: str) -> dict:
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            return {"ai_response": text}

class TransformAdvisorService(TransformAIBase):
    """Farm transformation advisory — advises on plan and experiences."""
    
    def advise(self, user_prompt: str, transformation_summary: str, language: str = "en") -> dict:
        """Farm-level transformation advisory."""
        system = farm_advisor_system_prompt(language)
        user = farm_advisory_prompt(user_prompt, transformation_summary)

        raw_response = self.provider.complete(
            system_prompt=system,
            user_prompt=user,
            temperature=self.temperature,
        )
        return self._parse_json_response(raw_response)

    def advise_experience(self, user_prompt: str, experience_details: dict, language: str = "en") -> dict:
        """Single experience advisory."""
        
        system = experience_advisor_system_prompt(language)
        user = experience_advisory_prompt(user_prompt, experience_details)

        raw_response = self.provider.complete(
            system_prompt=system,
            user_prompt=user,
            temperature=self.temperature,
        )
        return self._parse_json_response(raw_response)
    

class TransformStoryService(TransformAIBase):
    """Experience story generation — creates visitor-facing content."""

    def generate_story(self, experience_details: dict, language: str = "en") -> dict:
        system = story_generator_system_prompt(language)
        user = story_generation_prompt(experience_details)
        raw_response = self.provider.complete(
            system_prompt=system,
            user_prompt=user,
            temperature=self.temperature,
        )
        return self._parse_json_response(raw_response)

transform_advisor_service = TransformAdvisorService()
story_service = TransformStoryService()