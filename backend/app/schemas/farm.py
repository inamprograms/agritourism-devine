def farm_schema(data):
    return {
        "id": data.get("id"),
        "farmer_id": data.get("farmer_id"),
        "name": data.get("name"),
        "farm_type": data.get("farm_type"),
        "size_category": data.get("size_category"),
        "location": data.get("location"),
        "description": data.get("description"),
        "created_at": data.get("created_at"),
    }
