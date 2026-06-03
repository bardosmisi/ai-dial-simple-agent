from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate


class CreateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "add_user"

    @property
    def description(self) -> str:
        """
        LEARNING: Detailed Descriptions for Complex Tools

        This tool is more complex than the others because it accepts many fields.
        The description lists:
        1. What it does ("Creates a new user")
        2. Required fields (name, surname, email, about_me)
        3. Optional fields (all the extras)

        This helps the AI understand:
        - Minimum data needed
        - What additional enrichment is possible
        """
        return "Creates a new user in the system. Requires name, surname, email, and about_me. Optional fields include phone, date_of_birth, address, gender, company, salary, and credit_card."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        LEARNING: Pydantic Magic - Auto-Generated Schemas

        KEY CONCEPT: model_json_schema()

        Instead of manually writing this:
        {
            "type": "object",
            "properties": {
                "name": {"type": "string", ...},
                "surname": {"type": "string", ...},
                "email": {"type": "string", ...},
                "about_me": {"type": "string", ...},
                "phone": {"type": "string", ...},
                "date_of_birth": {"type": "string", ...},
                "address": {  # Nested object!
                    "type": "object",
                    "properties": {
                        "street": ...,
                        "city": ...,
                        ...
                    }
                },
                ...
            },
            "required": ["name", "surname", "email", "about_me"]
        }

        Pydantic generates it ALL from the UserCreate model definition!

        Benefits:
        1. No duplication - model is source of truth
        2. Includes nested objects (Address, CreditCard)
        3. Includes validation rules
        4. Updates automatically if model changes

        This is the power of schema-driven development.
        """
        return UserCreate.model_json_schema()

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        LEARNING: Pydantic Validation

        KEY CONCEPT: model_validate()

        What it does:
        1. Checks all required fields are present
        2. Validates field types (strings are strings, numbers are numbers)
        3. Validates nested objects (Address, CreditCard)
        4. Applies any custom validation rules
        5. Constructs a UserCreate object

        If validation fails, it raises an exception with a detailed message:
        - "Field 'name' is required"
        - "Field 'email' must be a valid email"
        - etc.

        This prevents bad data from reaching the API.

        Two-step process:
        1. model_validate(arguments) → UserCreate object
        2. add_user(user_create) → API call with validated data

        WHY NOT just pass arguments directly to add_user?
        - No validation - bad data reaches API
        - No type safety - runtime errors
        - No IDE support - can't autocomplete fields
        """
        try:
            # Validate arguments and create UserCreate object
            user_create = UserCreate.model_validate(arguments)

            # Call user service with validated object
            return self._user_client.add_user(user_create)
        except Exception as e:
            # Pydantic validation errors will be caught here too
            return f"Error while creating a new user: {str(e)}"
