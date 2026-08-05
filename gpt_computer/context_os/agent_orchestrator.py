from datetime import datetime
from typing import Any, Dict, List, Optional


class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.context_assignments: Dict[str, List[str]] = {}

    def register_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: List[str],
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        agent = {
            "id": agent_id,
            "name": name,
            "type": agent_type,
            "capabilities": capabilities,
            "description": description,
            "metadata": metadata or {},
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "assigned_contexts": [],
            "current_task": None,
        }

        self.agents[agent_id] = agent
        return agent_id

    def unregister_agent(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Remove from all contexts
            for context_id, agent_ids in self.context_assignments.items():
                if agent_id in agent_ids:
                    agent_ids.remove(agent_id)
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self.agents.get(agent_id)

    def get_agents_by_type(self, agent_type: str) -> List[Dict[str, Any]]:
        return [agent for agent in self.agents.values() if agent["type"] == agent_type]

    def get_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        return [
            agent
            for agent in self.agents.values()
            if capability in agent["capabilities"]
        ]

    def assign_agent_to_context(self, agent_id: str, context_id: str) -> bool:
        if agent_id not in self.agents:
            return False

        if context_id not in self.context_assignments:
            self.context_assignments[context_id] = []

        if agent_id not in self.context_assignments[context_id]:
            self.context_assignments[context_id].append(agent_id)
            self.agents[agent_id]["assigned_contexts"].append(context_id)
            return True

        return False

    def remove_agent_from_context(self, agent_id: str, context_id: str) -> bool:
        if agent_id not in self.agents:
            return False

        if (
            context_id in self.context_assignments
            and agent_id in self.context_assignments[context_id]
        ):
            self.context_assignments[context_id].remove(agent_id)
            if agent_id in self.agents[agent_id]["assigned_contexts"]:
                self.agents[agent_id]["assigned_contexts"].remove(context_id)
            return True

        return False

    def get_agents_for_context(self, context_id: str) -> List[Dict[str, Any]]:
        if context_id not in self.context_assignments:
            return []

        return [
            self.agents[agent_id] for agent_id in self.context_assignments[context_id]
        ]

    def create_task(
        self,
        task_id: str,
        name: str,
        description: str,
        context_id: str,
        required_capabilities: List[str],
        priority: str = "medium",
        deadline: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        # Find suitable agents
        suitable_agents = []
        for agent in self.agents.values():
            if all(cap in agent["capabilities"] for cap in required_capabilities):
                suitable_agents.append(agent["id"])

        task = {
            "id": task_id,
            "name": name,
            "description": description,
            "context_id": context_id,
            "required_capabilities": required_capabilities,
            "suitable_agents": suitable_agents,
            "assigned_agent": None,
            "priority": priority,
            "deadline": deadline.isoformat() if deadline else None,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "metadata": metadata or {},
        }

        self.tasks[task_id] = task
        return task_id

    def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        task = self.tasks.get(task_id)
        agent = self.agents.get(agent_id)

        if not task or not agent:
            return False

        if task["status"] != "pending":
            return False

        if agent["status"] != "active":
            return False

        task["assigned_agent"] = agent_id
        task["status"] = "in_progress"
        task["started_at"] = datetime.now().isoformat()
        agent["current_task"] = task_id

        return True

    def complete_task(
        self, task_id: str, result: Any, error: Optional[str] = None
    ) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["status"] = "completed" if error is None else "failed"
        task["completed_at"] = datetime.now().isoformat()
        task["result"] = result
        task["error"] = error

        if task["assigned_agent"]:
            agent = self.agents.get(task["assigned_agent"])
            if agent:
                agent["current_task"] = None

        return True

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

    def get_tasks_by_context(self, context_id: str) -> List[Dict[str, Any]]:
        return [
            task for task in self.tasks.values() if task["context_id"] == context_id
        ]

    def get_tasks_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        return [
            task for task in self.tasks.values() if task["assigned_agent"] == agent_id
        ]

    def create_workflow(
        self,
        workflow_id: str,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "steps": steps,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "metadata": metadata or {},
        }

        self.workflows[workflow_id] = workflow
        return workflow_id

    def execute_workflow(self, workflow_id: str, context_id: str) -> bool:
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False

        if workflow["status"] != "pending":
            return False

        workflow["status"] = "in_progress"
        workflow["started_at"] = datetime.now().isoformat()

        # Execute each step
        for step in workflow["steps"]:
            # Execute step logic here
            pass

        workflow["status"] = "completed"
        workflow["completed_at"] = datetime.now().isoformat()
        workflow["result"] = {"status": "success", "message": "Workflow completed"}

        return True

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.workflows.get(workflow_id)

    def get_workflows_by_context(self, context_id: str) -> List[Dict[str, Any]]:
        return [
            workflow
            for workflow in self.workflows.values()
            if workflow["metadata"].get("context_id") == context_id
        ]

    def get_agent_workflows(self, agent_id: str) -> List[Dict[str, Any]]:
        return [
            workflow
            for workflow in self.workflows.values()
            if workflow["metadata"].get("assigned_agent") == agent_id
        ]

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "total_tasks": len(self.tasks),
            "total_workflows": len(self.workflows),
            "active_agents": len(
                [a for a in self.agents.values() if a["status"] == "active"]
            ),
            "pending_tasks": len(
                [t for t in self.tasks.values() if t["status"] == "pending"]
            ),
            "in_progress_tasks": len(
                [t for t in self.tasks.values() if t["status"] == "in_progress"]
            ),
            "completed_tasks": len(
                [t for t in self.tasks.values() if t["status"] == "completed"]
            ),
            "failed_tasks": len(
                [t for t in self.tasks.values() if t["status"] == "failed"]
            ),
            "active_workflows": len(
                [w for w in self.workflows.values() if w["status"] == "in_progress"]
            ),
            "completed_workflows": len(
                [w for w in self.workflows.values() if w["status"] == "completed"]
            ),
        }

    def export_agent_state(self, agent_id: str) -> Dict[str, Any]:
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        return {
            "agent_id": agent["id"],
            "name": agent["name"],
            "type": agent["type"],
            "capabilities": agent["capabilities"],
            "description": agent["description"],
            "metadata": agent["metadata"],
            "status": agent["status"],
            "last_active": agent["last_active"],
            "assigned_contexts": agent["assigned_contexts"],
            "current_task": agent["current_task"],
        }

    def import_agent_state(self, agent_state: Dict[str, Any]) -> str:
        agent_id = agent_state["agent_id"]
        self.agents[agent_id] = agent_state
        return agent_id

    def export_task_state(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        return {
            "task_id": task["id"],
            "name": task["name"],
            "description": task["description"],
            "context_id": task["context_id"],
            "required_capabilities": task["required_capabilities"],
            "assigned_agent": task["assigned_agent"],
            "priority": task["priority"],
            "deadline": task["deadline"],
            "status": task["status"],
            "created_at": task["created_at"],
            "started_at": task["started_at"],
            "completed_at": task["completed_at"],
            "result": task["result"],
            "error": task["error"],
            "metadata": task["metadata"],
        }

    def import_task_state(self, task_state: Dict[str, Any]) -> str:
        task_id = task_state["task_id"]
        self.tasks[task_id] = task_state
        return task_id

    def export_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        return {
            "workflow_id": workflow["id"],
            "name": workflow["name"],
            "description": workflow["description"],
            "steps": workflow["steps"],
            "status": workflow["status"],
            "created_at": workflow["created_at"],
            "started_at": workflow["started_at"],
            "completed_at": workflow["completed_at"],
            "result": workflow["result"],
            "error": workflow["error"],
            "metadata": workflow["metadata"],
        }

    def import_workflow_state(self, workflow_state: Dict[str, Any]) -> str:
        workflow_id = workflow_state["workflow_id"]
        self.workflows[workflow_id] = workflow_state
        return workflow_id
