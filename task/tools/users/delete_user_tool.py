from typing import Any

from task.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        """
        LEARNING: Following Specifications

        The TODO says "delete_users" (plural).
        Even though it seems like it should be "delete_user" (singular),
        we follow the specification EXACTLY.

        In real projects, inconsistencies like this happen.
        When in doubt, follow the spec and potentially flag for clarification.
        """
        return "delete_users"

    @property
    def description(self) -> str:
        """
        LEARNING: Warnings in Descriptions

        For destructive operations (delete, remove, drop, etc.),
        it's good practice to warn in the description:
        "This action is permanent and cannot be undone"

        This helps the AI:
        1. Warn users before deleting
        2. Ask for confirmation
        3. Be extra careful with IDs

        The system prompt can reinforce this behavior too.
        """
        return "Deletes a user from the system by their ID. This action is permanent and cannot be undone."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        LEARNING: Pattern Recognition

        Notice this is IDENTICAL to get_user_by_id's schema.
        Both tools take a single required "id" parameter.

        The difference is in:
        - name: "get_user_by_id" vs "delete_users"
        - description: what the tool does
        - execute: which API method is called

        Same structure, different behavior - this is good API design.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The ID of the user to delete"
                }
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        LEARNING: Completing CRUD

        We've now implemented all CRUD operations:
        - Create: add_user (CreateUserTool)
        - Read: get_user_by_id (GetUserByIdTool) + search_users (SearchUsersTool)
        - Update: update_user (UpdateUserTool)
        - Delete: delete_users (DeleteUserTool)

        This is the standard pattern for data management systems.
        The AI now has full control over user data.
        """
        try:
            user_id = int(arguments["id"])
            return self._user_client.delete_user(user_id)
        except Exception as e:
            return f"Error while deleting user by id: {str(e)}"