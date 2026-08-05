from datetime import datetime
from typing import Any, Dict, List, Optional

from gpt_computer.context_os.models import (
    Context,
    ContextGraph,
    ContextMetadata,
    ContextState,
    ContextStatus,
    ContextType,
)


class ContextManager:
    def __init__(self):
        self.graph = ContextGraph()

    def create_context(
        self,
        name: str,
        description: str,
        context_type: ContextType,
        created_by: str,
        parent_context_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        context_metadata = ContextMetadata(
            name=name,
            description=description,
            type=context_type,
            created_by=created_by,
            **(metadata or {}),
        )

        context = Context(metadata=context_metadata)
        if parent_context_id:
            context.parent_context_id = parent_context_id
            parent = self.graph.get_context(parent_context_id)
            if parent:
                parent.child_context_ids.append(context.id)

        self.graph.add_context(context)
        return context.id

    def update_context(
        self,
        context_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ContextStatus] = None,
        metadata: Optional[Dict[str, Any]] = None,
        updated_by: str = "",
    ) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        if name:
            context.metadata.name = name
        if description:
            context.metadata.description = description
        if status:
            context.metadata.status = status
        if metadata:
            context.metadata.custom_properties.update(metadata)
        context.metadata.updated_at = datetime.now()
        context.metadata.last_modified_by = updated_by

        return True

    def delete_context(self, context_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        # Remove from parent's child contexts
        if context.parent_context_id:
            parent = self.graph.get_context(context.parent_context_id)
            if parent and context.id in parent.child_context_ids:
                parent.child_context_ids.remove(context.id)

        # Remove related contexts
        for related_id in context.related_context_ids:
            related = self.graph.get_context(related_id)
            if related:
                if context.id in related.related_context_ids:
                    related.related_context_ids.remove(context.id)

        # Remove from graph
        del self.graph.contexts[context_id]
        return True

    def get_context(self, context_id: str) -> Optional[Context]:
        return self.graph.get_context(context_id)

    def get_contexts(
        self,
        filter_type: Optional[ContextType] = None,
        filter_status: Optional[ContextStatus] = None,
    ) -> List[Context]:
        contexts = list(self.graph.contexts.values())

        if filter_type:
            contexts = [c for c in contexts if c.metadata.type == filter_type]

        if filter_status:
            contexts = [c for c in contexts if c.metadata.status == filter_status]

        return contexts

    def add_context_state(
        self,
        context_id: str,
        state_type: str,
        data: Dict[str, Any],
        created_by: str,
    ) -> str:
        context = self.graph.get_context(context_id)
        if not context:
            raise ValueError(f"Context not found: {context_id}")

        state = ContextState(
            context_id=context_id,
            state_type=state_type,
            data=data,
            created_by=created_by,
        )

        context.add_state(state)
        return state.id

    def update_context_state(
        self,
        context_id: str,
        state_id: str,
        data: Dict[str, Any],
        updated_by: str,
    ) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        return context.update_state(state_id, data, updated_by)

    def get_context_state(
        self, context_id: str, state_id: str
    ) -> Optional[ContextState]:
        context = self.graph.get_context(context_id)
        if not context:
            return None

        return context.get_state(state_id)

    def get_context_history(self, context_id: str) -> List[ContextState]:
        context = self.graph.get_context(context_id)
        if not context:
            return []

        return context.history

    def add_related_context(self, context_id: str, related_context_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        related = self.graph.get_context(related_context_id)
        if not related:
            return False

        context.add_related_context(related_context_id)
        related.add_related_context(context_id)
        return True

    def remove_related_context(self, context_id: str, related_context_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        related = self.graph.get_context(related_context_id)
        if not related:
            return False

        context.remove_related_context(related_context_id)
        related.remove_related_context(context_id)
        return True

    def add_agent_to_context(self, context_id: str, agent_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.add_agent(agent_id)
        return True

    def remove_agent_from_context(self, context_id: str, agent_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.remove_agent(agent_id)
        return True

    def add_task_to_context(self, context_id: str, task_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.add_task(task_id)
        return True

    def remove_task_from_context(self, context_id: str, task_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.remove_task(task_id)
        return True

    def add_service_to_context(self, context_id: str, service_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.add_service(service_id)
        return True

    def remove_service_from_context(self, context_id: str, service_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.remove_service(service_id)
        return True

    def add_knowledge_to_context(self, context_id: str, knowledge_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.add_knowledge(knowledge_id)
        return True

    def remove_knowledge_from_context(self, context_id: str, knowledge_id: str) -> bool:
        context = self.graph.get_context(context_id)
        if not context:
            return False

        context.remove_knowledge(knowledge_id)
        return True

    def get_contexts_by_agent(self, agent_id: str) -> List[Context]:
        return [c for c in self.graph.contexts.values() if agent_id in c.agents]

    def get_contexts_by_task(self, task_id: str) -> List[Context]:
        return [c for c in self.graph.contexts.values() if task_id in c.tasks]

    def get_contexts_by_service(self, service_id: str) -> List[Context]:
        return [c for c in self.graph.contexts.values() if service_id in c.services]

    def get_contexts_by_knowledge(self, knowledge_id: str) -> List[Context]:
        return [c for c in self.graph.contexts.values() if knowledge_id in c.knowledge]

    def export_context(self, context_id: str) -> Dict[str, Any]:
        context = self.graph.get_context(context_id)
        if not context:
            raise ValueError(f"Context not found: {context_id}")

        return context.to_dict()

    def import_context(self, context_data: Dict[str, Any]) -> str:
        context = Context.from_dict(context_data)
        self.graph.add_context(context)
        return context.id

    def get_context_graph(self) -> ContextGraph:
        return self.graph

    def search_contexts(self, query: str) -> List[Context]:
        results = []
        query_lower = query.lower()

        for context in self.graph.contexts.values():
            if (
                query_lower in context.metadata.name.lower()
                or query_lower in context.metadata.description.lower()
                or query_lower in context.metadata.type.value.lower()
            ):
                results.append(context)

        return results

    def get_context_tree(self, context_id: str) -> Dict[str, Any]:
        context = self.graph.get_context(context_id)
        if not context:
            return {}

        tree = {
            "id": context.id,
            "name": context.metadata.name,
            "type": context.metadata.type.value,
            "status": context.metadata.status.value,
            "children": [],
        }

        for child_id in context.child_context_ids:
            child = self.graph.get_context(child_id)
            if child:
                tree["children"].append(self.get_context_tree(child_id))

        return tree
