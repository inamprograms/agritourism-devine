from app.core.supabase import supabase

class PlanService:
    
    def increment_ai_counter(self, user_id: str, ai_type: str):
        """
        Increments the correct AI usage counter in user_plans.
        ai_type: "assistant" | "farm" | "experience" | "story"
        """
        column_map = {
            "assistant":  "ai_assistant_used",
            "farm":       "ai_farm_used",
            "experience": "ai_experience_used",
            "story":      "ai_story_used",
        }
        column = column_map.get(ai_type, "ai_assistant_used")
        self._increment(user_id, column)

    def increment_transformation_counter(self, user_id: str):
        """Increments transformations_used counter."""
        self._increment(user_id, "transformations_used")

    def _increment(self, user_id: str, column: str):
        """Base increment — fails silently, never blocks response."""
        try:
            res = (
                supabase.table("user_plans")
                .select(column)
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            if res.data:
                current = res.data.get(column, 0) or 0
                supabase.table("user_plans").update(
                    {column: current + 1}
                ).eq("user_id", user_id).execute()
        except Exception as e:
            print(f"[COUNTER_ERROR] Failed to increment {column}: {e}")

    def get_plan(self, user_id: str) -> dict | None:
        """
        Returns current user plan and usage.
        Used by /plans/me endpoint in Step 5d.
        """
        try:
            res = (
                supabase.table("user_plans")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            return res.data
        except Exception:
            return None

plan_service = PlanService()