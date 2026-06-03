import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        """
        LEARNING: Two Representations of Tools

        We need tools in TWO formats:

        1. __tools_dict (dict[str, BaseTool]):
           - For EXECUTION: When AI calls "web_search_tool", we look it up here
           - Key = tool name, Value = tool object
           - Fast O(1) lookup by name

        2. __tools (list[dict]):
           - For API COMMUNICATION: Sent to DIAL so it knows what tools exist
           - List of JSON schemas
           - Tells AI what tools are available and how to call them

        WHY TWO?
        - API needs schemas (descriptions, parameters) to make decisions
        - We need objects (execute methods) to perform actions
        - Separation of "interface" (schema) from "implementation" (code)

        This is a common pattern in API-driven systems.
        """

        # 1. Validate API key (fail fast if missing)
        if not api_key:
            raise ValueError("API key is required")

        # 2. Format the complete API endpoint
        # Example: "https://ai-proxy.lab.epam.com/openai/deployments/gpt-4/chat/completions"
        self.__endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"

        # 3. Store API key for authentication
        self.__api_key = api_key

        # 4. Build tools dictionary for execution lookup
        self.__tools_dict = {}
        if tools:
            for tool in tools:
                # Map tool name to tool object
                # Example: {"web_search_tool": WebSearchTool instance, ...}
                self.__tools_dict[tool.name] = tool

        # 5. Build tools list for API schemas
        self.__tools = []
        if tools:
            for tool in tools:
                # Get the JSON schema from each tool
                # The schema property combines name, description, and input_schema
                self.__tools.append(tool.schema)

        # 6. Optional: Debug output
        print(f"[OK] Endpoint: {self.__endpoint}")
        print(f"[OK] Tools loaded: {list(self.__tools_dict.keys())}")


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        """
        LEARNING: The Heart of the Agent - Recursive Tool Calling

        This is the MOST IMPORTANT method. It implements the agentic loop:

        1. Send conversation history to AI
        2. AI responds with either:
           a) Tool calls (finish_reason="tool_calls") → execute tools and recurse
           b) Final answer (finish_reason="stop") → return to user

        KEY CONCEPT: Recursion
        When AI needs tools, we:
        - Add AI's tool request to conversation
        - Execute tools
        - Add tool results to conversation
        - Call get_completion AGAIN with updated conversation

        This elegantly handles:
        - Single tool call: 1 recursion
        - Multiple sequential tool calls: Multiple recursions
        - No tool calls: 0 recursions (base case)

        Example flow:
        User: "Add Andrej Karpathy"
        → API responds with tool_calls → web_search
        → We execute web_search
        → RECURSE with tool results
        → API responds with tool_calls → add_user
        → We execute add_user
        → RECURSE with tool results
        → API responds with stop → final answer
        → RETURN to user
        """

        # 1. Prepare authentication headers
        headers = {
            "api-key": self.__api_key,  # DIAL API authentication
            "Content-Type": "application/json"  # We're sending JSON
        }

        # 2. Prepare request payload
        request_data = {
            # Convert Message objects to dicts (API format)
            "messages": [msg.to_dict() for msg in messages],
            # Include tool schemas so AI knows what tools are available
            "tools": self.__tools
        }

        # 3. Optional: Debug output
        if print_request:
            print("\n" + "="*50)
            print("REQUEST TO DIAL API")
            print(f"Messages in conversation: {len(messages)}")
            print("="*50)

        # 4. Make API call
        response = requests.post(
            url=self.__endpoint,
            headers=headers,
            json=request_data
        )

        # 5. Handle response
        if response.status_code == 200:
            # Success! Parse the response
            response_json = response.json()
            choices = response_json["choices"]
            choice = choices[0]  # DIAL returns array, we take first

            # Optional: Debug output
            if print_request:
                print(f"\nRESPONSE FROM DIAL API")
                print(f"Finish reason: {choice['finish_reason']}")

            # Extract message components
            message_data = choice["message"]
            content = message_data.get("content", "")
            tool_calls = message_data.get("tool_calls", None)

            # Create AI response message
            ai_response = Message(
                role=Role.AI,
                content=content,
                tool_calls=tool_calls
            )

            # Decision point: Does AI want to use tools?
            if choice["finish_reason"] == "tool_calls":
                """
                LEARNING: Recursive Case

                AI wants to call tools. We need to:
                1. Add AI's tool request to conversation
                2. Execute the tools
                3. Add tool results to conversation
                4. Call API again so it can see tool results

                The conversation history grows:
                [system, user] →
                [system, user, assistant(tool_calls)] →
                [system, user, assistant(tool_calls), tool, tool, ...] →
                [system, user, assistant(tool_calls), tool, tool, ..., assistant(final)]
                """
                # Add AI's tool call request to conversation
                messages.append(ai_response)

                # Execute all requested tools
                tool_messages = self._process_tool_calls(tool_calls)

                # Add tool results to conversation
                messages.extend(tool_messages)

                # RECURSION: Call ourselves again with updated conversation
                # AI will now see tool results and either:
                # - Call more tools (another recursion)
                # - Provide final answer (base case)
                return self.get_completion(messages, print_request)
            else:
                """
                LEARNING: Base Case

                finish_reason="stop" means AI has a final answer.
                No more tools needed. Return this message to the user.

                This is the base case that stops recursion.
                """
                return ai_response
        else:
            # API error
            raise Exception(f"API Error: {response.status_code} {response.text}")


    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """
        LEARNING: Tool Call Processing - The Bridge Between AI and Tools

        This method converts AI's tool call REQUESTS into executed RESULTS.

        Input (from AI):
        [
            {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "web_search_tool",
                    "arguments": "{\"request\": \"Andrej Karpathy\"}"
                }
            }
        ]

        Output (for AI):
        [
            Message(
                role=TOOL,
                tool_call_id="call_abc123",
                name="web_search_tool",
                content="Andrej Karpathy is an AI researcher..."
            )
        ]

        CRITICAL: tool_call_id Matching
        ================================
        The tool_call_id MUST match the id from the AI's request.
        This is how the API links "I want to call X" with "here's X's result".

        If IDs don't match:
        - API rejects the message
        - AI gets confused
        - Error: "tool call not found"

        Think of it like:
        - AI: "Call function #123"
        - You: "Here's result for #123"
        - AI: "Great, I can use that!"

        If you return result for #456, AI says "I didn't ask for #456!"
        """
        tool_messages = []

        for tool_call in tool_calls:
            # 1. Extract tool call ID (CRITICAL for matching!)
            tool_call_id = tool_call["id"]

            # 2. Extract function information
            function = tool_call["function"]

            # 3. Get function name (which tool to execute)
            function_name = function["name"]

            # 4. Parse arguments from JSON string to dict
            # AI sends: "{\"request\": \"search query\"}"
            # We need: {"request": "search query"}
            arguments = json.loads(function["arguments"])

            # 5. Execute the tool
            tool_execution_result = self._call_tool(function_name, arguments)

            # 6. Create TOOL message with result
            tool_messages.append(Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,  # MUST MATCH AI's request ID!
                content=tool_execution_result
            ))

            # 7. Print execution result for debugging
            print(f"\nFUNCTION '{function_name}'")
            print(tool_execution_result)
            print("-" * 50)

        # 8. Return all tool results
        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        """
        LEARNING: Simple Tool Execution with Graceful Failure

        This method looks up and executes a tool by name.

        Why return error string instead of raising exception?
        ======================================================
        AI models sometimes "hallucinate" - they might invent tool names that don't exist.

        Option 1 (bad): Raise exception
        - Crashes the agent
        - User sees technical error
        - No recovery possible

        Option 2 (good): Return error string
        - AI sees "Unknown function: made_up_tool"
        - AI can apologize: "Sorry, I don't have that capability"
        - Conversation continues gracefully

        This is called "graceful degradation" - handle errors without crashing.

        Example scenario:
        User: "Send an email to john@example.com"
        AI: *tries to call non-existent "send_email" tool*
        We return: "Unknown function: send_email"
        AI sees error and responds: "I'm sorry, I can't send emails. I can only manage users."
        """
        if function_name in self.__tools_dict:
            # Tool exists - look it up and execute
            tool = self.__tools_dict[function_name]
            return tool.execute(arguments)
        else:
            # Tool doesn't exist - return error as string (not exception!)
            # This lets the AI see and explain the error to the user
            return f"Unknown function: {function_name}"
