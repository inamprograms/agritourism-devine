# services/visitor_service.py

from data.supabase_client import supabase
from data.schemas.visitor import visitor_schema
from postgrest import APIError

class VisitorService:
    """
    Handles visitor-facing experience data:
    - Views, photos, reviews
    - Fetch and update visitor metrics
    """

    def get_experience(self, experience_id):
        """
        Fetch single experience with trust signals from both tables.
        """
        try:
            # 1. Fetch experience
            exp_res = supabase.table("experiences").select("*").eq("id", experience_id).single().execute()
            experience = exp_res.data
            if not experience:
                return None

            # 2. Fetch visitor experience info
            visitor_res = supabase.table("visitor").select("*").eq("experience_id", experience_id).single().execute()
            visitor_info = visitor_res.data or {"views": 0, "photos": [], "reviews": []}

            return visitor_schema(
                farm_id=experience["farm_id"],
                experience=experience,
                photos=visitor_info.get("photos", []),
                reviews=visitor_info.get("reviews", []),
                views=visitor_info.get("views", 0)
            )

        except APIError:
            return None
    
    def increment_views(self, experience_id):
        """
        Increment the views of a visitor by 1 using Supabase RCP
        and return the updated views count.
        """
        try:
            # Call the RPC function
            res = supabase.rpc("increment_views_fn", {"exp_id": experience_id}).execute()

            # if res.error:
            #     print("Error incrementing views:", res.error)
            #     return None

            # if not res.data:
            #     print("No row found with experience_id:", experience_id)
            #     return None

            # res.data is a list with the returned value
            # return res.data[0]

        except Exception as e:
            print("Exception incrementing views:", e)
            return None

# singleton instance
visitor_service = VisitorService()
