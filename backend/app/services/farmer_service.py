from app.utils.supabase_client import get_admin_supabase_client
from postgrest import APIError

class FarmerService:

    def get_or_create_for_user(self, user_id: str, farm_type: str) -> dict:
        """
        Returns existing farmer+farm for this user, or creates them.
        Called on every transform — safe to call repeatedly.
        """
        admin = get_admin_supabase_client()

        # Check if farmer exists for this user
        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        if farmer_res.data:
            farmer_id = farmer_res.data[0]["id"]
        else:
            new_farmer = (
                admin.table("farmers")
                .insert({"user_id": user_id, "name": "My Farm"})
                .execute()
            )
            farmer_id = new_farmer.data[0]["id"]

        # Check if farm exists for this farmer
        farm_res = (
            admin.table("farms")
            .select("id")
            .eq("farmer_id", farmer_id)
            .limit(1)
            .execute()
        )

        if farm_res.data:
            farm_id = farm_res.data[0]["id"]
        else:
            new_farm = (
                admin.table("farms")
                .insert({
                    "farmer_id": farmer_id,
                    "farm_type": farm_type,
                    "size_category": "medium",
                })
                .execute()
            )
            farm_id = new_farm.data[0]["id"]

        return {"farmer_id": farmer_id, "farm_id": farm_id}
    
    def get_farm_for_user(self, user_id: str) -> dict | None:
        """
        Returns farm_id for existing user.
        Returns None if no farmer/farm exists yet.
        """
        admin = get_admin_supabase_client()

        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not farmer_res.data:
            return None

        farmer_id = farmer_res.data[0]["id"]

        farm_res = (
            admin.table("farms")
            .select("id")
            .eq("farmer_id", farmer_id)
            .limit(1)
            .execute()
        )
        if not farm_res.data:
            return None

        return {"farmer_id": farmer_id, "farm_id": farm_res.data[0]["id"]}
    
    def get_farms_for_user(self, user_id: str) -> list:
        """Returns all farms for this user."""
        admin = get_admin_supabase_client()

        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not farmer_res.data:
            return []

        farmer_id = farmer_res.data[0]["id"]
        farms = (
            admin.table("farms")
            .select("*")
            .eq("farmer_id", farmer_id)
            .execute()
        )
        return farms.data or []

    def get_farm_by_id(self, farm_id: str) -> dict | None:
        """Returns a single farm by id."""
        admin = get_admin_supabase_client()
        res = (
            admin.table("farms")
            .select("*")
            .eq("id", farm_id)
            .single()
            .execute()
        )
        return res.data if res.data else None

    def get_farmer_for_user(self, user_id: str) -> dict | None:
        """Returns farmer record for this user."""
        admin = get_admin_supabase_client()
        res = (
            admin.table("farmers")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

farmer_service = FarmerService()