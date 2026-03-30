from typing import Any, List, Optional


class MockAI:
    def __init__(self, response: List):
        self.responses = iter(response)

    async def start(self, system: str, user: Any, *, step_name: str) -> List[str]:
        return [next(self.responses)]

    async def next(
        self, messages: List[str], prompt: Optional[str] = None, *, step_name: str
    ) -> List[str]:
        return [next(self.responses)]
