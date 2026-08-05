import uuid

from datetime import datetime
from typing import Any, Dict, List, Optional


class ExecutionEnvironment:
    def __init__(
        self,
        env_id: str,
        name: str,
        env_type: str,
        description: str = "",
        configuration: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = env_id
        self.name = name
        self.type = env_type
        self.description = description
        self.configuration = configuration or {}
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.status = "active"
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.resource_usage = {
            "cpu": 0.0,
            "memory": 0.0,
            "storage": 0.0,
            "network": 0.0,
        }
        self.running_tasks = []

    def update_resource_usage(self, resource_type: str, usage: float) -> None:
        if resource_type in self.resource_usage:
            self.resource_usage[resource_type] = usage
        self.last_updated = datetime.now()

    def add_running_task(self, task_id: str) -> None:
        if task_id not in self.running_tasks:
            self.running_tasks.append(task_id)

    def remove_running_task(self, task_id: str) -> None:
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)

    def is_available(self, required_resources: Dict[str, float]) -> bool:
        for resource_type, required in required_resources.items():
            if (
                resource_type in self.resource_usage
                and self.resource_usage[resource_type] >= required
            ):
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "configuration": self.configuration,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "resource_usage": self.resource_usage,
            "running_tasks": self.running_tasks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionEnvironment":
        return cls(
            env_id=data["id"],
            name=data["name"],
            env_type=data["type"],
            description=data["description"],
            configuration=data.get("configuration", {}),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {}),
        )


class ExecutionTask:
    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        environment_id: str,
        command: str,
        arguments: Optional[List[str]] = None,
        working_directory: Optional[str] = None,
        timeout: Optional[int] = None,
        resources: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = task_id
        self.name = name
        self.description = description
        self.environment_id = environment_id
        self.command = command
        self.arguments = arguments or []
        self.working_directory = working_directory
        self.timeout = timeout
        self.resources = resources or {}
        self.metadata = metadata or {}
        self.status = "pending"
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.output = None
        self.pid = None
        self.logs = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "environment_id": self.environment_id,
            "command": self.command,
            "arguments": self.arguments,
            "working_directory": self.working_directory,
            "timeout": self.timeout,
            "resources": self.resources,
            "metadata": self.metadata,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "result": self.result,
            "error": self.error,
            "output": self.output,
            "pid": self.pid,
            "logs": self.logs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionTask":
        task = cls(
            task_id=data["id"],
            name=data["name"],
            description=data["description"],
            environment_id=data["environment_id"],
            command=data["command"],
            arguments=data.get("arguments", []),
            working_directory=data.get("working_directory"),
            timeout=data.get("timeout"),
            resources=data.get("resources", {}),
            metadata=data.get("metadata", {}),
        )

        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])

        task.status = data["status"]
        task.result = data.get("result")
        task.error = data.get("error")
        task.output = data.get("output")
        task.pid = data.get("pid")
        task.logs = data.get("logs", [])

        return task


class ExecutionFabric:
    def __init__(self):
        self.environments: Dict[str, ExecutionEnvironment] = {}
        self.tasks: Dict[str, ExecutionTask] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def register_environment(
        self,
        name: str,
        env_type: str,
        description: str = "",
        configuration: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        env_id = f"env_{uuid.uuid4().hex[:8]}"
        environment = ExecutionEnvironment(
            env_id=env_id,
            name=name,
            env_type=env_type,
            description=description,
            configuration=configuration,
            capabilities=capabilities,
            metadata=metadata,
        )

        self.environments[env_id] = environment
        return env_id

    def unregister_environment(self, env_id: str) -> bool:
        if env_id in self.environments:
            del self.environments[env_id]
            return True
        return False

    def get_environment(self, env_id: str) -> Optional[ExecutionEnvironment]:
        return self.environments.get(env_id)

    def get_environments_by_type(self, env_type: str) -> List[ExecutionEnvironment]:
        return [env for env in self.environments.values() if env.type == env_type]

    def get_available_environments(
        self, required_resources: Optional[Dict[str, float]] = None
    ) -> List[ExecutionEnvironment]:
        available = []

        for env in self.environments.values():
            if required_resources:
                if env.is_available(required_resources):
                    available.append(env)
            else:
                available.append(env)

        return available

    def create_task(
        self,
        name: str,
        description: str,
        environment_id: str,
        command: str,
        arguments: Optional[List[str]] = None,
        working_directory: Optional[str] = None,
        timeout: Optional[int] = None,
        resources: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        env = self.environments.get(environment_id)
        if not env:
            raise ValueError(f"Environment not found: {environment_id}")

        if resources and not env.is_available(resources):
            raise ValueError(
                f"Environment {environment_id} does not have sufficient resources"
            )

        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = ExecutionTask(
            task_id=task_id,
            name=name,
            description=description,
            environment_id=environment_id,
            command=command,
            arguments=arguments,
            working_directory=working_directory,
            timeout=timeout,
            resources=resources,
            metadata=metadata,
        )

        self.tasks[task_id] = task
        env.add_running_task(task_id)

        return task_id

    def get_task(self, task_id: str) -> Optional[ExecutionTask]:
        return self.tasks.get(task_id)

    def get_tasks_by_environment(self, environment_id: str) -> List[ExecutionTask]:
        return [
            task
            for task in self.tasks.values()
            if task.environment_id == environment_id
        ]

    def get_tasks_by_status(self, status: str) -> List[ExecutionTask]:
        return [task for task in self.tasks.values() if task.status == status]

    def start_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status != "pending":
            return False

        env = self.environments.get(task.environment_id)
        if not env:
            return False

        task.status = "running"
        task.started_at = datetime.now()
        env.add_running_task(task_id)

        return True

    def complete_task(
        self, task_id: str, result: Any, error: Optional[str] = None
    ) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status not in ["pending", "running"]:
            return False

        task.status = "completed" if error is None else "failed"
        task.completed_at = datetime.now()
        task.result = result
        task.error = error

        env = self.environments.get(task.environment_id)
        if env:
            env.remove_running_task(task_id)

        self.execution_history.append(
            {
                "task_id": task_id,
                "name": task.name,
                "environment_id": task.environment_id,
                "status": task.status,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat()
                if task.completed_at
                else None,
                "result": task.result,
                "error": task.error,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return True

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status not in ["pending", "running"]:
            return False

        task.status = "cancelled"
        task.completed_at = datetime.now()
        task.error = "Task cancelled by user"

        env = self.environments.get(task.environment_id)
        if env:
            env.remove_running_task(task_id)

        self.execution_history.append(
            {
                "task_id": task_id,
                "name": task.name,
                "environment_id": task.environment_id,
                "status": task.status,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat()
                if task.completed_at
                else None,
                "result": task.result,
                "error": task.error,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return True

    def get_task_output(self, task_id: str) -> Optional[str]:
        task = self.tasks.get(task_id)
        if not task:
            return None

        return task.output

    def add_task_output(self, task_id: str, output: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status not in ["running", "completed"]:
            return False

        task.output = output
        if task.logs:
            task.logs.append(output)
        else:
            task.logs = [output]

        return True

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "total_environments": len(self.environments),
            "total_tasks": len(self.tasks),
            "running_tasks": len(
                [t for t in self.tasks.values() if t.status == "running"]
            ),
            "pending_tasks": len(
                [t for t in self.tasks.values() if t.status == "pending"]
            ),
            "completed_tasks": len(
                [t for t in self.tasks.values() if t.status == "completed"]
            ),
            "failed_tasks": len(
                [t for t in self.tasks.values() if t.status == "failed"]
            ),
            "cancelled_tasks": len(
                [t for t in self.tasks.values() if t.status == "cancelled"]
            ),
            "environments_by_type": {
                env_type: len(
                    [e for e in self.environments.values() if e.type == env_type]
                )
                for env_type in set(e.type for e in self.environments.values())
            },
        }

    def export_environment_state(self, env_id: str) -> Dict[str, Any]:
        env = self.environments.get(env_id)
        if not env:
            raise ValueError(f"Environment not found: {env_id}")

        return env.to_dict()

    def import_environment_state(self, env_state: Dict[str, Any]) -> str:
        env = ExecutionEnvironment.from_dict(env_state)
        self.environments[env.id] = env
        return env.id

    def export_task_state(self, task_id: str) -> Dict[str, Any]:
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        return task.to_dict()

    def import_task_state(self, task_state: Dict[str, Any]) -> str:
        task = ExecutionTask.from_dict(task_state)
        self.tasks[task.id] = task
        return task.id

    def get_execution_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        history = self.execution_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def clear_history(self) -> None:
        self.execution_history = []
