def farm_advisory_prompt(user_prompt: str, transformation_summary: dict) -> str:
    """
    Farm-level advisory prompt.
    Now includes full farm context and farmer goals so AI gives
    personalized, grounded advice.
    """
    
    farm_ctx = transformation_summary.get("farm_context", {})
    experiences = transformation_summary.get("experiences_by_level", {})
    
    return f"""
FARMER'S SITUATION:
- Farm type: {farm_ctx.get("farm_type", "not specified")}
- Size: {farm_ctx.get("size_category", "not specified")}
- Crops grown: {", ".join(farm_ctx.get("crops", [])) or "none listed"}
- Animals: {farm_ctx.get("animals") or "none listed"}
- Road access: {farm_ctx.get("road_access", "not specified")}
- Distance from nearest city: {farm_ctx.get("distance_from_city_km", "unknown")} km
- Budget available: {farm_ctx.get("budget_range", "low")}
- Family members who can help: {farm_ctx.get("family_helpers", 0)}
- Prior visitor experience: {farm_ctx.get("visitor_experience", "none")}
- Primary goal: {farm_ctx.get("primary_goal", "income")}
- Timeline to start: {farm_ctx.get("timeline", "months")}

FARMER'S QUESTION OR DESCRIPTION:
{user_prompt}

CURRENT PERSONALIZED AGRITOURISM TRANSFORMATION PLAN (generated for this farm — DO NOT modify):
{experiences}

YOUR TASKS:
1. Directly answer the farmer's question based on THEIR specific situation
2. Identify the single best first step for THIS farmer (lowest risk, lowest effort, consider their budget and timeline)
3. Suggest 2-3 small practical improvements relevant to their farm assets
4. Note future possibilities marked as [FUTURE IDEA]

IMPORTANT: Your advice must reflect this farmer's actual budget ({farm_ctx.get("budget_range", "low")}),
their timeline ({farm_ctx.get("timeline", "months")}), and their visitor experience level 
({farm_ctx.get("visitor_experience", "none")}). Do not suggest expensive setups if budget is low.

Return ONLY valid JSON with these exact keys:
{{
  "answer": "direct, personalized answer to the farmer's question in 2-3 sentences",
  "first_step": "the single best thing to start with given their specific situation and why",
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "future_ideas": ["future idea 1", "future idea 2"]
}}
"""

def experience_advisory_prompt(user_prompt: str, experience_details: dict, farm_context: dict = None) -> str:
    """
    Single experience advisory prompt.
    Now includes farm context so AI can give advice that fits this farmer's reality.
    """
    ctx = farm_context or {}
    
    return f"""
FARMER'S SITUATION:
- Budget: {ctx.get("budget_range", "low")}
- Family helpers available: {ctx.get("family_helpers", 0)}
- Prior visitor experience: {ctx.get("visitor_experience", "none")}
- Farm type: {ctx.get("farm_type", "not specified")}
- Location: {ctx.get("province", "rural area")}

FARMER'S QUESTION:
{user_prompt}

SELECTED EXPERIENCE DETAILS (DO NOT modify this data):
- Title: {experience_details.get("title")}
- Type: {experience_details.get("type")}
- Level: {experience_details.get("level")}
- Monetization: {experience_details.get("monetization")}
- Description: {experience_details.get("description", "not available")}
- Setup cost: {experience_details.get("setup_cost_range", "unknown")}
- Time to launch: {experience_details.get("time_to_launch", "unknown")}
- Estimated revenue: {experience_details.get("estimated_revenue", "unknown")}
- Season: {experience_details.get("season", "year_round")}

YOUR TASKS:
1. Directly answer the farmer's question about this experience
2. Explain what this experience involves in simple, plain language
3. Give a step-by-step guide to running it — practical and realistic
4. Suggest small improvements that fit their budget ({ctx.get("budget_range", "low")})
5. Note future possibilities marked as [FUTURE IDEA]

Return ONLY valid JSON with these exact keys:
{{
  "answer": "direct answer to the farmer's question in 2-3 sentences",
  "what_it_is": "simple explanation of this experience in 2-3 sentences",
  "how_to_run": ["step 1", "step 2", "step 3", "step 4"],
  "improvements": ["improvement 1 (budget-appropriate)", "improvement 2"],
  "future_ideas": ["future idea 1", "future idea 2"]
}}
"""

def story_generation_prompt(experience_details: dict, farm_context: dict = None) -> str:
    """
    Visitor-facing story generation prompt.
    Now includes farm location/type for culturally grounded storytelling.
    """
    ctx = farm_context or {}
    
    return f"""
FARM CONTEXT:
- Farm type: {ctx.get("farm_type", "mixed farm")}
- Location: {ctx.get("province", "rural area")}
- Crops: {", ".join(ctx.get("crops", [])) or "various crops"}
- Animals: {ctx.get("animals") or "farm animals"}

EXPERIENCE DETAILS:
- Title: {experience_details.get("title")}
- Type: {experience_details.get("type")}
- Description: {experience_details.get("description", "")}
- Season: {experience_details.get("season", "year_round")}
- Level: {experience_details.get("level")}

Write an engaging, visitor-friendly story about this farm experience that makes 
urban visitors excited to visit. Capture the authentic beauty of rural farm 
life — the sights, smells, sounds, and warmth of the people.

Write an engaging, visitor-friendly story about this farm experience.

Return ONLY valid JSON with these exact keys:
{{
  "headline": "short compelling headline (max 10 words)",
  "story": "warm engaging description for visitors (2-3 paragraphs separated by \\n\\n)",
  "highlights": ["highlight 1", "highlight 2", "highlight 3"],
  "call_to_action": "one inviting sentence encouraging visitors to book or join"
}}
"""

def evaluation_judge_prompt(question: str, context: str, response: str) -> str:
    return f"""You are an evaluation judge for an agritourism AI assistant.
Score the following AI interaction on these 5 dimensions.

QUESTION: {question}

RETRIEVED CONTEXT: {context}

AI RESPONSE: {response}

Score each dimension from 0.0 to 1.0 and give a one-sentence reason.

Dimensions:
1. faithfulness: Does the response avoid contradicting or misrepresenting 
   the provided context? The AI is allowed to add helpful framing and 
   supplementary explanation from general knowledge — that is expected behavior.
   Only score low if the response states something that directly conflicts 
   with what the context says, or makes up specific numbers/facts that 
   contradict the context.
   (1.0 = no contradictions, 0.5 = minor additions beyond context, 
    0.0 = directly contradicts context facts)

2. answer_relevance: Does the response directly address the question asked?
   (1.0 = fully answers it, 0.0 = completely off-topic)
   
3. context_precision: Based on the retrieved context provided above, was it 
   relevant and useful for answering this specific question?
   Look at whether the context contains information about the topic asked.
   Do not penalize if the AI added information beyond the context — 
   only evaluate whether the context itself was a good match for the question.
   (1.0 = context directly addresses the question topic,
    0.5 = context partially relevant, 
    0.0 = context completely unrelated to the question)

4. completeness: Does the response fully address the question without cutting off or leaving gaps?
   (1.0 = complete answer, 0.0 = incomplete or vague)

5. safety: Does the response stay within agritourism/farming topics and avoid harmful content?
   (1.0 = fully safe and on-topic, 0.0 = off-topic or harmful)

Scoring guidance — be fair and calibrated:
- A response that clearly addresses the question in plain language scores 0.7 or higher 
  on answer_relevance, even if it could theoretically be more detailed.
- Only score 0.0 if the response completely ignores the question or is factually wrong.
- A conversational, friendly tone is correct for this farmer-facing chatbot — 
  do not penalize it.
- A response that gives accurate, useful information scores at least 0.6 on completeness
  even if it does not cover every edge case.
- Faithfulness score of 0.0 means the response actively contradicts the context — 
  not just that it added helpful framing around it.
- When in doubt, score higher not lower. These are real farmer conversations.

Return ONLY valid JSON, no extra text:
{{
  "faithfulness": {{"score": 0.0, "reason": "one sentence"}},
  "answer_relevance": {{"score": 0.0, "reason": "one sentence"}},
  "context_precision": {{"score": 0.0, "reason": "one sentence"}},
  "completeness": {{"score": 0.0, "reason": "one sentence"}},
  "safety": {{"score": 0.0, "reason": "one sentence"}}
}}"""


def evaluation_judge_prompt_no_context(question: str, response: str) -> str:
    return f"""You are an evaluation judge for an agritourism AI assistant.
Score the following AI interaction on these 3 dimensions.
There was no retrieved context — the AI answered from general knowledge.

QUESTION: {question}

AI RESPONSE: {response}

Score each dimension from 0.0 to 1.0 and give a one-sentence reason.

Dimensions:
1. answer_relevance: Does the response directly address the question asked?
   (1.0 = fully answers it, 0.0 = completely off-topic)

2. completeness: Does the response fully address the question without cutting off or leaving gaps?
   (1.0 = complete answer, 0.0 = incomplete or vague)

3. safety: Does the response stay within agritourism/farming topics and avoid harmful content?
   (1.0 = fully safe and on-topic, 0.0 = off-topic or harmful)

Scoring guidance — be fair and calibrated:
- A response that clearly addresses the question in plain language scores 0.7 or higher 
  on answer_relevance, even if it could theoretically be more detailed.
- Only score 0.0 if the response completely ignores the question or is factually wrong.
- A conversational, friendly tone is correct for this farmer-facing chatbot — 
  do not penalize it.
- A response that gives accurate, useful information scores at least 0.6 on completeness
  even if it does not cover every edge case.
- When in doubt, score higher not lower. These are real farmer conversations.

Return ONLY valid JSON, no extra text:
{{
  "answer_relevance": {{"score": 0.0, "reason": "one sentence"}},
  "completeness": {{"score": 0.0, "reason": "one sentence"}},
  "safety": {{"score": 0.0, "reason": "one sentence"}}
}}"""


def guardrail_check_prompt(message: str) -> str:
    return f"""You are a safety classifier for an agritourism platform AI assistant.

Analyze this user message and classify it.

MESSAGE: {message}

Check for:
1. is_safe: Is the message free from harmful, abusive, or malicious intent?
   (true = safe, false = unsafe)

2. is_on_topic: Is the message related to agritourism, farming, carbon credits,
   or the platform? General greetings are also acceptable.
   (true = on topic, false = off topic)

3. reason: One sentence explaining your decision if either check fails.
   If both pass, reason can be "Message is safe and on topic."

Return ONLY valid JSON, no extra text:
{{
  "is_safe": true,
  "is_on_topic": true,
  "reason": "one sentence"
}}"""