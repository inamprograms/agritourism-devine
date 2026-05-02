def experience_schema(farm_id, exp):
    return {
        "farm_id": farm_id,
        "title": exp.get("title"),
        "level": exp.get("level"),
        "monetization": exp.get("monetization"),
        "type": exp.get("type"),
        "enabled": exp.get("enabled", False),
        "description": exp.get("description"),
        "requirements": exp.get("requirements", []),
        "estimated_revenue": exp.get("estimated_revenue"),
        "season": exp.get("season", "year_round"),
        "setup_cost_range": exp.get("setup_cost_range", "zero"),
        "time_to_launch": exp.get("time_to_launch", "1-2 weeks"),
    }
