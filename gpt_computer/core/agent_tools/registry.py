import asyncio
import logging

from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Tool(BaseModel):
    name: str
    description: str
    args_schema: Type[BaseModel]
    func: Callable[..., Any]
    is_async: bool = False

    async def run(self, **kwargs) -> Any:
        # Validate arguments
        validated_args = self.args_schema(**kwargs)

        try:
            if self.is_async:
                return await self.func(**validated_args.model_dump())
            else:
                # Run sync functions in a thread to avoid blocking
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(
                    None, lambda: self.func(**validated_args.model_dump())
                )
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return {"error": str(e)}


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        args_schema: Type[BaseModel],
        func: Callable[..., Any],
        is_async: bool = False,
    ):
        tool = Tool(
            name=name,
            description=description,
            args_schema=args_schema,
            func=func,
            is_async=is_async,
        )
        self.tools[name] = tool
        logger.debug(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [
            {"name": t.name, "description": t.description} for t in self.tools.values()
        ]

    async def execute(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool {name} not found"}
        return await tool.run(**kwargs)
