"""Multi-Agent Orchestration Framework

This module provides coordination for multiple agents working together
on complex tasks with dependency management and result aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from gpt_computer.agent.prompt import Prompt
from gpt_computer.infrastructure.files.operations import FilesDict


class AgentType(Enum):
    """Types of specialized agents."""

    ARCHITECT = "architect"
    IMPLEMENTATION = "implementation"
    TEST = "test"
    REVIEW = "review"
    OPTIMIZATION = "optimization"


@dataclass
class Task:
    """Unit of work for an agent."""

    id: str
    name: str
    description: str
    agent_type: AgentType
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[FilesDict] = None
    status: str = "pending"  # pending, in_progress, completed, failed


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    task_results: Dict[str, FilesDict]
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    execution_time: float


class Orchestrator:
    """Coordinates multiple agents on a complex task."""

    def __init__(self):
        """Initialize orchestrator."""
        self.agents: Dict[AgentType, Any] = {}
        self.task_queue: List[Task] = []
        self.results: Dict[str, FilesDict] = {}

    def register_agent(self, agent_type: AgentType, agent: Any) -> None:
        """Register an agent type.

        Args:
            agent_type: Type identifier for the agent
            agent: Agent instance
        """
        self.agents[agent_type] = agent

    def create_workflow(
        self,
        tasks: List[Task],
    ) -> None:
        """Create a workflow from tasks.

        Args:
            tasks: List of tasks to execute
        """
        self.task_queue = tasks
        self.results = {}

    def _build_dependency_graph(self, tasks: List[Task]) -> List[Task]:
        """Build task execution order from dependencies using topological sort.

        Args:
            tasks: List of tasks with dependencies

        Returns:
            Tasks ordered by dependency (topological sort)
        """
        # Create adjacency list
        in_degree = {task.id: 0 for task in tasks}
        graph = {task.id: [] for task in tasks}
        task_map = {task.id: task for task in tasks}

        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph[dep_id].append(task.id)
                    in_degree[task.id] += 1

        # Topological sort using Kahn's algorithm
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        ordered = []

        while queue:
            task_id = queue.pop(0)
            ordered.append(task_map[task_id])

            for neighbor_id in graph[task_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        return ordered

    def _gather_context(
        self, task: Task, results: Dict[str, FilesDict]
    ) -> Dict[str, Any]:
        """Gather results from dependent tasks.

        Args:
            task: Current task
            results: Results from completed tasks

        Returns:
            Context dictionary with dependency results
        """
        context = task.context.copy()
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id in results:
                    context[dep_id] = results[dep_id]
        return context

    async def execute_workflow(
        self,
        tasks: Optional[List[Task]] = None,
    ) -> WorkflowResult:
        """Execute a workflow of dependent tasks.

        Args:
            tasks: List of tasks (uses self.task_queue if not provided)

        Returns:
            WorkflowResult with task results and statistics
        """
        import time

        if tasks:
            self.create_workflow(tasks)
        elif not self.task_queue:
            raise ValueError("No tasks to execute")

        start_time = time.time()
        ordered_tasks = self._build_dependency_graph(self.task_queue)

        completed = 0
        failed = 0

        for task in ordered_tasks:
            task.status = "in_progress"

            # Check if agent is registered
            if task.agent_type not in self.agents:
                self.results[task.id] = FilesDict(
                    {"error.md": f"No agent registered for type {task.agent_type}"}
                )
                task.status = "failed"
                failed += 1
                continue

            # Gather context from dependencies
            context = self._gather_context(task, self.results)

            # Execute task
            try:
                agent = self.agents[task.agent_type]
                prompt = Prompt(text=task.description)

                # Check if this is an init task (no dependencies) or improve task
                if task.dependencies:
                    # Use improve with context from dependencies
                    # Merge context files into a FilesDict
                    context_files = FilesDict()
                    for dep_id, dep_result in context.items():
                        if isinstance(dep_result, FilesDict):
                            context_files.update(dep_result)

                    result = await agent.improve(context_files, prompt)
                else:
                    # Use init for first task
                    result = await agent.init(prompt)

                self.results[task.id] = result
                task.status = "completed"
                completed += 1
            except Exception as e:
                self.results[task.id] = FilesDict({"error.md": f"Error: {str(e)}"})
                task.status = "failed"
                failed += 1

        execution_time = time.time() - start_time

        return WorkflowResult(
            task_results=self.results,
            total_tasks=len(ordered_tasks),
            completed_tasks=completed,
            failed_tasks=failed,
            execution_time=execution_time,
        )

    def get_workflow_status(self) -> Dict[str, str]:
        """Get current status of all tasks.

        Returns:
            Dictionary mapping task IDs to status
        """
        return {task.id: task.status for task in self.task_queue}
