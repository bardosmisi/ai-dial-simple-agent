from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        """
        LEARNING: Contrasting Tool Descriptions

        Compare this to get_user_by_id:
        - get_user_by_id: "when you know the exact user ID"
        - search_users: "without knowing their exact ID"

        This helps the AI choose the right tool:
        - User: "Show me user 42" → get_user_by_id
        - User: "Find users named John" → search_users
        """
        return "Search for users based on optional filters like name, surname, email, or gender. Returns a list of matching users. Use this when you need to find users without knowing their exact ID."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        LEARNING: Optional Parameters

        KEY CONCEPT: Empty "required" array
        - All four parameters (name, surname, email, gender) are OPTIONAL
        - The AI can send any combination: {}, {"name": "John"}, {"name": "John", "gender": "male"}
        - Each parameter description helps AI understand what kind of filtering it does

        This flexibility lets the AI adapt to vague user requests like:
        - "Find Johns" → {"name": "John"}
        - "Find male users" → {"gender": "male"}
        - "Find john@example.com" → {"email": "john@example.com"}
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Filter by user's first name"
                },
                "surname": {
                    "type": "string",
                    "description": "Filter by user's last name"
                },
                "email": {
                    "type": "string",
                    "description": "Filter by email address"
                },
                "gender": {
                    "type": "string",
                    "description": "Filter by gender"
                }
            },
            "required": []  # Empty list = all parameters are optional
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        LEARNING: The ** Operator (Dictionary Unpacking)

        `**arguments` unpacks the dictionary into keyword arguments.

        Example flow:
        1. AI sends: {"name": "John", "gender": "male"}
        2. arguments = {"name": "John", "gender": "male"}
        3. **arguments expands to: name="John", gender="male"
        4. Becomes: search_users(name="John", gender="male")

        This works because:
        - The API parameters match the function parameters exactly
        - UserClient.search_users accepts all these as kwargs
        - We don't need to manually extract each field

        Alternative (verbose):
        name = arguments.get("name")
        surname = arguments.get("surname")
        ...
        search_users(name=name, surname=surname, ...)

        Using ** is cleaner and more maintainable!
        """
        try:
            # Unpack arguments dict into keyword arguments
            return self._user_client.search_users(**arguments)
        except Exception as e:
            return f"Error while searching users: {str(e)}"
