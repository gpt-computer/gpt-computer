# API Documentation Guide

## Overview

gpt-computer provides a comprehensive REST API for integrating autonomous code generation into your applications.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Authentication](#authentication)
4. [Response Formats](#response-formats)
5. [Examples](#examples)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Webhooks & Events](#webhooks--events)

---

## Quick Start

### Starting the API Server

```bash
# Install gpt-computer
poetry add gpt-computer

# Or install from source
git clone https://github.com/xeondesk/gpt-computer
cd gpt-computer
poetry install

# Start the API server
poetry run python -m gpt_computer.api.main

# Or with Uvicorn for production
poetry run uvicorn gpt_computer.api.main:app --host 0.0.0.0 --port 8000
```

### Basic Request Example

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple calculator app in Python",
    "max_iterations": 3
  }'
```

---

## API Endpoints

### Health Check
**`GET /health`**

Check if the API server is running.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.1"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Run Agent
**`POST /agent/run`**

Execute the agent with a given prompt.

**Request Body:**
```json
{
  "prompt": "string - the task description",
  "max_iterations": "integer - maximum iterations (default: 3)",
  "model": "string - LLM model (default: gpt-4)",
  "project_path": "string - project directory (optional)",
  "temperature": "float - creativity level 0-1 (default: 0.7)"
}
```

**Response:**
```json
{
  "status": "success|error",
  "result": "string - generated code or result",
  "iterations": "integer - iterations used",
  "tokens_used": {
    "prompt_tokens": "integer",
    "completion_tokens": "integer",
    "total_tokens": "integer"
  },
  "execution_time_seconds": "float",
  "errors": ["string - any errors encountered"]
}
```

**Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/agent/run",
    json={
        "prompt": "Create a REST API with FastAPI that returns current weather",
        "max_iterations": 5,
        "model": "gpt-4",
        "temperature": 0.3
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Result:\n{result['result']}")
print(f"Tokens used: {result['tokens_used']['total_tokens']}")
```

---

### Get Agent Status
**`GET /agent/status/{session_id}`** (Planned)

Get the status of an ongoing agent execution.

---

## Authentication

### API Key Authentication
```bash
curl -H "Authorization: Bearer sk-..." http://localhost:8000/health
```

### Environment Variables
```bash
export OPENAI_API_KEY="sk-..."
export CLAUDE_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk-..."
```

---

## Response Formats

### Success Response
```json
{
  "status": "success",
  "result": "Generated code or output",
  "metadata": {
    "iterations": 3,
    "execution_time": 45.2,
    "model": "gpt-4"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": "error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "error details"
  }
}
```

### Common Error Codes
- `INVALID_PROMPT`: Prompt is empty or invalid
- `MODEL_NOT_FOUND`: Specified model not available
- `API_KEY_MISSING`: No API key provided
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `EXECUTION_ERROR`: Error during code execution

---

## Examples

### Example 1: Simple Code Generation

```python
import requests
import json

def generate_code(prompt, max_iterations=3):
    """Generate code using gpt-computer API."""

    url = "http://localhost:8000/agent/run"

    payload = {
        "prompt": prompt,
        "max_iterations": max_iterations,
        "model": "gpt-4",
        "temperature": 0.5
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["result"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
code = generate_code("Create a Python function that calculates fibonacci numbers")
print(code)
```

### Example 2: Build a Web Application

```python
import requests

def build_web_app(name, description):
    """Build a new web application."""

    prompt = f"""Create a web application with the following specifications:
    Name: {name}
    Description: {description}

    Include:
    - FastAPI backend
    - Simple HTML frontend
    - Docker configuration
    - Unit tests
    """

    response = requests.post(
        "http://localhost:8000/agent/run",
        json={
            "prompt": prompt,
            "max_iterations": 10,
            "temperature": 0.3
        }
    )

    return response.json()

# Usage
result = build_web_app(
    name="Task Manager",
    description="A simple web-based task manager with database storage"
)

print(f"Status: {result['status']}")
print(f"Generated code:\n{result['result']}")
```

### Example 3: Improve Existing Code

```python
def improve_code(original_code, improvement_request):
    """Improve existing code based on request."""

    prompt = f"""
    Here is the original code:
    ```
    {original_code}
    ```

    Please {improvement_request}
    """

    response = requests.post(
        "http://localhost:8000/agent/run",
        json={"prompt": prompt, "max_iterations": 3}
    )

    return response.json()["result"]

# Usage
original = """
def add(a, b):
    return a + b
"""

improved = improve_code(
    original,
    "add type hints, docstring, and error handling"
)
print(improved)
```

---

## Error Handling

### Implementing Robust Error Handling

```python
import requests
from typing import Dict, Optional

def call_agent_api(prompt: str) -> Optional[Dict]:
    """Call agent API with comprehensive error handling."""

    try:
        response = requests.post(
            "http://localhost:8000/agent/run",
            json={"prompt": prompt},
            timeout=300  # 5 minute timeout
        )

        # Check for HTTP errors
        response.raise_for_status()

        data = response.json()

        # Check for API-level errors
        if data.get("status") == "error":
            error_code = data.get("code", "UNKNOWN")
            error_msg = data.get("error", "Unknown error")
            print(f"API Error [{error_code}]: {error_msg}")
            return None

        return data

    except requests.Timeout:
        print("Request timed out - operation took too long")
        return None
    except requests.ConnectionError:
        print("Failed to connect to API server")
        return None
    except requests.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# Usage
result = call_agent_api("Create a hello world program in Python")
if result:
    print(f"Success! Result:\n{result['result']}")
```

---

## Rate Limiting

### Current Limits
- **Default**: 100 requests per hour
- **Pro**: 1000 requests per hour
- **Enterprise**: Custom limits

### Handling Rate Limits

```python
import requests
import time

def call_with_retry(prompt: str, max_retries: int = 3) -> Optional[Dict]:
    """Call API with automatic retry on rate limit."""

    for attempt in range(max_retries):
        response = requests.post(
            "http://localhost:8000/agent/run",
            json={"prompt": prompt}
        )

        # Rate limit - wait and retry
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response.json() if response.ok else None

    print("Max retries exceeded")
    return None
```

---

## Webhooks & Events (Planned)

**Coming in version 0.2.0**

Receive notifications when:
- Code generation completes
- Errors occur
- Iterations progress
- Resource limits are reached

```python
# Example webhook setup (future)
requests.post(
    "http://localhost:8000/webhooks/register",
    json={
        "event": "agent.complete",
        "url": "https://your-server.com/webhook",
        "secret": "webhook-secret"
    }
)
```

---

## SDK & Libraries

### Python Client Library
```python
from gpt_computer import GptComputerAPI

api = GptComputerAPI(api_key="sk-...", base_url="http://localhost:8000")
result = await api.agent.run_async("Generate Python code for...")
```

### JavaScript/TypeScript Library
```typescript
import { GptComputerAPI } from 'gpt-computer-js';

const api = new GptComputerAPI({ apiKey: 'sk-...' });
const result = await api.agent.run({ prompt: '...' });
```

---

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app
RUN pip install gpt-computer

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

CMD ["python", "-m", "uvicorn", "gpt_computer.api.main:app", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  gpt-computer:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./projects:/app/projects
```

### Kubernetes Deployment
See [docs/deployment.md](deployment.md) for detailed Kubernetes setup.

---

## Best Practices

### For Production Use
1. **Use HTTPS**: Always encrypt API communications
2. **API Key Rotation**: Rotate keys regularly
3. **Rate Limiting**: Implement client-side rate limiting
4. **Error Handling**: Implement comprehensive error handling
5. **Monitoring**: Track API performance and errors
6. **Logging**: Log requests and responses for debugging
7. **Timeouts**: Set appropriate request timeouts
8. **Caching**: Cache results to reduce API calls

### Code Examples
```python
# ✅ Good practices
api_key = os.getenv("OPENAI_API_KEY")  # Get from env, not hardcoded
timeout = 300  # Set timeout
errors = []  # Track errors
try:
    # ... API call ...
except Exception as e:
    errors.append(str(e))

# ❌ Avoid
api_key = "sk-hardcoded-key"  # Never hardcode
# No timeout handling
# No error handling
```

---

## Troubleshooting

### Common Issues

**Problem**: `Connection refused`
- **Solution**: Ensure API server is running on correct port

**Problem**: `Authentication failed`
- **Solution**: Check API key is set and valid

**Problem**: `Timeout errors`
- **Solution**: Increase timeout for complex tasks

**Problem**: `Out of memory`
- **Solution**: Use smaller projects or reduce max_iterations

---

## API Reference

For detailed API reference, see [api_reference.rst](api_reference.rst)

## Related Documentation

- [MODULE_STRUCTURE.md](MODULE_STRUCTURE.md) - API code structure
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [TESTING.md](TESTING.md) - API testing guide

---

**Last Updated**: March 2025
**API Version**: 0.1.1
