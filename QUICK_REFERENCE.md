# DIAL AI Agent - Quick Reference Guide

## Starting the Agent

```bash
# 1. Start user service
docker-compose up -d

# 2. Set API key
export DIAL_API_KEY='your-key-here'

# 3. Run agent
python -m task.app
```

## Testing Commands

Try these in order:

1. **Simple query:** `Who is Andrej Karpathy?`
   - Tests: Web search only

2. **User lookup:** `Show me user with ID 1`
   - Tests: get_user_by_id tool

3. **Search users:** `Find all users named John`
   - Tests: search_users with filters

4. **Complex task:** `Add Andrej Karpathy as a new user`
   - Tests: Web search → create user (multi-tool)

5. **Update:** `Update user 1's company to Tesla`
   - Tests: update_user tool

6. **Delete:** `Delete user with ID 500`
   - Tests: delete_users tool

## Key Code Snippets

### Creating a Tool

```python
class MyTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "What it does and when to use it"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Parameter description"}
            },
            "required": ["param"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            # Tool logic
            return "result"
        except Exception as e:
            return f"Error: {str(e)}"
```

### Recursive Tool Calling Pattern

```python
def get_completion(self, messages):
    response = api_call(messages, tools)

    if finish_reason == "tool_calls":
        # Execute tools and recurse
        messages.append(ai_response)
        messages.extend(execute_tools(tool_calls))
        return self.get_completion(messages)  # Recurse
    else:
        # Base case - return final answer
        return ai_response
```

### Tool Call Processing

```python
def _process_tool_calls(self, tool_calls):
    results = []
    for call in tool_calls:
        tool_call_id = call["id"]  # CRITICAL
        function_name = call["function"]["name"]
        arguments = json.loads(call["function"]["arguments"])

        result = execute_tool(function_name, arguments)

        results.append(Message(
            role=TOOL,
            tool_call_id=tool_call_id,  # MUST MATCH
            name=function_name,
            content=result
        ))
    return results
```

## Architecture Flow

```
User Input
    ↓
Conversation (add user message)
    ↓
DialClient.get_completion()
    ↓
DIAL API
    ↓
finish_reason == "tool_calls"?
    YES → Execute tools → Add results → RECURSE
    NO  → Return final answer
    ↓
Print to user
```

## Important Patterns

### 1. Error Handling
```python
# DON'T raise exceptions in tools
def execute(self, args):
    if error:
        raise Exception("Failed")  # ❌ Bad

# DO return error strings
def execute(self, args):
    try:
        return do_work()
    except Exception as e:
        return f"Error: {str(e)}"  # ✅ Good
```

### 2. JSON Schema Types
```python
# Use "number" not "integer"
"id": {"type": "number"}  # ✅ Correct
"id": {"type": "integer"}  # ❌ Non-standard

# Optional parameters
"required": []  # Empty = all optional
"required": ["name", "email"]  # These are required
```

### 3. Tool Call ID Matching
```python
# AI sends
{"id": "call_abc123", "function": {...}}

# You MUST respond with
Message(tool_call_id="call_abc123", ...)  # MUST MATCH
```

## File Structure

```
task/
├── app.py                      # Entry point
├── client.py                   # DIAL client (orchestration)
├── prompts.py                  # System prompt
├── models/
│   ├── conversation.py         # Conversation container
│   ├── message.py              # Message structure
│   └── role.py                 # Role enum
└── tools/
    ├── base.py                 # Tool base class
    ├── web_search.py           # Web search tool
    └── users/
        ├── base.py             # User tool base
        ├── user_client.py      # User service client
        ├── get_user_by_id_tool.py
        ├── search_users_tool.py
        ├── create_user_tool.py
        ├── update_user_tool.py
        ├── delete_user_tool.py
        └── models/
            └── user_info.py    # Pydantic models
```

## API Endpoints

### User Service (localhost:8041)
- `GET /v1/users/{id}` - Get user by ID
- `GET /v1/users/search?name=&surname=&email=&gender=` - Search
- `POST /v1/users` - Create user
- `PUT /v1/users/{id}` - Update user
- `DELETE /v1/users/{id}` - Delete user

### DIAL API
- `POST https://ai-proxy.lab.epam.com/openai/deployments/{model}/chat/completions`
- Models: gpt-4, gpt-4o, claude-3-5-sonnet

## Common Issues

| Issue | Solution |
|-------|----------|
| "API key is required" | Set DIAL_API_KEY env var |
| Connection timeout to DIAL | Connect to EPAM VPN |
| Connection refused (port 8041) | Start Docker: `docker-compose up -d` |
| "tool call not found" | Check tool_call_id matches |
| Infinite tool calling | Check finish_reason logic |
| Validation errors | Check required fields in schema |

## Environment Variables

```bash
# Required
export DIAL_API_KEY='your-api-key-here'

# Optional (for debugging)
export DEBUG=1
```

## Useful Commands

```bash
# Check user service health
curl http://localhost:8041/health

# View user service logs
docker-compose logs -f

# Stop user service
docker-compose down

# Run tests
python test_tools.py
```

## Model Selection

Available models in DIAL (set in `app.py`):
- `gpt-4` - OpenAI GPT-4 (most reliable tool calling)
- `gpt-4o` - GPT-4 Omni (faster, multimodal)
- `claude-3-5-sonnet` - Anthropic Claude 3.5 Sonnet (excellent reasoning)

```python
dial_client = DialClient(
    endpoint=DIAL_ENDPOINT,
    deployment_name="gpt-4",  # Change here
    api_key=API_KEY,
    tools=[...]
)
```

## Debugging Tips

### Enable request logging
The `print_request` parameter in `get_completion()` is already True by default.

### Check conversation history
```python
print(f"Messages: {len(conversation.get_messages())}")
for msg in conversation.get_messages():
    print(f"{msg.role}: {msg.content[:50]}...")
```

### Monitor tool execution
Tool results are automatically printed in `_process_tool_calls()`

### Test tools individually
```python
from task.tools.users.user_client import UserClient
from task.tools.users.get_user_by_id_tool import GetUserByIdTool

client = UserClient()
tool = GetUserByIdTool(client)
print(tool.execute({"id": 1}))
```

## Key Concepts Cheat Sheet

| Concept | Quick Explanation |
|---------|-------------------|
| **Tool** | A capability the AI can use (search, CRUD, etc.) |
| **tool_call** | AI's request to use a tool |
| **tool_call_id** | ID linking request to response (CRITICAL) |
| **finish_reason** | "tool_calls" = more work, "stop" = done |
| **Recursion** | Calling get_completion() within itself |
| **Base case** | finish_reason="stop" stops recursion |
| **JSON Schema** | Format for describing API parameters |
| **Pydantic** | Python library for validation + auto-schemas |
| **System prompt** | First message defining agent behavior |
| **Conversation** | Full history (system, user, assistant, tool) |

## Performance Tips

1. **Conversation length:** Keep history under 20 messages for speed
2. **Tool descriptions:** Clear descriptions help AI choose right tool
3. **Error messages:** Specific errors help AI recover gracefully
4. **Caching:** Consider caching user service responses
5. **Model choice:** gpt-4 most reliable, gpt-4o fastest
