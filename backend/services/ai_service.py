from groq import Groq
from config import Config


class AIFarmAdvisorService:
    def __init__(self):
        self.client = Groq(api_key=Config.AI_API_KEY)

    def advise(self, user_prompt, transformation_summary, language="en"):
        prompt = self._build_prompt(
            user_prompt=user_prompt,
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

    def _build_prompt(self, user_prompt, transformation_summary, language):
        return f"""
            Farmer description:
            {user_prompt}

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
        
    def advise_experience(self, user_prompt, experience_details, language="en"):
        """
        AI explanation layer for a SINGLE experience.

        Purpose:
        - Explain what this experience is
        - Help farmer understand how to run it safely
        - Suggest small improvements
        - Suggest future ideas (clearly marked as LATER)

        IMPORTANT:
        - Does NOT change rules
        - Does NOT invent new experiences
        - Works ONLY on already-generated experience data
        """

        prompt = f"""
        Farmer description:
        {user_prompt}

        Selected experience (DO NOT CHANGE):
        {experience_details}

        Your tasks:
        1. Explain this experience in simple terms
        2. Explain how the farmer can run it step-by-step
        3. Suggest small improvements (optional)
        4. Suggest future ideas (mark clearly as LATER)

        Return response in JSON with keys:
        - explanation
        - how_to_run
        - improvements
        - future_ideas
        """

        response = self.client.chat.completions.create(
            model=Config.AI_MODEL,
            messages=[
                {"role": "system", "content": self._system_prompt(language)},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        return {
            "ai_response": response.choices[0].message.content
        }
