from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "update_user"

    @property
    def description(self) -> str:
        """
        LEARNING: Partial Updates

        Key phrase: "Only provided fields will be updated"

        This tells the AI it can send:
        - {"id": 1, "new_info": {"company": "Tesla"}} - only update company
        - {"id": 1, "new_info": {"company": "Tesla", "salary": 250000}} - update two fields

        UserUpdate has all optional fields (unlike UserCreate which has required fields).
        This enables partial updates without resending unchanged data.
        """
        return "Updates an existing user's information. Requires the user ID and a new_info object with fields to update. Only provided fields will be updated."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        LEARNING: Nested Schema Structure

        This is more complex than previous tools because it has TWO levels:

        Level 1: Tool parameters
        - id: which user to update
        - new_info: what to change

        Level 2: new_info contents (from UserUpdate model)
        - company, salary, email, etc.

        Result structure AI sends:
        {
            "id": 42,
            "new_info": {
                "company": "Tesla",
                "salary": 250000
            }
        }

        This nested structure keeps the API clean:
        - ID is separate from update data
        - Easy to validate "which user" vs "what changes"
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The ID of the user to update"
                },
                "new_info": UserUpdate.model_json_schema()  # Nested schema!
            },
            "required": ["id", "new_info"]  # Both parameters required
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        LEARNING: Multi-step Extraction

        We need to:
        1. Extract and validate id
        2. Extract and validate new_info
        3. Call API with both

        Note the pattern:
        - Simple field (id): extract and cast
        - Complex field (new_info): validate with Pydantic

        This matches the schema structure:
        - Top-level fields → manual extraction
        - Nested object → Pydantic validation
        """
        try:
            # Extract user ID
            user_id = int(arguments["id"])

            # Extract and validate update data
            new_info = UserUpdate.model_validate(arguments["new_info"])

            # Update user with both pieces of data
            return self._user_client.update_user(user_id, new_info)
        except Exception as e:
            return f"Error while updating user: {str(e)}"
