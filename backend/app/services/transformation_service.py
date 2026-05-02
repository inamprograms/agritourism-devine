# services/transformation_service.py

class TransformationService:
    """
    Personalized farm -> agritourism transformation engine.

    How it works:
    - Each experience has eligibility conditions checked against real farm data
    - Each experience has a score — higher score = better fit for this farm
    - Only eligible experiences are returned, ordered by score (best first)
    - Experiences are grouped into 3 levels (phases) for a roadmap feel
    """

    # ----------------------------------------------------------------
    # EXPERIENCE LIBRARY
    # Pakistan-specific agritourism experiences with eligibility rules
    # ----------------------------------------------------------------
    EXPERIENCE_LIBRARY = [

        # ============================================================
        # LEVEL 1 — Zero / Near-Zero Investment (Start immediately)
        # ============================================================
        {
            "title": "Farm Walk & Crop Tour",
            "type": "educational",
            "level": 1,
            "monetization": "free",
            "description": "Guided walk around the farm explaining crops, farming methods, and daily farm life to visitors.",
            "requirements": ["basic signage", "farmer available to guide"],
            "season": "year_round",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Free entry — builds reputation and visitor base",
            # Eligibility: any farm qualifies
            "eligibility": lambda f: True,
            # Score: more scenic = more attractive walk
            "score": lambda f: 10 + (5 if f.get("scenic_features") else 0),
        },
        {
            "title": "Fresh Produce Tasting",
            "type": "activity",
            "level": 1,
            "monetization": "free",
            "description": "Let visitors taste freshly picked fruits or vegetables straight from the farm.",
            "requirements": ["seasonal crop ready", "basic hygiene setup"],
            "season": "harvest_season",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Free — leads to direct produce sales",
            "eligibility": lambda f: bool(f.get("crops")),
            "score": lambda f: 12 + (5 if _has_fruit_crop(f) else 0),
        },
        {
            "title": "Animal Feeding Session",
            "type": "activity",
            "level": 1,
            "monetization": "paid",
            "description": "Visitors feed and interact with farm animals. Great for families and children.",
            "requirements": ["farm animals present", "safe enclosure area"],
            "season": "year_round",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Rs. 200–500 per visitor",
            "eligibility": lambda f: bool(f.get("animals")),
            "score": lambda f: 14 + (5 if _animal_count(f) >= 5 else 0),
        },
        {
            "title": "Milking Demonstration",
            "type": "activity",
            "level": 1,
            "monetization": "paid",
            "description": "Show visitors how cows or goats are milked. Offer fresh milk/lassi to drink.",
            "requirements": ["dairy animals (cows or goats)", "clean milking area"],
            "season": "year_round",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Rs. 300–700 per visitor including fresh milk",
            "eligibility": lambda f: _has_dairy_animal(f),
            "score": lambda f: 16,
        },
        {
            "title": "Traditional Farming Tool Display",
            "type": "educational",
            "level": 1,
            "monetization": "free",
            "description": "Display traditional farming tools and explain their history and use to visitors.",
            "requirements": ["collection of traditional tools"],
            "season": "year_round",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Free — adds educational value to other paid experiences",
            "eligibility": lambda f: True,
            "score": lambda f: 8,
        },
        {
            "title": "Nature & Bird Walk",
            "type": "nature",
            "level": 1,
            "monetization": "paid",
            "description": "Guided walk focused on trees, birds, and natural features of the farm.",
            "requirements": ["trees or natural features present"],
            "season": "year_round",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Rs. 300–600 per visitor",
            "eligibility": lambda f: bool(f.get("existing_trees")) or bool(f.get("scenic_features")),
            "score": lambda f: 10 + (8 if bool(f.get("scenic_features")) else 0),
        },

        # ============================================================
        # LEVEL 2 — Small Investment (Rs. 5,000–30,000)
        # ============================================================
        {
            "title": "Pick-Your-Own Harvest Day",
            "type": "activity",
            "level": 2,
            "monetization": "paid",
            "description": "Visitors pick their own fruits or vegetables and take them home. Highly popular with urban families.",
            "requirements": ["fruit or vegetable crop", "harvest season", "baskets/bags for visitors"],
            "season": "harvest_season",
            "setup_cost_range": "low",
            "time_to_launch": "1 month",
            "estimated_revenue": "Rs. 500–1,500 per family + produce sales",
            "eligibility": lambda f: _has_fruit_crop(f) or _has_vegetable_crop(f),
            "score": lambda f: 18 + (5 if _has_fruit_crop(f) else 0) + (3 if _near_city(f) else 0),
        },
        {
            "title": "Desi Cooking Class",
            "type": "workshop",
            "level": 2,
            "monetization": "paid",
            "description": "Teach visitors to cook traditional recipes using fresh farm produce. Ideal for urban visitors wanting authentic experiences.",
            "requirements": ["outdoor cooking setup", "farm produce available", "family member to teach"],
            "season": "year_round",
            "setup_cost_range": "low",
            "time_to_launch": "1 month",
            "estimated_revenue": "Rs. 1,000–2,500 per person",
            "eligibility": lambda f: bool(f.get("crops")) and f.get("family_helpers", 0) >= 1,
            "score": lambda f: 16 + (4 if _near_city(f) else 0),
        },
        {
            "title": "Fresh Dairy Experience (Chai & Lassi)",
            "type": "activity",
            "level": 2,
            "monetization": "paid",
            "description": "Visitors watch milk being collected, then enjoy fresh chai or lassi made on the spot.",
            "requirements": ["dairy animals", "basic outdoor seating", "gas/wood fire setup"],
            "season": "year_round",
            "setup_cost_range": "low",
            "time_to_launch": "1 month",
            "estimated_revenue": "Rs. 300–800 per visitor",
            "eligibility": lambda f: _has_dairy_animal(f),
            "score": lambda f: 17,
        },
        {
            "title": "School Educational Visit Program",
            "type": "educational",
            "level": 2,
            "monetization": "paid",
            "description": "Structured program for school groups — farm tour, hands-on activities, and a simple meal.",
            "requirements": ["open space for groups", "basic toilet facility", "at least 1 guide"],
            "season": "year_round",
            "setup_cost_range": "low",
            "time_to_launch": "1 month",
            "estimated_revenue": "Rs. 300–600 per student (groups of 20–50)",
            "eligibility": lambda f: _has_open_space(f) and _near_city(f),
            "score": lambda f: 15 + (5 if _has_toilet(f) else 0),
        },
        {
            "title": "Sunset Farm Photography Walk",
            "type": "nature",
            "level": 2,
            "monetization": "paid",
            "description": "Guided photography walk during golden hour. Very popular with young urban visitors.",
            "requirements": ["scenic features or open landscape", "accessible path"],
            "season": "year_round",
            "setup_cost_range": "zero",
            "time_to_launch": "1-2 weeks",
            "estimated_revenue": "Rs. 500–1,000 per visitor",
            "eligibility": lambda f: bool(f.get("scenic_features")) or bool(f.get("existing_trees")),
            "score": lambda f: 13 + (7 if bool(f.get("scenic_features")) else 0) + (3 if _near_city(f) else 0),
        },
        {
            "title": "On-Farm Farmers Market",
            "type": "market",
            "level": 2,
            "monetization": "paid",
            "description": "A small weekly or monthly market where visitors buy fresh produce, dairy, and homemade goods directly from your farm.",
            "requirements": ["variety of produce", "basic stall setup", "accessible road"],
            "season": "year_round",
            "setup_cost_range": "low",
            "time_to_launch": "1 month",
            "estimated_revenue": "Rs. 5,000–20,000 per market day",
            "eligibility": lambda f: bool(f.get("crops")) and f.get("road_access") in ["pucca", "highway_nearby"],
            "score": lambda f: 16 + (5 if _near_city(f) else 0),
        },

        # ============================================================
        # LEVEL 3 — Growth Investment (Rs. 30,000–150,000+)
        # ============================================================
        {
            "title": "Weekend Farm Experience Package",
            "type": "package",
            "level": 3,
            "monetization": "paid",
            "description": "A full-day package combining farm tour, activity, meal, and take-home produce. Marketed to urban families for weekends.",
            "requirements": ["multiple activities ready", "meal capability", "accessible road", "parking space"],
            "season": "year_round",
            "setup_cost_range": "medium",
            "time_to_launch": "3 months",
            "estimated_revenue": "Rs. 3,000–8,000 per family",
            "eligibility": lambda f: _near_city(f) and f.get("road_access") in ["pucca", "highway_nearby"],
            "score": lambda f: 20 + (5 if _has_dairy_animal(f) else 0) + (5 if bool(f.get("crops")) else 0),
        },
        {
            "title": "Seasonal Harvest Festival",
            "type": "event",
            "level": 3,
            "monetization": "paid",
            "description": "An annual or bi-annual event celebrating harvest season. Includes picking, food, music, and cultural activities.",
            "requirements": ["seasonal crop", "open space for 50+ visitors", "road access", "basic facilities"],
            "season": "harvest_season",
            "setup_cost_range": "medium",
            "time_to_launch": "3 months",
            "estimated_revenue": "Rs. 500–1,500 per visitor (100–500 visitors per event)",
            "eligibility": lambda f: (bool(f.get("crops")) and _has_open_space(f) and
                                      f.get("road_access") in ["pucca", "highway_nearby"]),
            "score": lambda f: 19 + (6 if _near_city(f) else 0),
        },
        {
            "title": "Overnight Farm Stay",
            "type": "lodging",
            "level": 3,
            "monetization": "paid",
            "description": "Guests stay overnight on the farm — sleep under stars or in a spare room. Experience early morning farming life.",
            "requirements": ["spare room or safe tent space", "basic toilet", "family comfortable with guests overnight"],
            "season": "year_round",
            "setup_cost_range": "medium",
            "time_to_launch": "3 months",
            "estimated_revenue": "Rs. 3,000–8,000 per night per family",
            "eligibility": lambda f: (_has_structure(f, "house") or _has_structure(f, "guest_room")) and
                                     _has_toilet(f) and
                                     f.get("visitor_experience", "none") != "none",
            "score": lambda f: 22 + (5 if bool(f.get("scenic_features")) else 0),
        },
        {
            "title": "Corporate Team-Building Day",
            "type": "package",
            "level": 3,
            "monetization": "paid",
            "description": "Full-day program for corporate groups — farm activities, team challenges, and a farm-to-table meal.",
            "requirements": ["open space", "multiple activities", "accessible road", "capacity for 20+ people"],
            "season": "year_round",
            "setup_cost_range": "medium",
            "time_to_launch": "3 months",
            "estimated_revenue": "Rs. 15,000–40,000 per group",
            "eligibility": lambda f: (_has_open_space(f) and _near_city(f) and
                                      f.get("road_access") in ["pucca", "highway_nearby"] and
                                      f.get("visitor_experience", "none") != "none"),
            "score": lambda f: 18 + (8 if f.get("distance_from_city_km", 999) <= 30 else 0),
        },
    ]

    def __init__(self):
        pass

    def generate_experiences(self, farm_data: dict) -> list:
        """
        Main method — evaluates every experience in the library
        against this specific farm's data.

        Returns a list of eligible experiences sorted by:
        1. Level (ascending — easiest first)
        2. Score (descending — best fit first within each level)
        """
        eligible = []

        for exp in self.EXPERIENCE_LIBRARY:
            try:
                if exp["eligibility"](farm_data):
                    score = exp["score"](farm_data)
                    result = {
                        "title": exp["title"],
                        "type": exp["type"],
                        "level": exp["level"],
                        "monetization": exp["monetization"],
                        "description": exp["description"],
                        "requirements": exp["requirements"],
                        "season": exp["season"],
                        "setup_cost_range": exp["setup_cost_range"],
                        "time_to_launch": exp["time_to_launch"],
                        "estimated_revenue": exp["estimated_revenue"],
                        "enabled": False,
                        "_score": score,
                    }
                    eligible.append(result)
            except Exception:
                # Skip any experience that errors during evaluation
                continue

        # Sort: level first, then score descending within each level
        eligible.sort(key=lambda x: (x["level"], -x["_score"]))

        # Remove internal score field before returning
        for exp in eligible:
            exp.pop("_score", None)

        return eligible

    def get_ai_summary(self, experiences: list, farm_data: dict = None) -> dict:
        """
        Converts generated experiences into a structured summary
        for AI consumption — now includes farm context.
        """
        summary = {
            "farm_context": {
                "farm_type": farm_data.get("farm_type") if farm_data else None,
                "size_category": farm_data.get("size_category") if farm_data else None,
                "crops": farm_data.get("crops", []) if farm_data else [],
                "animals": farm_data.get("animals", {}) if farm_data else {},
                "road_access": farm_data.get("road_access") if farm_data else None,
                "distance_from_city_km": farm_data.get("distance_from_city_km") if farm_data else None,
                "budget_range": farm_data.get("budget_range") if farm_data else None,
                "visitor_experience": farm_data.get("visitor_experience") if farm_data else None,
                "primary_goal": farm_data.get("primary_goal") if farm_data else None,
                "timeline": farm_data.get("timeline") if farm_data else None,
            },
            "experiences_by_level": {}
        }

        for exp in experiences:
            level = f"Level {exp['level']}"
            if level not in summary["experiences_by_level"]:
                summary["experiences_by_level"][level] = []
            summary["experiences_by_level"][level].append({
                "title": exp["title"],
                "type": exp["type"],
                "monetization": exp["monetization"],
                "estimated_revenue": exp.get("estimated_revenue"),
                "time_to_launch": exp.get("time_to_launch"),
                "setup_cost_range": exp.get("setup_cost_range"),
            })

        return summary


# ----------------------------------------------------------------
# HELPER FUNCTIONS — used in eligibility and score lambdas
# ----------------------------------------------------------------

def _has_fruit_crop(f: dict) -> bool:
    fruit_crops = {"mango", "guava", "citrus", "orange", "banana", "strawberry",
                   "apricot", "peach", "plum", "pomegranate", "date", "lemon"}
    crops = [c.lower() for c in f.get("crops", [])]
    return any(c in fruit_crops for c in crops)


def _has_vegetable_crop(f: dict) -> bool:
    veg_crops = {"tomato", "potato", "onion", "carrot", "spinach", "coriander",
                 "chilli", "garlic", "cucumber", "peas", "corn"}
    crops = [c.lower() for c in f.get("crops", [])]
    return any(c in veg_crops for c in crops)


def _has_dairy_animal(f: dict) -> bool:
    animals = {k.lower(): v for k, v in f.get("animals", {}).items()}
    return animals.get("cows", 0) > 0 or animals.get("goats", 0) > 0 or animals.get("buffalo", 0) > 0


def _animal_count(f: dict) -> int:
    return sum(f.get("animals", {}).values())


def _near_city(f: dict) -> bool:
    dist = f.get("distance_from_city_km")
    if dist is None:
        return True  # assume near if unknown
    return dist <= 60


def _has_open_space(f: dict) -> bool:
    structures = [s.lower() for s in f.get("structures", [])]
    return "open_field" in structures or len(structures) == 0  # open if no structures listed


def _has_structure(f: dict, structure_name: str) -> bool:
    structures = [s.lower() for s in f.get("structures", [])]
    return structure_name.lower() in structures


def _has_toilet(f: dict) -> bool:
    structures = [s.lower() for s in f.get("structures", [])]
    return "toilet" in structures or "bathroom" in structures or "washroom" in structures