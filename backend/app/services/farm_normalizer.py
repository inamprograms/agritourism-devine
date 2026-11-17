"""
services/farm_normalizer.py

Cleans messy farm input BEFORE the rule engine sees it.
- Pure function: never writes to the database, never changes the stored farm.
- Understands plurals, common typos, counts typed inside names ("5 buffaloes"),
  and common Urdu/Roman-Urdu names.
- Anything it cannot recognise is returned in `unrecognized` so it can be logged
  and the dictionaries below can be extended from what farmers really type.
"""
import re
from difflib import get_close_matches

# ---------------- Known names (single source of truth) ----------------
ANIMALS = {"cow", "buffalo", "goat", "sheep", "chicken", "duck", "horse",
           "camel", "donkey", "rabbit", "turkey"}
ANIMAL_SYNONYMS = {
    "bhains": "buffalo", "bhens": "buffalo", "bhainsa": "buffalo",
    "gai": "cow", "gaye": "cow", "gaay": "cow", "gae": "cow",
    "bakri": "goat", "bakra": "goat", "bakriyan": "goat",
    "bher": "sheep", "bheri": "sheep", "bhed": "sheep",
    "murghi": "chicken", "murgi": "chicken", "hen": "chicken", "hens": "chicken",
    "ghora": "horse", "unt": "camel", "gadha": "donkey",
    "بھینس": "buffalo", "گائے": "cow", "بکری": "goat", "مرغی": "chicken",
}

FRUIT_CROPS = {"mango", "guava", "citrus", "orange", "banana", "strawberry",
               "apricot", "peach", "plum", "pomegranate", "date", "lemon",
               "apple", "grape", "avocado"}
VEGETABLE_CROPS = {"tomato", "potato", "onion", "carrot", "spinach", "coriander",
                   "chilli", "garlic", "cucumber", "peas", "corn"}
OTHER_CROPS = {"wheat", "rice", "cotton", "sugarcane", "maize", "barley",
               "mustard", "sunflower", "fodder", "lentil", "chickpea"}
CROP_SYNONYMS = {
    "aam": "mango", "amrood": "guava", "kinnow": "citrus", "malta": "citrus",
    "seb": "apple", "anar": "pomegranate", "kela": "banana", "khajoor": "date",
    "angoor": "grape", "tamatar": "tomato", "aloo": "potato", "pyaz": "onion",
    "gajar": "carrot", "palak": "spinach", "dhaniya": "coriander",
    "mirch": "chilli", "lehsun": "garlic", "kheera": "cucumber", "matar": "peas",
    "makai": "maize", "gandum": "wheat", "chawal": "rice", "ganna": "sugarcane",
}
ALL_CROPS = FRUIT_CROPS | VEGETABLE_CROPS | OTHER_CROPS

TREES = {"mango", "guava", "neem", "eucalyptus", "banyan", "peepal", "shisham",
         "acacia", "citrus", "jamun", "mulberry", "lemon", "orange", "banana",
         "apple", "pomegranate", "bamboo", "palm", "date", "peach", "plum"}
TREE_SYNONYMS = {"aam": "mango", "amrood": "guava", "sheesham": "shisham",
                 "kikar": "acacia", "pipal": "peepal", "bohr": "banyan",
                 "safeda": "eucalyptus"}


# ---------------- Small helpers ----------------
def _clean_text(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _singular(w):
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("oes"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def _is_junk(s):
    return len(s) < 3 or not re.search(r"[a-z؀-ۿ]", s)


def _match(word, known, synonyms, cutoff=0.7):
    """Return the canonical name for `word`, or None if unknown."""
    for cand in (word, _singular(word)):
        if cand in synonyms:
            return synonyms[cand]
        if cand in known:
            return cand
    if len(word) >= 5:
        pool = list(known) + list(synonyms)
        close = get_close_matches(_singular(word), pool, n=1, cutoff=cutoff)
        if close:
            return synonyms.get(close[0], close[0])
    return None


def _match_phrase(phrase, known, synonyms):
    """Try the whole phrase, then each word ('dairy cow' -> 'cow')."""
    hit = _match(phrase, known, synonyms)
    if hit:
        return hit
    for w in reversed(phrase.split()):
        hit = _match(w, known, synonyms)
        if hit:
            return hit
    return None


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _split_count(raw_name, stored_count):
    """'5 bafflows' with stored count 1  ->  ('bafflows', 5)."""
    name = _clean_text(raw_name)
    count = _to_int(stored_count)
    if count is None:
        count = 1
    m = re.match(r"^(\d+)\s*x?\s*(.+)$", name) or re.match(r"^(.+?)\s*[:x]?\s*(\d+)$", name)
    if m:
        a, b = m.group(1), m.group(2)
        number, text = (int(a), b) if a.isdigit() else (int(b), a)
        name = text.strip(" :")
        if count == 1:  # the form stores 1 when the number was typed inside the name
            count = number
    return name, count


# ---------------- Main entry ----------------
def normalize_farm(farm: dict):
    """
    Returns (clean_farm, unrecognized).
    clean_farm is a COPY of the farm with:
      crops          -> list of lowercase canonical names (unknown ones kept, flagged)
      animals        -> {canonical_name: count}  (only recognised animals are kept)
      existing_trees -> list of lowercase names (junk like 'dd' removed)
      distance_from_city_km, family_helpers -> int or None
      visitor_experience -> lowercase string or None
    """
    f = dict(farm or {})
    unrecognized = {"crops": [], "animals": [], "trees": []}

    # crops
    crops = []
    for raw in f.get("crops") or []:
        c = _clean_text(raw)
        if _is_junk(c):
            unrecognized["crops"].append(c)
            continue
        hit = _match(c, ALL_CROPS, CROP_SYNONYMS)
        if hit is None:
            unrecognized["crops"].append(c)
            hit = c  # keep it: a real crop we simply don't know yet
        if hit not in crops:
            crops.append(hit)
    f["crops"] = crops

    # animals (only recognised animals count: feeding/milking rules need real, safe animals)
    animals = {}
    for raw_name, raw_count in (f.get("animals") or {}).items():
        name, count = _split_count(raw_name, raw_count)
        hit = None if _is_junk(name) else _match_phrase(name, ANIMALS, ANIMAL_SYNONYMS)
        if hit is None:
            unrecognized["animals"].append(_clean_text(raw_name))
            continue
        if count > 0:
            animals[hit] = animals.get(hit, 0) + count
    f["animals"] = animals

    # trees
    trees = []
    for raw in f.get("existing_trees") or []:
        t = _clean_text(raw)
        if _is_junk(t):
            unrecognized["trees"].append(t)
            continue
        hit = _match(t, TREES, TREE_SYNONYMS, cutoff=0.75)
        if hit is None:
            unrecognized["trees"].append(t)
            hit = t
        if hit not in trees:
            trees.append(hit)
    f["existing_trees"] = trees

    # structures / scenic features: pick-list values, just make them consistent
    for key in ("structures", "scenic_features"):
        f[key] = [_clean_text(x).replace(" ", "_") for x in (f.get(key) or [])]

    # simple fields
    f["road_access"] = _clean_text(f["road_access"]).replace(" ", "_") if f.get("road_access") else None
    f["distance_from_city_km"] = _to_int(f.get("distance_from_city_km"))
    f["family_helpers"] = _to_int(f.get("family_helpers"))
    ve = f.get("visitor_experience")
    f["visitor_experience"] = _clean_text(ve) if ve else None

    unrecognized = {k: v for k, v in unrecognized.items() if v}
    return f, unrecognized