from __future__ import annotations

from gptc.locals.models import get_models

try:
    from gptc.locals.provider import LocalProvider

    has_requirements = True
except ImportError:
    has_requirements = False

from gpt_computer.ai.providers.base_provider import AbstractProvider, ProviderModelMixin
from gptc.errors import MissingRequirementsError
from gptc.typing import CreateResult, Messages


class Local(AbstractProvider, ProviderModelMixin):
    label = "GPT4All"
    working = has_requirements
    active_by_default = False
    supports_message_history = True
    supports_system_message = True
    supports_stream = True

    @classmethod
    def get_models(cls):
        if not cls.models:
            cls.models = list(get_models())
            cls.default_model = cls.models[0]
        return cls.models

    @classmethod
    def create_completion(
        cls, model: str, messages: Messages, stream: bool, **kwargs
    ) -> CreateResult:
        if not has_requirements:
            raise MissingRequirementsError(
                'Install "gpt4all" package | pip install -U gptc[local]'
            )
        return LocalProvider.create_completion(
            cls.get_model(model), messages, stream, **kwargs
        )
