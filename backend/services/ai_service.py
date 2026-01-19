from groq import Groq
from config import Config


class AIFarmAdvisorService:
    def __init__(self):
        self.client = Groq(api_key=Config.AI_API_KEY)

    def advise(self, farm_notes, transformation_summary, language="en"):
        prompt = self._build_prompt(
            farm_notes=farm_notes,
            transformation_summary=transformation_summary,
            language=language
        )

        response = self.client.chat.completions.create(
            model=Config.AI_MODEL,
            messages=[
                {"role": "system", "content": self._system_prompt(language)},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        return self._parse_response(response.choices[0].message.content)

    def _system_prompt(self, language):
        return f"""
            You are an AI Farm Advisor for small and rural farmers.

            Rules:
            - Do NOT invent new activities
            - Do NOT change pricing or rules
            - ONLY explain and suggest improvements
            - Clearly mark future ideas as "Later"
            - Speak in simple farmer-friendly language
            - Language: {language}
        """

    def _build_prompt(self, farm_notes, transformation_summary, language):
        return f"""
            Farmer description:
            {farm_notes}

            Current agritourism plan (rule-based, DO NOT CHANGE):
            {transformation_summary}

            Your tasks:
            1. Explain what agritourism means for THIS farm
            2. Explain what the farmer can start with (low risk)
            3. Suggest small improvements (optional)
            4. Suggest future ideas (mark as LATER)

            Return response in JSON with keys:
            - explanation
            - start_small
            - suggestions
            - future_ideas
        """

    def _parse_response(self, text):
        """
        AI already returns structured text.
        Keep raw for now.
        """
        return {
            "ai_response": text
        }
