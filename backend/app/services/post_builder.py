# services/post_builder.py
#
# Builds the message a farmer can send to visitors (WhatsApp, SMS, Facebook).
#
# Rule: the AI writes ONLY the friendly text. The facts that matter to a
# visitor (farm name, place, price, phone) are added by this code from the
# database, so the AI can never invent or change them. If a fact is missing,
# a visible [placeholder] is written instead, and the missing item is
# reported so the page can warn the farmer.

import re

MAX_SHORT_WORDS = 60
MAX_LONG_WORDS = 130

PRICE_PLACEHOLDER = "[add your price]"
PHONE_PLACEHOLDER = "[add your phone number]"
LOCATION_PLACEHOLDER = "[add your village or area]"

# Any AI sentence with money words or ANY digit is removed. Prices, phone numbers,
# dates and times come from the database or the farmer, never from the AI.
_MONEY = re.compile(r"(\$|€|£|\brs\.?\b|\bpkr\b|\busd\b|\bzar\b|\brand\b|\bdollars?\b|\brupees?\b)", re.I)
_DIGIT = re.compile(r"\d")


# Used only when the AI is unavailable or gives nothing usable: one plain sentence
# about what visitors do. Facts only, no marketing claims.
FALLBACK_LINES = {
    "Farm Walk & Crop Tour": "Join a guided walk around our farm to see the crops and learn how we farm.",
    "Fresh Produce Tasting": "Taste fresh fruits or vegetables picked on our farm.",
    "Animal Feeding Session": "Meet our farm animals and help feed them.",
    "Milking Demonstration": "See how milking is done on our farm.",
    "Traditional Farming Tool Display": "See traditional farming tools and hear how they are used.",
    "Nature & Bird Walk": "Walk through our trees and fields to look for birds and plants.",
    "Pick-Your-Own Harvest Day": "Pick your own fruits or vegetables and take them home.",
    "Desi Cooking Class": "Cook a traditional dish with fresh farm produce.",
    "Fresh Dairy Experience (Chai & Lassi)": "See milk being collected and enjoy fresh chai or lassi.",
    "School Educational Visit Program": "Bring your school class for a farm visit with a walk and a hands-on activity.",
    "Sunset Farm Photography Walk": "Join an evening walk to take photos of our farm at sunset.",
    "On-Farm Farmers Market": "Buy fresh produce and farm goods directly from our farm.",
    "Weekend Farm Experience Package": "Spend a full day on our farm with a tour, an activity and a meal.",
    "Seasonal Harvest Festival": "Join us on the farm for a harvest-time gathering.",
    "Overnight Farm Stay": "Stay a night on our farm.",
    "Corporate Team-Building Day": "Bring your team for a day on our farm with simple activities.",
}


def fallback_post(title):
    """Plain message used when the AI cannot write one."""
    line = FALLBACK_LINES.get(title) or "Come and spend a day on our farm."
    return {"post": f"{line} Come and see our farm."}


def _clean(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def _format_price(price):
    try:
        p = float(price)
    except (TypeError, ValueError):
        return None
    if p == 0:
        return "Free"
    amount = str(int(p)) if p == int(p) else f"{p:.2f}"
    return f"${amount} per visitor"


def build_post_facts(farm, profile, experience, phone):
    """Collect the facts that go under the message, and what is missing."""
    farm = farm or {}
    profile = profile or {}
    experience = experience or {}
    missing = []

    name = _clean(farm.get("name")) or "My farm"
    location = _clean(farm.get("location")) or _clean(profile.get("province"))
    if not location:
        missing.append("location")

    price_line = _format_price(experience.get("price")) if experience.get("price") is not None else None
    if price_line is None and experience.get("monetization") == "free":
        price_line = "Free"
    if price_line is None:
        missing.append("price")

    phone = _clean(phone)
    if not phone:
        missing.append("phone")

    return {
        "farm_name": name,
        "location": location,
        "price_line": price_line,
        "phone": phone,
        "missing": missing,
    }


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _words(text):
    return len(text.split())


def _tidy_body(text, max_words):
    """Drop sentences with money words or digits, then keep whole sentences up to max_words."""
    kept = [s for s in _sentences(text) if not _MONEY.search(s) and not _DIGIT.search(s)]
    out, count = [], 0
    for s in kept:
        n = _words(s)
        if out and count + n > max_words:
            break
        if not out and n > max_words:
            return " ".join(s.split()[:max_words]).rstrip(",;:") + "."
        out.append(s)
        count += n
    return " ".join(out)


def _footer(facts):
    place = facts["location"] or LOCATION_PLACEHOLDER
    lines = [
        f"Farm: {facts['farm_name']}, {place}",
        f"Price: {facts['price_line'] or PRICE_PLACEHOLDER}",
        f"Contact: {facts['phone'] or PHONE_PLACEHOLDER}",
    ]
    return "\n".join(lines)


def assemble_post(ai, facts):
    """
    ai    -> dict parsed from the AI: {"post": "...", "longer_post": "..."}
    facts -> from build_post_facts
    Returns {"post", "longer_post", "missing"} or None if the AI gave nothing usable.
    """
    if not isinstance(ai, dict) or not isinstance(ai.get("post"), str):
        return None
    short = _tidy_body(ai["post"], MAX_SHORT_WORDS)
    if not short:
        return None
    footer = _footer(facts)
    longer = None
    if isinstance(ai.get("longer_post"), str):
        longer_body = _tidy_body(ai["longer_post"], MAX_LONG_WORDS)
        if longer_body:
            longer = f"{longer_body}\n\n{footer}"
    return {
        "post": f"{short}\n\n{footer}",
        "longer_post": longer,
        "missing": facts["missing"],
    }
