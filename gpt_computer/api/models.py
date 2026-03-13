from typing import Optional

from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_iterations: int = 10


class AgentRunResponse(BaseModel):
    result: str
    steps: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    version: str
