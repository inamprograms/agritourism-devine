"""
Languages the AI can reply in (farm AI, experience AI and story AI use this one list).

Only codes marked enabled are accepted. Anything else falls back to English, so a
wrong or made-up value from the browser can never change the AI instructions.
To switch on a coming-soon language later: set "enabled": True here and in the
frontend list (src/config/languages.ts).
"""

DEFAULT_LANGUAGE = "en"

# "prompt" is the exact words put into the AI instructions.
LANGUAGES = {
    "en": {"enabled": True, "prompt": "English"},
    "ur": {"enabled": True, "prompt": "Urdu (write in Urdu script, with simple everyday words)"},
    "zu": {"enabled": True, "prompt": "isiZulu (Zulu), with simple everyday words"},
    # Coming soon: listed so the platform shows them, but not accepted yet.
    "tn": {"enabled": False, "prompt": "Setswana"},
    "st": {"enabled": False, "prompt": "Sesotho"},
    "xh": {"enabled": False, "prompt": "isiXhosa"},
}


def clean_language(code):
    """Return a language code that is enabled. Anything else becomes English."""
    if isinstance(code, str):
        code = code.strip().lower()
        entry = LANGUAGES.get(code)
        if entry and entry["enabled"]:
            return code
    return DEFAULT_LANGUAGE


def prompt_name(code):
    """Language name for the AI instructions."""
    return LANGUAGES[clean_language(code)]["prompt"]