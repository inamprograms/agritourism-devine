# routes/carbon_routes.py

from flask import Blueprint, request, jsonify
from services.carbon.carbon_service import CarbonService
from data.schemas.carbon_schema import carbon_input_schema, carbon_output_schema


# Create blueprint
carbon_bp = Blueprint("carbon_bp", __name__, url_prefix="/carbon")


@carbon_bp.route("/estimate", methods=["POST"])
def estimate_carbon():
    """
    Endpoint to calculate carbon credits for agroforestry.
    Expects JSON payload:
    {
        "land_area_hectares": float,
        "tree_density": str,
        "tree_age_years": int,
        "management_practice": str,
        "climate_zone": str (optional),
        "tree_species": str (optional),
        "soil_type": str (optional)
    }
    """
    try:
        raw_data = request.get_json() or {}
        
        # Validate input
        validated_input = carbon_input_schema(raw_data)
        
        # Calculate using CarbonService
        result = CarbonService.calculate(**validated_input)
        
        # Format output
        formatted_result = carbon_output_schema(result)
        
        return jsonify({"success": True, "data": formatted_result}), 200
        
    except ValueError as e:
        return jsonify({"success": False, "error": f"Validation error: {str(e)}"}), 400
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
