# data/schemas/visitor.py

def visitor_schema(farm_id, experience, photos=None, reviews=None, views=0):
    """
    Defines the structure of experience for visitor discovery.
    """
    return {
        "farm_id": farm_id,
        "experience_id": experience.get("id"),
        "title": experience.get("title"),
        "type": experience.get("type"),
        "level": experience.get("level"),
        "monetization": experience.get("monetization"),
        "enabled": experience.get("enabled", False),
        "photos": photos or [],
        "reviews": reviews or [],
        "views": views
    }