# services/experience_content.py
#
# The words a farmer reads for each experience: three first steps for this
# week, safety notes, and the "why this fits you" sentence.
#
# DRAFT CONTENT. Written to be simple and careful, but NOT yet reviewed by
# local experts. Local reviewers should read and correct this file
# (it is the single place to edit) before it is shown as trusted advice.
# Costs and prices are never stated here.

LOCAL_RULES_NOTE = (
    "Check with your local authority or village council if you are not sure "
    "whether you need permission for visitors, food or overnight guests."
)

# title -> {"first_steps": [3 items], "safety_notes": [items]}
CONTENT = {
    "Farm Walk & Crop Tour": {
        "first_steps": [
            "Walk your farm and choose a safe route that takes 20 to 30 minutes.",
            "Pick 3 things to show (a crop, an animal, a farming method) and practise explaining each in simple words.",
            "Invite 2 or 3 families you know for a trial walk and ask what they liked.",
        ],
        "safety_notes": [
            "Keep visitors away from deep water, machines and chemical stores.",
            "Watch children at all times near canals, ponds and animals.",
        ],
    },
    "Fresh Produce Tasting": {
        "first_steps": [
            "Choose one crop that is ready now and check it is clean and safe to eat.",
            "Prepare a clean place with clean water, plates or trays.",
            "Tell 2 or 3 families which day the tasting will be.",
        ],
        "safety_notes": [
            "Wash produce with clean water before serving.",
            "Do not serve crops that were recently sprayed. Follow the waiting time on the product label.",
            "Wash your hands before serving. Anyone with an upset stomach should not serve food.",
        ],
    },
    "Animal Feeding Session": {
        "first_steps": [
            "Choose your calmest animals and a fenced place where visitors can feed them.",
            "Prepare small portions of safe feed (grass or fodder) for each visitor.",
            "Decide the days and times you are free, and invite 2 or 3 families for a trial.",
        ],
        "safety_notes": [
            "Only let visitors feed calm animals. Keep away young bulls, animals with young ones, and any animal that kicks or bites.",
            "Children must be with an adult at all times.",
            "Wash hands with soap after touching animals and before eating.",
        ],
    },
    "Milking Demonstration": {
        "first_steps": [
            "Choose your quietest animal and a clean place for the demonstration.",
            "Practise explaining each step of milking in simple words.",
            "Try it with one family and ask what was interesting or unclear.",
        ],
        "safety_notes": [
            "Wash the animal's udder and your hands, and use clean containers.",
            "Boil milk before giving it to visitors, especially children, pregnant women and sick people.",
            "Keep visitors at a safe distance. An animal may kick.",
        ],
    },
    "Traditional Farming Tool Display": {
        "first_steps": [
            "Collect the old farming tools you already have.",
            "Place them in a tidy row in the shade and write the name and use of each on a card.",
            "Prepare a short story for each tool and tell it to one family as a trial.",
        ],
        "safety_notes": [
            "Keep sharp tools out of children's reach or behind a rope.",
            "Check each tool for rust and loose parts before showing it.",
        ],
    },
    "Nature & Bird Walk": {
        "first_steps": [
            "Walk your farm early in the morning and note where the trees and birds are.",
            "Choose a flat, safe route of about 30 minutes.",
            "Learn the names of 5 trees or birds you see (ask the elders in your family) and try the walk with one family.",
        ],
        "safety_notes": [
            "Check for snakes, thorns and wasp nests before taking visitors.",
            "Avoid wet, slippery ground and deep water.",
            "Ask visitors to wear closed shoes and bring water.",
        ],
    },
    "Pick-Your-Own Harvest Day": {
        "first_steps": [
            "Choose one part of the field where the crop is ready and easy to reach.",
            "Arrange baskets or bags and decide how you will weigh or count what visitors pick.",
            "Invite 2 or 3 families for a trial day and note what they ask.",
        ],
        "safety_notes": [
            "Do not let visitors into fields that were recently sprayed. Follow the waiting time on the product label.",
            "Show visitors where to walk so they do not damage the crop.",
            "Keep clean water available for washing hands.",
        ],
    },
    "Desi Cooking Class": {
        "first_steps": [
            "Choose one simple dish, made from your own produce, that someone in your family cooks well.",
            "Check your cooking place: safe fire, clean water, seating.",
            "Cook the dish once with friends or relatives and write down the amounts and timing.",
        ],
        "safety_notes": [
            "Keep children away from open fires and hot pots.",
            "Keep food clean: wash hands, use clean utensils, cover the food.",
            "Ask guests about food allergies before cooking.",
        ],
    },
    "Fresh Dairy Experience (Chai & Lassi)": {
        "first_steps": [
            "Choose a clean, shaded seating place near the animals but not too close.",
            "Practise making chai and lassi with clean utensils and clean water.",
            "Offer a trial to 2 or 3 families and ask for their opinion.",
        ],
        "safety_notes": [
            "Boil milk well before making chai. Use only clean, safely handled milk and clean water for lassi.",
            "Keep hot pots and fires away from children.",
            "Keep flies, animals and waste away from the food area.",
        ],
    },
    "School Educational Visit Program": {
        "first_steps": [
            "Call or visit one nearby school and ask which class could visit.",
            "Plan a visit of 1 to 2 hours: a walk, one hands-on activity and a water break.",
            "Check you have enough toilets, shade and drinking water for the group size.",
        ],
        "safety_notes": [
            "Agree with the school how many adults will come with the children.",
            "Keep the group away from canals, ponds, machines and animal pens unless you are guiding them.",
            "Plan for heat and rain, and know where the nearest clinic is.",
        ],
    },
    "Sunset Farm Photography Walk": {
        "first_steps": [
            "Visit your farm at sunset this week and find 2 or 3 good viewpoints.",
            "Check the path is safe and not slippery.",
            "Invite a few photographers or students to try it and ask them to share their photos.",
        ],
        "safety_notes": [
            "Do not take visitors onto uneven ground after dark.",
            "Watch for snakes and insects in tall crops.",
            "Ask visitors not to enter fields or pick crops without asking you.",
        ],
    },
    "On-Farm Farmers Market": {
        "first_steps": [
            "Choose a day and a place near the road where visitors can park.",
            "List what you can sell (crops, milk, eggs) and a price for each.",
            "Ask 2 or 3 neighbours who also produce food to join you on the first day.",
        ],
        "safety_notes": [
            "Keep food covered and off the ground, and keep stalls clean.",
            "Keep animals away from the stall area.",
            "Show visitors where to park and keep children safe near the road.",
        ],
    },
    "Weekend Farm Experience Package": {
        "first_steps": [
            "First run one or two of the simpler experiences successfully before offering a package.",
            "Write down what a family would do in one day: times, activities, meal.",
            "List what each part would cost you and compare it with what families may pay before you set a price.",
        ],
        "safety_notes": [
            "Plan toilets, shade, drinking water and parking for the number of guests.",
            "Keep a first-aid kit and know where the nearest clinic is.",
            "Prepare food cleanly and keep it covered.",
        ],
    },
    "Seasonal Harvest Festival": {
        "first_steps": [
            "Choose a date during your harvest and tell your family what you plan.",
            "List what you need for the number of guests: space, toilets, water, parking, helpers.",
            "Talk to village elders or the local council about a large gathering.",
        ],
        "safety_notes": [
            "A large gathering needs clear paths, toilets, drinking water and a first-aid kit.",
            "Keep children away from machines, animals and water.",
            "Plan where cars will park so the road stays safe.",
        ],
    },
    "Overnight Farm Stay": {
        "first_steps": [
            "Look at your spare room or tent space: it should be clean, dry and have a lock or safe door.",
            "Check the toilet and bathing arrangements, and make sure everyone in the family is comfortable with guests staying.",
            "Try one night with a friend or relative first and ask what to improve.",
        ],
        "safety_notes": [
            "Never use a charcoal or gas heater or stove in a closed sleeping room. The fumes can be deadly.",
            "Agree clear house rules and privacy with your family and guests.",
            "Keep chemicals, tools and valuables locked away from guests.",
        ],
    },
    "Corporate Team-Building Day": {
        "first_steps": [
            "Ask 2 or 3 offices near you if they plan team days.",
            "Plan a half-day programme with 2 or 3 simple activities and a meal.",
            "Check space, toilets, shade and parking for 20 or more people.",
        ],
        "safety_notes": [
            "Plan toilets, drinking water, shade and parking for the group.",
            "Use only safe activities. Keep guests away from machines and tractors.",
            "Keep food clean and have a first-aid kit ready.",
        ],
    },
}


def _join(items, limit=3):
    names = [str(i).replace("_", " ") for i in items if i][:limit]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _km(f):
    d = f.get("distance_from_city_km")
    return f"{d} km" if isinstance(d, int) else None


def _crops(f):
    return _join(f.get("crops") or [])


def _plural(name):
    n = str(name)
    if n in ("sheep", "fish"):
        return n
    if n.endswith(("o", "s", "x", "ch", "sh")):
        return n + "es"
    return n + "s"


def _animals(f):
    return _join([_plural(k) for k in (f.get("animals") or {}).keys()])


def _dairy(f):
    a = f.get("animals") or {}
    return _join([_plural(k) for k in ("cow", "buffalo", "goat") if a.get(k, 0) > 0])


# title -> function(farm) -> one sentence built from the farm's own answers
WHY = {
    "Farm Walk & Crop Tour": lambda f: "Every farm can offer this. It costs nothing, and you are the guide."
        + (" Your scenic views make the walk more special." if f.get("scenic_features") else ""),
    "Fresh Produce Tasting": lambda f: f"You grow {_crops(f)}, and visitors enjoy tasting it fresh.",
    "Animal Feeding Session": lambda f: f"You keep {_animals(f)}. Children and families enjoy feeding animals.",
    "Milking Demonstration": lambda f: f"You have {_dairy(f)}. City visitors are curious to see how milking is done.",
    "Traditional Farming Tool Display": lambda f: "Old farming tools you already own tell the story of your farm.",
    "Nature & Bird Walk": lambda f: "Your trees and natural surroundings give visitors something to see and learn.",
    "Pick-Your-Own Harvest Day": lambda f: f"You grow {_crops(f)}. Families like to pick their own and take it home.",
    "Desi Cooking Class": lambda f: f"You grow {_crops(f)} and have help in the family to teach and cook.",
    "Fresh Dairy Experience (Chai & Lassi)": lambda f: f"You have {_dairy(f)}, so you can serve fresh chai and lassi.",
    "School Educational Visit Program": lambda f: "You have open space"
        + (f" and your farm is {_km(f)} from the city." if _km(f) else " for school groups."),
    "Sunset Farm Photography Walk": lambda f: "Your trees and views look beautiful at sunset.",
    "On-Farm Farmers Market": lambda f: f"You grow {_crops(f)} and your farm has a good road for visitors.",
    "Weekend Farm Experience Package": lambda f: "Your farm"
        + (f" is {_km(f)} from the city and" if _km(f) else "")
        + " has a good road, so families can come for a day.",
    "Seasonal Harvest Festival": lambda f: f"You grow {_crops(f)}, have open space and a good road for a harvest gathering.",
    "Overnight Farm Stay": lambda f: "You have a house or room, a toilet, and you have hosted visitors before.",
    "Corporate Team-Building Day": lambda f: "You have open space and a good road, and your farm is within reach of the city"
        + (f" ({_km(f)})." if _km(f) else "."),
}


def why_for_you(title, farm):
    """One sentence from the farm's own answers. Never fails."""
    try:
        fn = WHY.get(title)
        text = fn(farm) if fn else ""
        return " ".join(text.split())
    except Exception:
        return ""


def content_for(title):
    """first_steps and safety_notes (with the local-rules note added)."""
    c = CONTENT.get(title, {"first_steps": [], "safety_notes": []})
    return {
        "first_steps": list(c["first_steps"]),
        "safety_notes": list(c["safety_notes"]) + [LOCAL_RULES_NOTE],
    }