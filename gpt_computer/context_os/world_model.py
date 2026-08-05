import uuid

from datetime import datetime
from typing import Any, Dict, List, Optional

from gpt_computer.repository_intelligence.knowledge_graph import KnowledgeGraph


class Entity:
    def __init__(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = entity_id
        self.name = name
        self.type = entity_type
        self.description = description
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.relationships: List[Dict[str, Any]] = []

    def add_relationship(
        self,
        target_id: str,
        relationship_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
        relationship = {
            "id": rel_id,
            "source_id": self.id,
            "target_id": target_id,
            "type": relationship_type,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }

        self.relationships.append(relationship)
        return rel_id

    def remove_relationship(self, rel_id: str) -> bool:
        for i, rel in enumerate(self.relationships):
            if rel["id"] == rel_id:
                del self.relationships[i]
                return True
        return False

    def get_relationships(
        self, relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if relationship_type:
            return [
                rel for rel in self.relationships if rel["type"] == relationship_type
            ]
        return self.relationships.copy()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "relationships": self.relationships,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            entity_type=data["type"],
            description=data["description"],
            metadata=data.get("metadata", {}),
        )


class RepositoryEntity(Entity):
    def __init__(
        self,
        entity_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
        language: Optional[str] = None,
        stars: Optional[int] = None,
        forks: Optional[int] = None,
        issues: Optional[int] = None,
        pulls: Optional[int] = None,
    ):
        super().__init__(entity_id, name, "repository", description, metadata)
        self.url = url
        self.language = language
        self.stars = stars
        self.forks = forks
        self.issues = issues
        self.pulls = pulls

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "url": self.url,
                "language": self.language,
                "stars": self.stars,
                "forks": self.forks,
                "issues": self.issues,
                "pulls": self.pulls,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryEntity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            url=data.get("url"),
            language=data.get("language"),
            stars=data.get("stars"),
            forks=data.get("forks"),
            issues=data.get("issues"),
            pulls=data.get("pulls"),
        )


class PersonEntity(Entity):
    def __init__(
        self,
        entity_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        email: Optional[str] = None,
        location: Optional[str] = None,
        bio: Optional[str] = None,
    ):
        super().__init__(entity_id, name, "person", description, metadata)
        self.email = email
        self.location = location
        self.bio = bio

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "email": self.email,
                "location": self.location,
                "bio": self.bio,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonEntity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            email=data.get("email"),
            location=data.get("location"),
            bio=data.get("bio"),
        )


class TaskEntity(Entity):
    def __init__(
        self,
        entity_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        deadline: Optional[datetime] = None,
        assignee: Optional[str] = None,
    ):
        super().__init__(entity_id, name, "task", description, metadata)
        self.status = status
        self.priority = priority
        self.deadline = deadline
        self.assignee = assignee

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        result = {
            "status": self.status,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "assignee": self.assignee,
        }
        data.update(result)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskEntity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            status=data.get("status"),
            priority=data.get("priority"),
            deadline=datetime.fromisoformat(data["deadline"])
            if data.get("deadline")
            else None,
            assignee=data.get("assignee"),
        )


class DocumentEntity(Entity):
    def __init__(
        self,
        entity_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        file_type: Optional[str] = None,
        size: Optional[int] = None,
    ):
        super().__init__(entity_id, name, "document", description, metadata)
        self.file_path = file_path
        self.file_type = file_type
        self.size = size

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "file_path": self.file_path,
                "file_type": self.file_type,
                "size": self.size,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentEntity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            file_path=data.get("file_path"),
            file_type=data.get("file_type"),
            size=data.get("size"),
        )


class ServiceEntity(Entity):
    def __init__(
        self,
        entity_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        port: Optional[int] = None,
    ):
        super().__init__(entity_id, name, "service", description, metadata)
        self.endpoint = endpoint
        self.method = method
        self.port = port

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "endpoint": self.endpoint,
                "method": self.method,
                "port": self.port,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceEntity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            endpoint=data.get("endpoint"),
            method=data.get("method"),
            port=data.get("port"),
        )


class KnowledgeEntity(Entity):
    def __init__(
        self,
        entity_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        knowledge_type: Optional[str] = None,
        source: Optional[str] = None,
        confidence: Optional[float] = None,
    ):
        super().__init__(entity_id, name, "knowledge", description, metadata)
        self.knowledge_type = knowledge_type
        self.source = source
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "knowledge_type": self.knowledge_type,
                "source": self.source,
                "confidence": self.confidence,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEntity":
        return cls(
            entity_id=data["id"],
            name=data["name"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            knowledge_type=data.get("knowledge_type"),
            source=data.get("source"),
            confidence=data.get("confidence"),
        )


class WorldModel:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.knowledge_graph = KnowledgeGraph()
        self.entity_types = {
            "repository": RepositoryEntity,
            "person": PersonEntity,
            "task": TaskEntity,
            "document": DocumentEntity,
            "service": ServiceEntity,
            "knowledge": KnowledgeEntity,
        }

    def register_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        if entity_type not in self.entity_types:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        entity_class = self.entity_types[entity_type]
        entity = entity_class(entity_id, name, description, metadata, **kwargs)
        self.entities[entity_id] = entity
        self.knowledge_graph.add_entity(entity_id, entity.to_dict())
        return entity_id

    def unregister_entity(self, entity_id: str) -> bool:
        if entity_id in self.entities:
            del self.entities[entity_id]
            self.knowledge_graph.entities.pop(entity_id, None)
            return True
        return False

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        return [
            entity
            for entity in self.entities.values()
            if isinstance(entity, self.entity_types[entity_type])
        ]

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        source = self.entities.get(source_id)
        target = self.entities.get(target_id)

        if not source or not target:
            raise ValueError(
                f"Source or target entity not found: {source_id}, {target_id}"
            )

        rel_id = source.add_relationship(target_id, relationship_type, metadata)
        self.knowledge_graph.add_relationship(
            {
                "source": source_id,
                "target": target_id,
                "type": relationship_type,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
            }
        )

        return rel_id

    def remove_relationship(
        self, source_id: str, target_id: str, relationship_type: str
    ) -> bool:
        source = self.entities.get(source_id)
        if not source:
            return False

        relationships = source.get_relationships(relationship_type)
        if not relationships:
            return False

        rel_id = relationships[0]["id"]
        source.remove_relationship(rel_id)

        # Remove from knowledge graph
        self.knowledge_graph.relationships = [
            rel
            for rel in self.knowledge_graph.relationships
            if not (
                rel["source"] == source_id
                and rel["target"] == target_id
                and rel["type"] == relationship_type
            )
        ]

        return True

    def get_entity_relationships(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        entity = self.entities.get(entity_id)
        if not entity:
            return []

        return entity.get_relationships(relationship_type)

    def get_related_entities(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
    ) -> List[str]:
        entity = self.entities.get(entity_id)
        if not entity:
            return []

        relationships = entity.get_relationships(relationship_type)
        return [rel["target"] for rel in relationships]

    def search_entities(
        self, query: str, entity_type: Optional[str] = None
    ) -> List[Entity]:
        results = []
        query_lower = query.lower()

        for entity in self.entities.values():
            if entity_type and not isinstance(entity, self.entity_types[entity_type]):
                continue

            if (
                query_lower in entity.name.lower()
                or query_lower in entity.description.lower()
                or any(
                    query_lower in str(value).lower()
                    for key, value in entity.metadata.items()
                )
            ):
                results.append(entity)

        return results

    def get_entity_graph(self) -> Dict[str, Any]:
        return {
            "entities": {
                entity_id: entity.to_dict()
                for entity_id, entity in self.entities.items()
            },
            "relationships": self.knowledge_graph.relationships,
        }

    def import_entity_graph(self, entity_graph: Dict[str, Any]) -> None:
        # Import entities
        for entity_id, entity_data in entity_graph.get("entities", {}).items():
            entity_type = entity_data.get("type")
            if entity_type in self.entity_types:
                entity_class = self.entity_types[entity_type]
                entity = entity_class.from_dict(entity_data)
                self.entities[entity_id] = entity
                self.knowledge_graph.add_entity(entity_id, entity.to_dict())

        # Import relationships
        self.knowledge_graph.relationships = entity_graph.get("relationships", [])

    def export_entity_graph(self) -> Dict[str, Any]:
        return {
            "entities": {
                entity_id: entity.to_dict()
                for entity_id, entity in self.entities.items()
            },
            "relationships": self.knowledge_graph.relationships,
        }

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "total_entities": len(self.entities),
            "entity_types": list(self.entity_types.keys()),
            "total_relationships": len(self.knowledge_graph.relationships),
            "entities_by_type": {
                entity_type: len(
                    [
                        e
                        for e in self.entities.values()
                        if isinstance(e, self.entity_types[entity_type])
                    ]
                )
                for entity_type in self.entity_types
            },
        }

    def sync_with_semantic_graph(self, semantic_graph) -> None:
        # Sync with semantic graph from repository intelligence
        for node in semantic_graph.nodes.values():
            entity_type = node.node_type.value
            if entity_type in self.entity_types:
                entity_id = f"node_{node.id}"
                metadata = {
                    "semantic_node_id": node.id,
                    "file_path": node.file_path,
                    "line_start": node.line_start,
                    "line_end": node.line_end,
                    "complexity": node.complexity,
                    "cyclomatic_complexity": node.cyclomatic_complexity,
                    "lines_of_code": node.lines_of_code,
                    "docstring": node.docstring,
                    "signature": node.signature,
                    "return_type": node.return_type,
                }

                self.register_entity(
                    entity_id=entity_id,
                    name=node.name,
                    entity_type=entity_type,
                    description=node.docstring or "",
                    metadata=metadata,
                )

        # Sync relationships
        for edge in semantic_graph.edges:
            source_entity_id = f"node_{edge.source_id}"
            target_entity_id = f"node_{edge.target_id}"

            self.add_relationship(
                source_id=source_entity_id,
                target_id=target_entity_id,
                relationship_type=edge.edge_type.value,
                metadata={"semantic_edge_id": edge.id},
            )
