from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from gpt_computer.repository_intelligence.models import SemanticGraph


@dataclass
class KnowledgeGraph:
    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    embeddings: Dict[str, List[float]] = field(default_factory=dict)

    def add_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> None:
        self.entities[entity_id] = entity_data

    def add_relationship(self, relationship: Dict[str, Any]) -> None:
        self.relationships.append(relationship)

    def add_embedding(self, entity_id: str, embedding: List[float]) -> None:
        self.embeddings[entity_id] = embedding

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        return [e for e in self.entities.values() if e.get("type") == entity_type]

    def get_related_entities(
        self, entity_id: str, relationship_type: Optional[str] = None
    ) -> List[str]:
        related = []
        for rel in self.relationships:
            if rel.get("source") == entity_id:
                target = rel.get("target")
                if not relationship_type or rel.get("type") == relationship_type:
                    related.append(target)
            elif rel.get("target") == entity_id:
                source = rel.get("source")
                if not relationship_type or rel.get("type") == relationship_type:
                    related.append(source)
        return related

    def search(self, query: str, threshold: float = 0.5) -> List[Dict[str, Any]]:
        results = []
        for entity_id, entity in self.entities.items():
            if entity.get("name", "").lower() == query.lower():
                results.append(entity)
            elif entity.get("description", "").lower().find(query.lower()) != -1:
                results.append(entity)

        return results

    def from_semantic_graph(
        self,
        semantic_graph: SemanticGraph,
        embedding_model: Optional[Any] = None,
    ) -> "KnowledgeGraph":
        kg = KnowledgeGraph()

        for node_id, node in semantic_graph.nodes.items():
            entity = {
                "id": node_id,
                "name": node.name,
                "type": node.node_type.value,
                "file_path": node.file_path,
                "qualified_name": node.qualified_name,
                "line_start": node.line_start,
                "line_end": node.line_end,
                "complexity": node.complexity,
                "docstring": node.docstring,
                "signature": node.signature,
                "return_type": node.return_type,
            }

            if embedding_model:
                text = f"{node.name} {node.docstring} {node.signature}"
                embedding = embedding_model.encode(text)
                kg.add_embedding(node_id, embedding)

            kg.add_entity(node_id, entity)

        for edge in semantic_graph.edges:
            source_node = semantic_graph.get_node(edge.source_id)
            target_node = semantic_graph.get_node(edge.target_id)

            if source_node and target_node:
                relationship = {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.edge_type.value,
                    "weight": edge.weight,
                    "metadata": edge.metadata,
                }
                kg.add_relationship(relationship)

        return kg

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": self.entities,
            "relationships": self.relationships,
            "embeddings": self.embeddings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        kg = cls()
        kg.entities = data.get("entities", {})
        kg.relationships = data.get("relationships", [])
        kg.embeddings = data.get("embeddings", {})
        return kg
