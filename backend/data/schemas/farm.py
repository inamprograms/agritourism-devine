def farm_schema(data):
    return {
        "farmer_id": data.get("farmer_id"),
        "farm_type": data.get("farm_type"),
        "size_category": data.get("size_category")
    }
