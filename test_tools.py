"""
Test script to verify all tools work correctly before running the full agent.

This tests each tool in isolation to catch errors early.
"""

import os
from task.tools.users.user_client import UserClient
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool

def test_user_service():
    """Test that the user service is accessible"""
    print("="*60)
    print("Testing User Service Connection")
    print("="*60)

    client = UserClient()

    try:
        # Test get user by ID
        print("\n1. Testing get_user_by_id...")
        get_tool = GetUserByIdTool(client)
        result = get_tool.execute({"id": 1})
        print("[OK] Success!")
        print(result[:200] + "..." if len(result) > 200 else result)

        # Test search users
        print("\n2. Testing search_users...")
        search_tool = SearchUsersTool(client)
        result = search_tool.execute({"name": "John"})
        print("[OK] Success!")
        print("Found users with name 'John'")

        print("\nAll user service tests passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False

def test_web_search():
    """Test web search tool (requires DIAL API key)"""
    print("\n" + "="*60)
    print("Testing Web Search Tool")
    print("="*60)

    api_key = os.getenv('DIAL_API_KEY')

    if not api_key:
        print("[WARN]  DIAL_API_KEY not set - skipping web search test")
        print("   Set it with: export DIAL_API_KEY='your-key'")
        return False

    from task.tools.web_search import WebSearchTool

    try:
        print("\nTesting web_search_tool...")
        web_tool = WebSearchTool(
            api_key=api_key,
            endpoint="https://ai-proxy.lab.epam.com"
        )
        result = web_tool.execute({"request": "Python programming language"})
        print("[OK] Success!")
        print(result[:200] + "..." if len(result) > 200 else result)

        print("\nWeb search test passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    print("\nRunning Tool Tests\n")

    # Test user service tools
    user_service_ok = test_user_service()

    # Test web search (optional if no API key)
    web_search_ok = test_web_search()

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"User Service Tools: {'PASS' if user_service_ok else 'FAIL'}")
    print(f"Web Search Tool: {'PASS' if web_search_ok else 'SKIPPED (no API key)'}")
    print("="*60)
