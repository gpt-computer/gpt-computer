"""Tests for multi-agent orchestration."""

import pytest
import asyncio
from gpt_computer.agent.orchestration import (
    AgentType,
    Orchestrator,
    Task,
    WorkflowResult,
    ArchitectAgent,
    ImplementationAgent,
    TestAgent,
    ReviewAgent,
)
from gpt_computer.agent.prompt import Prompt
from gpt_computer.infrastructure.files.operations import FilesDict


class MockAIClient:
    """Mock AI client for testing."""

    pass


class TestOrchestrator:
    """Test orchestrator functionality."""

    def test_register_agent(self):
        """Test registering agents."""
        orchestrator = Orchestrator()
        agent = ArchitectAgent(MockAIClient())

        orchestrator.register_agent(AgentType.ARCHITECT, agent)

        assert AgentType.ARCHITECT in orchestrator.agents
        assert orchestrator.agents[AgentType.ARCHITECT] == agent

    def test_create_workflow(self):
        """Test creating a workflow."""
        orchestrator = Orchestrator()

        tasks = [
            Task(
                id="task1",
                name="Design architecture",
                description="Design system architecture",
                agent_type=AgentType.ARCHITECT,
            ),
            Task(
                id="task2",
                name="Implement features",
                description="Implement the features",
                agent_type=AgentType.IMPLEMENTATION,
                dependencies=["task1"],
            ),
        ]

        orchestrator.create_workflow(tasks)

        assert len(orchestrator.task_queue) == 2
        assert orchestrator.task_queue[0].id == "task1"
        assert orchestrator.task_queue[1].id == "task2"

    def test_build_dependency_graph(self):
        """Test topological sort of dependencies."""
        orchestrator = Orchestrator()

        tasks = [
            Task(
                id="task1",
                name="Task 1",
                description="First task",
                agent_type=AgentType.ARCHITECT,
            ),
            Task(
                id="task2",
                name="Task 2",
                description="Second task",
                agent_type=AgentType.IMPLEMENTATION,
                dependencies=["task1"],
            ),
            Task(
                id="task3",
                name="Task 3",
                description="Third task",
                agent_type=AgentType.TEST,
                dependencies=["task2"],
            ),
        ]

        ordered = orchestrator._build_dependency_graph(tasks)

        assert ordered[0].id == "task1"
        assert ordered[1].id == "task2"
        assert ordered[2].id == "task3"

    @pytest.mark.asyncio
    async def test_execute_workflow_simple(self):
        """Test executing a simple workflow."""
        orchestrator = Orchestrator()

        # Register agent
        agent = ArchitectAgent(MockAIClient())
        orchestrator.register_agent(AgentType.ARCHITECT, agent)

        # Create workflow
        tasks = [
            Task(
                id="task1",
                name="Design architecture",
                description="Design system architecture",
                agent_type=AgentType.ARCHITECT,
            ),
        ]

        result = await orchestrator.execute_workflow(tasks)

        assert isinstance(result, WorkflowResult)
        assert result.total_tasks == 1
        assert result.completed_tasks == 1
        assert result.failed_tasks == 0
        assert "task1" in result.task_results

    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self):
        """Test executing a workflow with dependencies."""
        orchestrator = Orchestrator()

        # Register agents
        architect = ArchitectAgent(MockAIClient())
        impl = ImplementationAgent(MockAIClient())
        orchestrator.register_agent(AgentType.ARCHITECT, architect)
        orchestrator.register_agent(AgentType.IMPLEMENTATION, impl)

        # Create workflow with dependencies
        tasks = [
            Task(
                id="task1",
                name="Design architecture",
                description="Design system architecture",
                agent_type=AgentType.ARCHITECT,
            ),
            Task(
                id="task2",
                name="Implement features",
                description="Implement the features",
                agent_type=AgentType.IMPLEMENTATION,
                dependencies=["task1"],
            ),
        ]

        result = await orchestrator.execute_workflow(tasks)

        assert result.total_tasks == 2
        assert result.completed_tasks == 2
        assert result.failed_tasks == 0
        assert "task1" in result.task_results
        assert "task2" in result.task_results

    @pytest.mark.asyncio
    async def test_execute_workflow_missing_agent(self):
        """Test executing workflow with missing agent."""
        orchestrator = Orchestrator()

        # Create workflow without registering agent
        tasks = [
            Task(
                id="task1",
                name="Design architecture",
                description="Design system architecture",
                agent_type=AgentType.ARCHITECT,
            ),
        ]

        result = await orchestrator.execute_workflow(tasks)

        assert result.total_tasks == 1
        assert result.completed_tasks == 0
        assert result.failed_tasks == 1
        assert "error.md" in result.task_results["task1"]

    def test_get_workflow_status(self):
        """Test getting workflow status."""
        orchestrator = Orchestrator()

        tasks = [
            Task(
                id="task1",
                name="Task 1",
                description="First task",
                agent_type=AgentType.ARCHITECT,
                status="pending",
            ),
            Task(
                id="task2",
                name="Task 2",
                description="Second task",
                agent_type=AgentType.IMPLEMENTATION,
                status="completed",
            ),
        ]

        orchestrator.create_workflow(tasks)
        status = orchestrator.get_workflow_status()

        assert status["task1"] == "pending"
        assert status["task2"] == "completed"


class TestSpecializedAgents:
    """Test specialized agent implementations."""

    @pytest.mark.asyncio
    async def test_architect_agent_init(self):
        """Test architect agent init."""
        agent = ArchitectAgent(MockAIClient())
        prompt = Prompt(text="Design a REST API")

        result = await agent.init(prompt)

        assert isinstance(result, FilesDict)
        assert "architecture.md" in result

    @pytest.mark.asyncio
    async def test_implementation_agent_init(self):
        """Test implementation agent init."""
        agent = ImplementationAgent(MockAIClient())
        prompt = Prompt(text="Implement the API")

        result = await agent.init(prompt)

        assert isinstance(result, FilesDict)
        assert "main.py" in result

    @pytest.mark.asyncio
    async def test_test_agent_init(self):
        """Test test agent init."""
        agent = TestAgent(MockAIClient())
        prompt = Prompt(text="Write tests")

        result = await agent.init(prompt)

        assert isinstance(result, FilesDict)
        assert "test_main.py" in result

    @pytest.mark.asyncio
    async def test_review_agent_init(self):
        """Test review agent init."""
        agent = ReviewAgent(MockAIClient())
        prompt = Prompt(text="Review the code")

        result = await agent.init(prompt)

        assert isinstance(result, FilesDict)
        assert "review.md" in result
