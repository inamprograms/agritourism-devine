import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from app.services.ai.factory import get_ai_provider
from app.services.ai.prompts.system_prompts import (
    farm_advisor_system_prompt,
    experience_advisor_system_prompt,
    story_generator_system_prompt,
)
from app.services.ai.prompts.user_prompts import (
    farm_advisory_prompt,
    experience_advisory_prompt,
    story_generation_prompt,
)
from config import Config

logger = logging.getLogger(__name__)

# How long we wait for the AI before telling the farmer to try again.
# Set AI_TIMEOUT_SECONDS in config.py to change it.
AI_TIMEOUT_SECONDS = getattr(Config, "AI_TIMEOUT_SECONDS", 30)

# Calls run in these threads so we can stop waiting after the timeout.
_executor = ThreadPoolExecutor(max_workers=8)

# The one agreed reply shape for each assistant. The frontend always gets these keys.
FARM_REPLY = {"text": ["answer", "first_step"], "lists": ["improvements", "future_ideas"]}
EXPERIENCE_REPLY = {"text": ["answer", "what_it_is"], "lists": ["how_to_run", "improvements", "future_ideas"]}


class AIUnavailable(Exception):
    """The AI did not answer in time, failed, or sent nothing. Safe to show to the farmer."""
    user_message = "The AI helper is not available right now. Please try again in a minute."


def _json_candidates(text: str):
    """Possible JSON strings inside an AI reply: the whole text, a fenced block, or the {...} part."""
    cleaned = text.strip()
    yield cleaned
    if "```" in cleaned:
        inner = cleaned.split("```")[1]
        if inner.lstrip().lower().startswith("json"):
            inner = inner.lstrip()[4:]
        yield inner.strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        yield cleaned[start:end + 1]


def _shape(raw_text: str, spec: dict) -> dict:
    """
    Turn whatever the AI sent into the agreed reply shape:
    every text key is a string, every list key is a list of strings.
    If the reply is not JSON, the plain text becomes the answer.
    """
    parsed = None
    for candidate in _json_candidates(raw_text):
        try:
            value = json.loads(candidate)
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict):
            parsed = value
            break

    keys = spec["text"] + spec["lists"]
    out = {k: "" for k in spec["text"]}
    out.update({k: [] for k in spec["lists"]})

    if parsed is None or not any(k in parsed for k in keys):
        out["answer"] = raw_text.strip()
        return out

    for k in spec["text"]:
        v = parsed.get(k)
        out[k] = "" if v is None else str(v).strip()
    for k in spec["lists"]:
        v = parsed.get(k)
        if isinstance(v, str):
            v = [v]
        if isinstance(v, (list, tuple)):
            out[k] = [str(x).strip() for x in v if str(x).strip()]
    return out


class TransformAIBase:
    """Shared base for all Transform AI services."""

    def __init__(self):
        self.provider = get_ai_provider()
        self.temperature = Config.AI_TEMPERATURE

    def _complete(self, system: str, user: str, max_tokens: int = None) -> str:
        """Call the AI with a time limit. Raises AIUnavailable on timeout, error or empty reply."""
        extra = {"max_tokens": max_tokens} if max_tokens else {}  # only when a caller asks for it
        future = _executor.submit(
            self.provider.complete,
            system_prompt=system,
            user_prompt=user,
            temperature=self.temperature,
            **extra,
        )
        try:
            text = future.result(timeout=AI_TIMEOUT_SECONDS)
        except FutureTimeout:
            logger.warning("AI call timed out after %s seconds", AI_TIMEOUT_SECONDS)
            raise AIUnavailable("timeout")
        except Exception as e:
            logger.warning("AI call failed: %s", e, exc_info=True)
            raise AIUnavailable(str(e)) from e
        if not isinstance(text, str) or not text.strip():
            raise AIUnavailable("empty reply")
        return text

    def _parse_json_response(self, text: str) -> dict:
        """Used by the story service: JSON if possible, else the plain text."""
        for candidate in _json_candidates(text):
            try:
                value = json.loads(candidate)
            except (ValueError, TypeError):
                continue
            if isinstance(value, dict):
                return value
        return {"ai_response": text}


class TransformAdvisorService(TransformAIBase):
    """Farm transformation advisory: advises on the plan and its experiences."""

    def advise(self, user_prompt: str, transformation_summary: dict, language: str = "en", history=None) -> dict:
        """Farm-level advice. Always returns the FARM_REPLY keys."""
        system = farm_advisor_system_prompt(language)
        user = farm_advisory_prompt(user_prompt, transformation_summary, history)
        return _shape(self._complete(system, user), FARM_REPLY)

    def advise_experience(self, user_prompt: str, experience_details: dict, farm_context: dict = None,
                          language: str = "en", history=None) -> dict:
        """Single experience advice. Always returns the EXPERIENCE_REPLY keys."""
        system = experience_advisor_system_prompt(language)
        user = experience_advisory_prompt(user_prompt, experience_details, farm_context, history)
        return _shape(self._complete(system, user), EXPERIENCE_REPLY)


class TransformStoryService(TransformAIBase):
    """Experience post generation: the friendly text of the message a farmer sends to visitors."""

    def generate_story(self, experience_details: dict, farm_context: dict = None, language: str = "en") -> dict:
        system = story_generator_system_prompt(language)
        user = story_generation_prompt(experience_details, farm_context)
        return self._parse_json_response(self._complete(system, user, max_tokens=4000))


transform_advisor_service = TransformAdvisorService()
story_service = TransformStoryService()