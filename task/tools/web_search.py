from typing import Any

import requests

from task.tools.base import BaseTool


class WebSearchTool(BaseTool):

    def __init__(self, api_key: str, endpoint: str):
        self.__api_key = api_key
        self.__endpoint = f"{endpoint}/openai/deployments/gemini-2.5-pro/chat/completions"

    # https://dialx.ai/dial_api#operation/sendChatCompletionRequest (-> tools -> function)
    # Sample of tool config:
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "web_search_tool",
    #         "description": "Tool for WEB searching.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "request": {
    #                     "type": "string",
    #                     "description": "The search query or question to search for on the web"
    #                 }
    #             },
    #             "required": [
    #                 "request"
    #             ]
    #         }
    #     }
    # }

    @property
    def name(self) -> str:
        """
        LEARNING: The name property returns the unique identifier for this tool.
        This name must match what the AI will use when calling the tool.
        It appears in the AI's tool_calls response.
        """
        return "web_search_tool"

    @property
    def description(self) -> str:
        """
        LEARNING: The description tells the AI WHEN and WHY to use this tool.
        The AI reads this to decide if this tool fits the user's request.
        Be specific and clear about the tool's purpose.
        """
        return "Tool for searching information on the web. Use this when you need current information, facts, or answers that require internet search."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        LEARNING: The input_schema defines what parameters the AI can send.
        This is JSON Schema format - the standard for describing JSON structures.

        Structure:
        - type: "object" means the parameters are a dictionary
        - properties: defines each parameter (name, type, description)
        - required: list of parameter names that MUST be provided

        The AI will generate arguments matching this schema.
        Example: {"request": "Who is Andrej Karpathy?"}
        """
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the web"
                }
            },
            "required": ["request"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        LEARNING: This method performs the actual web search.

        KEY CONCEPT - Tools within Tools:
        This tool makes a DIAL API call! We're using DIAL's "static_function" feature.
        static_function is a special tool type that DIAL provides - like google_search.

        Flow:
        1. Our agent calls web_search_tool
        2. We make an API call to DIAL with google_search static_function
        3. DIAL performs the Google search
        4. DIAL returns search results
        5. We return those results to our agent

        This is "delegating" to DIAL's built-in capabilities.
        """
        # 1. Prepare authentication and content type headers
        headers = {
            "api-key": self.__api_key,
            "Content-Type": "application/json"
        }

        # 2. Create the request to DIAL
        # We send a simple user message with the search query
        # And specify we want to use the google_search static_function
        request_data = {
            "messages": [{"role": "user", "content": str(arguments["request"])}],
            "tools": [{
                "type": "static_function",  # Special type for DIAL's built-in tools
                "static_function": {
                    "name": "google_search",  # DIAL's Google Search capability
                    "description": "Grounding with Google Search",
                    "configuration": {}
                }
            }]
        }

        # 3. Make the API call to DIAL
        response = requests.post(url=self.__endpoint, headers=headers, json=request_data)

        # 4. Handle the response
        if response.status_code == 200:
            # Success! Extract the search results from the message content
            return response.json()["choices"][0]["message"]["content"]
        else:
            # Error - return the error as a string so the AI can see what went wrong
            return f"Error: {response.status_code} {response.text}"
