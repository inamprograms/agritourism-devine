def farm_advisory_prompt(user_prompt: str, transformation_summary: str) -> str:
    return f"""
Farmer's question or description:
{user_prompt}

Current agritourism transformation plan (rule-based — DO NOT modify this data):
{transformation_summary}

Your tasks:
1. Directly answer the farmer's question
2. Identify the single best first step (lowest risk, lowest effort)
3. Suggest 2-3 small practical improvements
4. Note future possibilities clearly marked as [FUTURE IDEA]

Return ONLY valid JSON with these exact keys:
{{
  "answer": "direct, clear answer to the farmer's question in 2-3 sentences",
  "first_step": "the single best thing to start with and exactly why",
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "future_ideas": ["future idea 1", "future idea 2"]
}}
"""


def experience_advisory_prompt(user_prompt: str, experience_details: dict) -> str:
    return f"""
Farmer's question or description:
{user_prompt}

Selected experience details (DO NOT modify this data):
{experience_details}

Your tasks:
1. Directly answer the farmer's question about this experience
2. Explain what this experience involves in simple terms
3. Give a step-by-step guide to running it
4. Suggest small improvements
5. Note future possibilities marked as [FUTURE IDEA]

Return ONLY valid JSON with these exact keys:
{{
  "answer": "direct answer to the farmer's question in 2-3 sentences",
  "what_it_is": "simple explanation of this experience",
  "how_to_run": ["step 1", "step 2", "step 3", "step 4"],
  "improvements": ["improvement 1", "improvement 2"],
  "future_ideas": ["future idea 1", "future idea 2"]
}}
"""


def story_generation_prompt(experience_details: dict) -> str:
    return f"""
Experience details:
{experience_details}

Write an engaging, visitor-friendly story about this farm experience.

Return ONLY valid JSON with these exact keys:
{{
  "headline": "short compelling headline (max 10 words)",
  "story": "warm engaging description for visitors (2-3 paragraphs separated by \\n\\n)",
  "highlights": ["highlight 1", "highlight 2", "highlight 3"],
  "call_to_action": "one inviting sentence encouraging visitors to book or join"
}}
"""