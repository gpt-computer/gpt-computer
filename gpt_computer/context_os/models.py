import uuid

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ContextType(Enum):
    PROJECT = "project"
    MODULE = "module"
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    INTERFACE = "interface"
    ENUM = "enum"
    CONSTANT = "constant"
    DATA = "data"
    SERVICE = "service"
    TASK = "task"
    MEETING = "meeting"
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    ROADMAP = "roadmap"
    AGENT = "agent"
    KNOWLEDGE = "knowledge"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"


class ContextStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ContextMetadata:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    description: str = ""
    type: ContextType = ContextType.PROJECT
    status: ContextStatus = ContextStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    last_modified_by: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, Any] = field(default_factory=dict)
    sharing: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextState:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    context_id: str = ""
    state_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "context_id": self.context_id,
            "state_type": self.state_type,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextState":
        return cls(
            id=data["id"],
            context_id=data["context_id"],
            state_type=data["state_type"],
            data=data["data"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            created_by=data["created_by"],
            version=data["version"],
        )


@dataclass
class Context:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    metadata: ContextMetadata = field(default_factory=ContextMetadata)
    current_state: Optional[ContextState] = None
    history: List[ContextState] = field(default_factory=list)
    parent_context_id: Optional[str] = None
    child_context_ids: List[str] = field(default_factory=list)
    related_context_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, Any] = field(default_factory=dict)
    sharing: Dict[str, Any] = field(default_factory=dict)
    graph: Optional["ContextGraph"] = None
    agents: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    knowledge: List[str] = field(default_factory=list)
    architecture: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None

    def add_state(self, state: ContextState) -> str:
        self.history.append(state)
        self.current_state = state
        self.metadata.updated_at = datetime.now()
        return state.id

    def update_state(
        self, state_id: str, data: Dict[str, Any], updated_by: str
    ) -> bool:
        for state in self.history:
            if state.id == state_id:
                state.data = data
                state.updated_at = datetime.now()
                state.created_by = updated_by
                self.current_state = state
                self.metadata.updated_at = datetime.now()
                return True
        return False

    def get_state(self, state_id: str) -> Optional[ContextState]:
        for state in self.history:
            if state.id == state_id:
                return state
        return None

    def add_related_context(self, context_id: str) -> None:
        if context_id not in self.related_context_ids:
            self.related_context_ids.append(context_id)

    def remove_related_context(self, context_id: str) -> None:
        if context_id in self.related_context_ids:
            self.related_context_ids.remove(context_id)

    def add_agent(self, agent_id: str) -> None:
        if agent_id not in self.agents:
            self.agents.append(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        if agent_id in self.agents:
            self.agents.remove(agent_id)

    def add_task(self, task_id: str) -> None:
        if task_id not in self.tasks:
            self.tasks.append(task_id)

    def remove_task(self, task_id: str) -> None:
        if task_id in self.tasks:
            self.tasks.remove(task_id)

    def add_service(self, service_id: str) -> None:
        if service_id not in self.services:
            self.services.append(service_id)

    def remove_service(self, service_id: str) -> None:
        if service_id in self.services:
            self.services.remove(service_id)

    def add_knowledge(self, knowledge_id: str) -> None:
        if knowledge_id not in self.knowledge:
            self.knowledge.append(knowledge_id)

    def remove_knowledge(self, knowledge_id: str) -> None:
        if knowledge_id in self.knowledge:
            self.knowledge.remove(knowledge_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "metadata": {
                "id": self.metadata.id,
                "name": self.metadata.name,
                "description": self.metadata.description,
                "type": self.metadata.type.value,
                "status": self.metadata.status.value,
                "created_at": self.metadata.created_at.isoformat(),
                "updated_at": self.metadata.updated_at.isoformat(),
                "created_by": self.metadata.created_by,
                "last_modified_by": self.metadata.last_modified_by,
                "version": self.metadata.version,
                "tags": self.metadata.tags,
                "labels": self.metadata.labels,
                "custom_properties": self.metadata.custom_properties,
                "permissions": self.metadata.permissions,
                "sharing": self.metadata.sharing,
            },
            "current_state_id": self.current_state.id if self.current_state else None,
            "parent_context_id": self.parent_context_id,
            "child_context_ids": self.child_context_ids,
            "related_context_ids": self.related_context_ids,
            "tags": self.tags,
            "labels": self.labels,
            "custom_properties": self.custom_properties,
            "permissions": self.permissions,
            "sharing": self.sharing,
            "agents": self.agents,
            "tasks": self.tasks,
            "services": self.services,
            "knowledge": self.knowledge,
            "architecture": self.architecture,
            "security": self.security,
            "performance": self.performance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        context = cls()
        context.id = data["id"]
        context.metadata = ContextMetadata(
            id=data["metadata"]["id"],
            name=data["metadata"]["name"],
            description=data["metadata"]["description"],
            type=ContextType(data["metadata"]["type"]),
            status=ContextStatus(data["metadata"]["status"]),
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            updated_at=datetime.fromisoformat(data["metadata"]["updated_at"]),
            created_by=data["metadata"]["created_by"],
            last_modified_by=data["metadata"]["last_modified_by"],
            version=data["metadata"]["version"],
            tags=data["metadata"]["tags"],
            labels=data["metadata"]["labels"],
            custom_properties=data["metadata"]["custom_properties"],
            permissions=data["metadata"]["permissions"],
            sharing=data["metadata"]["sharing"],
        )
        if data.get("current_state_id"):
            # Find the current state in history
            for state in data.get("history", []):
                if state["id"] == data["current_state_id"]:
                    context.current_state = ContextState.from_dict(state)
                    break
        context.parent_context_id = data.get("parent_context_id")
        context.child_context_ids = data.get("child_context_ids", [])
        context.related_context_ids = data.get("related_context_ids", [])
        context.tags = data.get("tags", [])
        context.labels = data.get("labels", [])
        context.custom_properties = data.get("custom_properties", {})
        context.permissions = data.get("permissions", {})
        context.sharing = data.get("sharing", {})
        context.agents = data.get("agents", [])
        context.tasks = data.get("tasks", [])
        context.services = data.get("services", [])
        context.knowledge = data.get("knowledge", [])
        context.architecture = data.get("architecture")
        context.security = data.get("security")
        context.performance = data.get("performance")
        return context


@dataclass
class ContextGraph:
    contexts: Dict[str, Context] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)

    def add_context(self, context: Context) -> str:
        self.contexts[context.id] = context
        return context.id

    def add_relationship(self, rel: Dict[str, Any]) -> str:
        self.relationships.append(rel)
        return rel["id"]

    def get_context(self, context_id: str) -> Optional[Context]:
        return self.contexts.get(context_id)

    def get_contexts_by_type(self, context_type: ContextType) -> List[Context]:
        return [c for c in self.contexts.values() if c.metadata.type == context_type]

    def get_contexts_by_status(self, status: ContextStatus) -> List[Context]:
        return [c for c in self.contexts.values() if c.metadata.status == status]

    def get_related_contexts(self, context_id: str) -> List[Context]:
        context = self.get_context(context_id)
        if not context:
            return []

        related = []
        for rel_id in context.related_context_ids:
            rel_context = self.get_context(rel_id)
            if rel_context:
                related.append(rel_context)

        return related

    def merge(self, other: "ContextGraph") -> None:
        self.contexts.update(other.contexts)
        self.relationships.extend(other.relationships)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contexts": {cid: c.to_dict() for cid, c in self.contexts.items()},
            "relationships": self.relationships,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextGraph":
        graph = cls()
        for cid, cdata in data.get("contexts", {}).items():
            graph.contexts[cid] = Context.from_dict(cdata)
        graph.relationships = data.get("relationships", [])
        return graph
