from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gpt_computer.api.models import AgentRunRequest, AgentRunResponse, HealthResponse
from gpt_computer.core.agent.react import ReActAgent
from gpt_computer.core.agent_tools.registry import ToolRegistry
from gpt_computer.core.ai import AI
from gpt_computer.core.config import get_settings

app = FastAPI(title="GPT Computer API", version="0.1.0")

# Setup a default registry (mock for now, or basic tools)
registry = ToolRegistry()


# Add a basic tool for demonstration
class CalculatorInput(BaseModel):
    expression: str


def calculate(expression: str) -> str:
    """Evaluates a mathematical expression safely."""
    try:
        # VERY UNSAFE in production, but okay for this demo/prototype phase
        # In real world, use a safe math parser
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error: {e}"


registry.register(
    name="calculate",
    description="Evaluates a mathematical expression (e.g., '2 + 2')",
    args_schema=CalculatorInput,
    func=calculate,
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="0.1.0")


@app.post("/agent/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest):
    settings = get_settings()

    # Initialize AI with request specific or default settings
    try:
        ai = AI(
            model_name=request.model,
            temperature=request.temperature,
            azure_endpoint=settings.azure_openai_endpoint,
        )

        agent = ReActAgent(ai=ai, tools=registry, max_iterations=request.max_iterations)

        result = await agent.run(request.prompt)

        return AgentRunResponse(result=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
