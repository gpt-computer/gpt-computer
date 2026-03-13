from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from gpt_computer.api.main import app
from gpt_computer.core.agent.react import ReActAgent
from gpt_computer.core.ai import AI

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_run_agent(monkeypatch):
    # Mock AI and Agent
    mock_ai = MagicMock(spec=AI)
    mock_agent = MagicMock(spec=ReActAgent)
    mock_agent.run = AsyncMock(return_value="Calculated 4")

    # We need to mock the classes in api.main, not core
    monkeypatch.setattr("gpt_computer.api.main.AI", lambda **kwargs: mock_ai)
    monkeypatch.setattr("gpt_computer.api.main.ReActAgent", lambda **kwargs: mock_agent)

    response = client.post(
        "/agent/run", json={"prompt": "Calculate 2+2", "max_iterations": 5}
    )

    assert response.status_code == 200
    assert response.json()["result"] == "Calculated 4"
