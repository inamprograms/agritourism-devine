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
        "crops": data.get("crops", []),
        "animals": data.get("animals", {}),
        "existing_trees": data.get("existing_trees", []),
        "water_source": data.get("water_source"),
        "structures": data.get("structures", []),
        "road_access": data.get("road_access"),
        "distance_from_city_km": data.get("distance_from_city_km"),
        "scenic_features": data.get("scenic_features", []),
    }
