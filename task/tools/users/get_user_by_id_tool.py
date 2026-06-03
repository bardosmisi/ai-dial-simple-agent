from typing import Any

from task.tools.users.base import BaseUserServiceTool


class GetUserByIdTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        """
        LEARNING: This is the simplest CRUD operation - READ by ID.
        The name should be clear and describe the action.
        """
        return "get_user_by_id"

    @property
    def description(self) -> str:
        """
        LEARNING: Good descriptions tell the AI:
        1. What the tool does
        2. When to use it (vs other tools)

        Here we emphasize "when you know the exact user ID" to help AI
        distinguish this from search_users (which is for fuzzy searching).
        """
        return "Retrieves detailed information about a specific user by their ID. Use this when you know the exact user ID."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        LEARNING: JSON Schema type system

        IMPORTANT: Use "number" not "integer"
        - "number" covers both integers and floats in JSON Schema
        - "integer" is more restrictive
        - Convention is to use "number" for numeric IDs

        We mark "id" as required because you can't fetch a user without an ID.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The unique identifier of the user"
                }
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        LEARNING: Error Handling in AI Tools

        WHY TRY-EXCEPT?
        If the user service throws an exception (network error, user not found),
        we need to catch it and return an error MESSAGE.

        Remember: The AI reads the tool's return value as TEXT.
        If we let the exception bubble up, the AI never sees what went wrong.
        By catching and returning a string, the AI can:
        - Understand the error
        - Explain it to the user in natural language
        - Potentially try alternative approaches

        This pattern of "exceptions → error strings" is critical in AI systems.
        """
        try:
            # Convert to int (API expects integer type)
            user_id = int(arguments["id"])

            # Call the user service via the client
            # _user_client is inherited from BaseUserServiceTool
            return self._user_client.get_user(user_id)
        except Exception as e:
            # Return error as string so AI can read and explain it
            return f"Error while retrieving user by id: {str(e)}"