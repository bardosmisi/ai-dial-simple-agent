import os

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY')

def main():
    """
    LEARNING: Putting It All Together - The Main Application

    This function wires all components together:
    1. User service client (talks to local API)
    2. Tools (the agent's capabilities)
    3. DIAL client (talks to AI API)
    4. Conversation (maintains history)
    5. Input loop (user interface)

    Architecture:
    User (terminal)
      ↓ input
    main() → DialClient → DIAL API
      ↓                      ↓
    Conversation ←──────── AI Response
      ↓                      ↓
    Tools ← execute ─────── tool_calls
      ↓
    UserService API / Web Search

    The conversation object is KEY:
    - It maintains FULL history
    - System prompt is ALWAYS first
    - Each turn adds User → Assistant → (optional) Tool messages
    - This context lets AI:
      * Remember previous requests
      * Refer to earlier tool results
      * Maintain coherent multi-turn conversations
    """

    print("="*60)
    print("[AI] DIAL AI User Management Agent")
    print("="*60)

    # 1. Create UserClient for local user service
    user_client = UserClient()
    print("[OK] User service client initialized")

    # 2. Create DialClient with ALL tools
    dial_client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4",  # Can use: gpt-4, gpt-4o, claude-3-5-sonnet, etc.
        api_key=API_KEY,
        tools=[
            WebSearchTool(api_key=API_KEY, endpoint=DIAL_ENDPOINT),
            GetUserByIdTool(user_client),
            SearchUsersTool(user_client),
            CreateUserTool(user_client),
            UpdateUserTool(user_client),
            DeleteUserTool(user_client)
        ]
    )

    # 3. Create Conversation with system message
    # The system prompt is ALWAYS the first message
    conversation = Conversation()
    conversation.add_message(Message(
        role=Role.SYSTEM,
        content=SYSTEM_PROMPT
    ))
    print("[OK] Conversation initialized with system prompt\n")

    print("Ready! Try these commands:")
    print("  - 'Add Andrej Karpathy as a new user'")
    print("  - 'Show me user with ID 1'")
    print("  - 'Find all users named John'")
    print("  - Type 'exit' or 'quit' to stop")
    print("="*60 + "\n")

    # 4. Run infinite conversation loop
    while True:
        # Get user input
        user_input = input("> ").strip()

        # Allow graceful exit
        if user_input.lower() in ['exit', 'quit']:
            print("\n Goodbye!")
            break

        # Skip empty input
        if not user_input:
            continue

        # Add user message to conversation
        conversation.add_message(Message(
            role=Role.USER,
            content=user_input
        ))

        # Get AI response (this handles tool calls internally via recursion)
        try:
            ai_response = dial_client.get_completion(
                messages=conversation.get_messages(),
                print_request=True
            )

            # Add AI response to conversation history
            conversation.add_message(ai_response)

            # Print AI's response to user
            print(f"\n[AI] Assistant: {ai_response.content}\n")

        except Exception as e:
            # Handle errors gracefully
            print(f"\n[ERROR] Error: {str(e)}\n")
            # Don't crash - let user try again


main()

#TODO:
# Request sample:
# Add Andrej Karpathy as a new user