# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation for building AI-powered chat applications using the DIAL API (EPAM's internal AI proxy). The project is structured as a learning task where you implement an agent from scratch that integrates with a User Service and uses custom tools.

**Key Context:**
- DIAL API Endpoint: `https://ai-proxy.lab.epam.com`
- Requires EPAM VPN connection for API access
- DIAL API key must be set as `DIAL_API_KEY` environment variable
- User Service runs locally on port 8041 via Docker

## Running the Application

### Start User Service (Required Dependency)
```bash
docker-compose up -d
```
This starts the mock user service on `localhost:8041` with 1000 pre-generated users.

### Run the Main Application
```bash
python -m task.app
```

### Health Check User Service
```bash
curl http://localhost:8041/health
```

## Development Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Unix/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Architecture

### Agent Flow (Agentic Loop)
The application implements an agentic conversation loop:
1. User provides input via terminal
2. Message added to conversation history
3. DialClient sends conversation + tool schemas to DIAL API
4. If model responds with `finish_reason: "tool_calls"`:
   - Execute requested tools (web search, user CRUD operations)
   - Add tool results as TOOL role messages to conversation
   - Recursively call API again with updated conversation
5. If model responds with `finish_reason: "stop"`:
   - Return final assistant response

### Tool Architecture
All tools extend `BaseTool` abstract class with:
- `execute(arguments)` - tool execution logic
- `name` - tool identifier
- `description` - what the tool does (used by LLM)
- `input_schema` - JSON Schema for tool parameters
- `schema` property - formats tool for DIAL API (OpenAI tool format)

**Available Tools:**
- `WebSearchTool` - web searching capability
- `GetUserByIdTool` - retrieve user by ID from user service
- `SearchUsersTool` - search users by name/surname/email/gender
- `CreateUserTool` - add new user to user service
- `UpdateUserTool` - update existing user
- `DeleteUserTool` - remove user

### Message System
- `Message` - conversation message with role, content, tool_calls, tool_call_id, name
- `Role` - enum for SYSTEM, USER, ASSISTANT, TOOL
- `Conversation` - conversation container managing message history

**Critical Implementation Detail:** Tool messages must include `tool_call_id` that matches the `id` from the assistant's `tool_calls` array. The LLM uses this to correlate tool results with tool requests. Missing or mismatched IDs cause API errors.

## DIAL API Integration

### Request Structure
```python
{
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "", "tool_calls": [...]},
        {"role": "tool", "name": "tool_name", "tool_call_id": "call_xxx", "content": "..."}
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "...",
                "parameters": {...}  # JSON Schema
            }
        }
    ]
}
```

### Response Patterns
- `finish_reason: "tool_calls"` - model wants to use tools (continue loop)
- `finish_reason: "stop"` - model has final answer (end loop)

### Headers Required
```python
{
    "api-key": DIAL_API_KEY,
    "Content-Type": "application/json"
}
```

## User Service API

Base URL: `http://localhost:8041`

- `GET /v1/users/{user_id}` - get user by ID
- `GET /v1/users/search?name=&surname=&email=&gender=` - search users
- `POST /v1/users` - create user (body: UserCreate model)
- `PUT /v1/users/{user_id}` - update user (body: UserUpdate model)
- `DELETE /v1/users/{user_id}` - delete user

All requests use `Content-Type: application/json` header.

## Implementation Notes

### Current State
- Models (`conversation.py`, `message.py`, `role.py`) - ✅ Complete
- Tool base classes (`base.py`, `users/base.py`) - ✅ Complete
- User models (`user_info.py`) - ✅ Complete
- User client (`user_client.py`) - ✅ Complete
- Individual tools - 🚧 Need implementation (follow TODO comments)
- `client.py` - 🚧 Need implementation (follow TODO comments)
- `prompts.py` - 🚧 Need system prompt
- `app.py` - 🚧 Need to wire everything together

### Testing the Agent
Example prompt to test full functionality:
```
Add Andrej Karpathy as a new user
```

This tests:
1. Web search to find information about Andrej Karpathy
2. User creation with discovered information
3. Multi-turn tool calling
4. Conversation history management

## Branch Structure

- `main` - minimal guidance, more challenging
- `with-detailed-description` - includes more detailed TODO instructions
