def experience_schema(farm_id, exp):
    return {
        "farm_id": farm_id,
        "title": exp.get("title"),
        "level": exp.get("level"),
        "monetization": exp.get("monetization"),
        "type": exp.get("type"),
        "enabled": exp.get("enabled", False)
    }
