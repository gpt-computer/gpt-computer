from __future__ import annotations

from gpt_computer.ai.providers.base_provider import (
    AsyncGeneratorProvider,
    AsyncProvider,
)
from gpt_computer.ai.providers.create_images import CreateImagesProvider
from gpt_computer.ai.providers.retry_provider import (
    IterListProvider,
    ProviderCircuitBreaker,
    RetryProvider,
    RotatedProvider,
)
from gpt_computer.ai.providers.types import BaseProvider, ProviderType
from gpt_computer.infrastructure import debug

__others__ = [
    "AnyProvider",
    "BaseProvider",
    "ProviderType",
    "RetryProvider",
    "IterListProvider",
    "RotatedProvider",
    "ProviderCircuitBreaker",
    "AsyncProvider",
    "AsyncGeneratorProvider",
    "CreateImagesProvider",
    "ProviderUtils",
    "ProviderLoader",
    "Custom",
    "debug",
    "__providers__",
    "__map__",
    "__path__",
]


class ProviderLoader:
    names = [
        "AIBadgr",
        "Anthropic",
        "Antigravity",
        "AgentTools",
        "Airforce",
        "BingCreateImages",
        "BraveSearch",
        "BlackForestLabs_Flux1Dev",
        "BlackForestLabs_Flux1KontextDev",
        "BlackboxPro",
        "CachedSearch",
        "Cerebras",
        "Claude",
        "Cloudflare",
        "Cohere",
        "CohereForAI_C4AI_Command",
        "Copilot",
        "CopilotAccount",
        "CopilotApp",
        "CopilotSession",
        "DeepInfra",
        "DeepSeek",
        "EdgeTTS",
        "ElevenLabs",
        "GPTCSpace",
        "GLM",
        "Gemini",
        "GeminiCLI",
        "GeminiPro",
        "GigaChat",
        "GithubCopilot",
        "GithubCopilotAPI",
        "GoogleAiMode",
        "GoogleSearch",
        "Grok",
        "Groq",
        "HailuoAI",
        "HuggingChat",
        "HuggingFace",
        "HuggingFaceMedia",
        "HuggingSpace",
        "LMArena",
        "Local",
        "MarkItDown",
        "MetaAI",
        "MetaAIAccount",
        "MicrosoftDesigner",
        "MiniMax",
        "Nvidia",
        "RelayRouter",
        "KiloCode",
        "LLM7",
        "Ollama",
        "OpenAIFM",
        "OpenCode",
        "OpenRouter",
        "OpenRouterFree",
        "OrcaRouter",
        "OpenaiAPI",
        "OpenaiAccount",
        "OpenaiChat",
        "ChatGPTLightweight",
        "OpenaiTemplate",
        "OperaAria",
        "Perplexity",
        "PerplexityApi",
        "PhindAi",
        "Pi",
        "Pollinations",
        "PollinationsAudio",
        "PollinationsImage",
        "Puter",
        "Qwen",
        "QwenCode",
        "Reka",
        "Replicate",
        "SearXNG",
        "StabilityAI_SD35Large",
        "TeachAnything",
        "ThebApi",
        "Together",
        "WhiteRabbitNeo",
        "You",
        "YouTube",
        "Yqcloud",
        "gTTS",
        "xAI",
    ]
    loaded = {}
    ignored = []

    @classmethod
    def from_name(cls, name: str) -> ProviderType:
        if name in cls.loaded:
            return cls.loaded[name]
        provider = cls._load(name)
        cls.loaded[name] = provider
        return provider

    @classmethod
    def _load(cls, name: str) -> ProviderType:
        debug.log(f"Loading provider: {name}")

        if name == "AnyProvider":
            from gpt_computer.ai.providers.any_provider import AnyProvider

            return AnyProvider
        elif name == "AIBadgr":
            from gptc.Provider.needs_auth.AIBadgr import AIBadgr

            return AIBadgr
        elif name == "Anthropic":
            from gptc.Provider.needs_auth.Anthropic import Anthropic

            return Anthropic
        elif name == "Antigravity":
            from gptc.Provider.needs_auth.Antigravity import Antigravity

            return Antigravity
        elif name == "Airforce" or name == "ApiAirforce":
            from gptc.Provider.needs_auth.Airforce import Airforce

            return Airforce
        elif name == "BingCreateImages":
            from gptc.Provider.needs_auth.BingCreateImages import BingCreateImages

            return BingCreateImages
        elif name == "BraveSearch":
            from gptc.Provider.BraveSearch import BraveSearch

            return BraveSearch
        elif name == "BlackForestLabs_Flux1Dev":
            from gptc.Provider.hf_space.BlackForestLabs_Flux1Dev import (
                BlackForestLabs_Flux1Dev,
            )

            return BlackForestLabs_Flux1Dev
        elif name == "BlackForestLabs_Flux1KontextDev":
            from gptc.Provider.hf_space.BlackForestLabs_Flux1KontextDev import (
                BlackForestLabs_Flux1KontextDev,
            )

            return BlackForestLabs_Flux1KontextDev
        elif name == "BlackboxPro":
            from gptc.Provider.needs_auth.BlackboxPro import BlackboxPro

            return BlackboxPro
        elif name == "CachedSearch":
            from gptc.Provider.search.CachedSearch import CachedSearch

            return CachedSearch
        elif name == "Cerebras":
            from gptc.Provider.needs_auth.Cerebras import Cerebras

            return Cerebras
        elif name == "Claude":
            from gptc.Provider.needs_auth.Claude import Claude

            return Claude
        elif name == "Cloudflare":
            from gptc.Provider.Cloudflare import Cloudflare

            return Cloudflare
        elif name == "Cohere":
            from gptc.Provider.needs_auth.Cohere import Cohere

            return Cohere
        elif name == "CohereForAI_C4AI_Command":
            from gptc.Provider.hf_space.CohereForAI_C4AI_Command import (
                CohereForAI_C4AI_Command,
            )

            return CohereForAI_C4AI_Command
        elif name == "Copilot":
            from gptc.Provider.Copilot import Copilot

            return Copilot
        elif name == "CopilotAccount":
            from gptc.Provider.needs_auth.CopilotAccount import CopilotAccount

            return CopilotAccount
        elif name == "CopilotApp":
            from gptc.Provider.CopilotApp import CopilotApp

            return CopilotApp
        elif name == "CopilotSession":
            from gptc.Provider.CopilotSession import CopilotSession

            return CopilotSession
        elif name == "Custom":
            from gptc.Provider.needs_auth.Custom import Custom

            return Custom
        elif name == "DeepInfra":
            from .DeepInfra import DeepInfra

            return DeepInfra
        elif name == "DeepSeek" or name == "DeepSeekAPI":
            from gptc.Provider.needs_auth.DeepSeek import DeepSeek

            return DeepSeek
        elif name == "Default":
            from gpt_computer.ai.providers.any_provider import DefaultProvider

            return DefaultProvider
        elif name == "EdgeTTS":
            from gptc.Provider.audio.EdgeTTS import EdgeTTS

            return EdgeTTS
        elif name == "ElevenLabs":
            from gptc.Provider.audio.ElevenLabs import ElevenLabs

            return ElevenLabs
        elif name == "GPTCSpace":
            from gpt_computer.ai.client.factory import AbstractClientFactory

            cls.loaded[name] = AbstractClientFactory.create_provider(None, "default")
            cls.loaded[name].__name__ = name
            cls.loaded[name].url = "https://gptc.dev"
            cls.loaded[name].active_by_default = True
            return cls.loaded[name]
        elif name == "GLM":
            from gptc.Provider.glm import GLM

            return GLM
        elif name == "Gemini":
            from gptc.Provider.needs_auth.Gemini import Gemini

            return Gemini
        elif name == "GeminiCLI":
            from gptc.Provider.needs_auth.GeminiCLI import GeminiCLI

            return GeminiCLI
        elif name == "GeminiPro":
            from gptc.Provider.needs_auth.GeminiPro import GeminiPro

            return GeminiPro
        elif name == "GigaChat":
            from gptc.Provider.needs_auth.GigaChat import GigaChat

            return GigaChat
        elif name == "GithubCopilot":
            from gptc.Provider.github.GithubCopilot import GithubCopilot

            return GithubCopilot
        elif name == "GithubCopilotAPI":
            from gptc.Provider.needs_auth.GithubCopilotAPI import GithubCopilotAPI

            return GithubCopilotAPI
        elif name == "GoogleAiMode":
            from gptc.Provider.search.GoogleAiMode import GoogleAiMode

            return GoogleAiMode
        elif name == "GoogleSearch":
            from gptc.Provider.search.GoogleSearch import GoogleSearch

            return GoogleSearch
        elif name == "Grok":
            from gptc.Provider.needs_auth.Grok import Grok

            return Grok
        elif name == "Groq":
            from gptc.Provider.needs_auth.Groq import Groq

            return Groq
        elif name == "HailuoAI":
            from gptc.Provider.needs_auth.mini_max.HailuoAI import HailuoAI

            return HailuoAI
        elif name == "HuggingChat":
            from gptc.Provider.needs_auth.hf.HuggingChat import HuggingChat

            return HuggingChat
        elif name == "HuggingFace" or name == "HuggingFaceAPI":
            from gptc.Provider.needs_auth.hf import HuggingFace

            return HuggingFace
        elif name == "HuggingFaceMedia":
            from gptc.Provider.needs_auth.hf.HuggingFaceMedia import HuggingFaceMedia

            return HuggingFaceMedia
        elif name == "HuggingSpace":
            from gptc.Provider.hf_space import HuggingSpace

            return HuggingSpace
        elif name == "LMArena":
            from gptc.Provider.needs_auth.LMArena import LMArena

            return LMArena
        elif name == "Local":
            from gptc.Provider.local import Local

            return Local
        elif name == "MarkItDown":
            from gptc.Provider.audio.MarkItDown import MarkItDown

            return MarkItDown
        elif name == "MetaAI":
            from gptc.Provider.needs_auth.MetaAI import MetaAI

            return MetaAI
        elif name == "MetaAIAccount":
            from gptc.Provider.needs_auth.MetaAIAccount import MetaAIAccount

            return MetaAIAccount
        elif name == "MicrosoftDesigner":
            from gptc.Provider.needs_auth.MicrosoftDesigner import MicrosoftDesigner

            return MicrosoftDesigner
        elif name == "MiniMax":
            from gptc.Provider.needs_auth.mini_max.MiniMax import MiniMax

            return MiniMax
        elif name == "Nvidia":
            from gptc.Provider.needs_auth.Nvidia import Nvidia

            return Nvidia
        elif name == "RelayRouter":
            from gpt_computer.ai.client.factory import AbstractClientFactory

            cls.loaded[name] = AbstractClientFactory.create_provider(
                None,
                "custom:srv_mt1wbaxgf9c946af0c58",
            )
            cls.loaded[name].__name__ = name
            cls.loaded[name].url = "https://relayrouter.org"
            cls.loaded[name].active_by_default = True
            return cls.loaded[name]
        elif name == "KiloCode":
            from gpt_computer.ai.client.factory import AbstractClientFactory

            cls.loaded[name] = AbstractClientFactory.create_provider(
                None, "https://api.kilo.ai/api/gateway"
            )
            cls.loaded[name].__name__ = name
            cls.loaded[name].url = "https://kilo.ai"
            cls.loaded[name].active_by_default = True
            cls.loaded[name].default_model = "kilo-auto/free"
            return cls.loaded[name]
        elif name == "LLM7":
            from gpt_computer.ai.client.factory import AbstractClientFactory

            cls.loaded[name] = AbstractClientFactory.create_provider(
                None, "https://api.llm7.io/v1"
            )
            cls.loaded[name].__name__ = name
            cls.loaded[name].url = "https://llm7.io"
            cls.loaded[name].active_by_default = True
            cls.loaded[name].default_model = "default"
            cls.loaded[name].models = ["default"]
            cls.loaded[name].add_user = False
            return cls.loaded[name]
        elif name == "Ollama":
            from gptc.Provider.local.Ollama import Ollama

            return Ollama
        elif name == "OpenAIFM":
            from gptc.Provider.audio.OpenAIFM import OpenAIFM

            return OpenAIFM
        elif name == "OpenCode":
            import time

            from gpt_computer.ai.client.factory import AbstractClientFactory

            cls.loaded[name] = AbstractClientFactory.create_provider(
                None, "https://opencode.ai/zen/v1"
            )
            cls.loaded[name].__name__ = name
            cls.loaded[name].url = "https://opencode.ai"
            cls.loaded[name].active_by_default = True
            cls.loaded[name].default_model = "big-pickle"
            cls.loaded[name].headers = {
                "Content-Type": "application/json",
                "User-Agent": "opencode/1.18.31 ai-sdk/provider-utils/4.0.23 runtime/bun/1.3.14",
                "x-session-affinity": f"ses_{int(time.time())}",
                "x-session-id": f"ses_{int(time.time())}",
            }
            return cls.loaded[name]

        elif name == "OpenRouter":
            from gptc.Provider.needs_auth.OpenRouter import OpenRouter

            return OpenRouter
        elif name == "OpenRouterFree":
            from gptc.Provider.needs_auth.OpenRouter import OpenRouterFree

            return OpenRouterFree
        elif name == "OrcaRouter":
            from gpt_computer.ai.client.factory import AbstractClientFactory

            cls.loaded[name] = AbstractClientFactory.create_provider(None, name.lower())
            cls.loaded[name].__name__ = name
            cls.loaded[name].url = "https://orcarouter.ai"
            cls.loaded[name].active_by_default = True
            cls.loaded[name].supports_native_tools = True
            return cls.loaded[name]
        elif name == "AgentTools":
            from gptc.Provider.AgentTools import AgentTools

            return AgentTools
        elif name == "OpenaiAPI":
            from gptc.Provider.needs_auth.OpenaiAPI import OpenaiAPI

            return OpenaiAPI
        elif name == "OpenaiAccount":
            from gptc.Provider.needs_auth.OpenaiAccount import OpenaiAccount

            return OpenaiAccount
        elif name == "OpenaiChat":
            from gptc.Provider.needs_auth.OpenaiChat import OpenaiChat

            return OpenaiChat
        elif name == "ChatGPTLightweight":
            from gptc.Provider.ChatGPTLightweight import ChatGPTLightweight

            return ChatGPTLightweight
        elif name == "OpenaiTemplate":
            from gptc.Provider.template.OpenaiTemplate import OpenaiTemplate

            return OpenaiTemplate
        elif name == "OperaAria":
            from gptc.Provider.OperaAria import OperaAria

            return OperaAria
        elif name == "Perplexity":
            from gptc.Provider.Perplexity import Perplexity

            return Perplexity
        elif name == "PerplexityApi":
            from gptc.Provider.needs_auth.PerplexityApi import PerplexityApi

            return PerplexityApi
        elif name == "PhindAi":
            from gptc.Provider.PhindAi import PhindAi

            return PhindAi
        elif name == "Pi":
            from gptc.Provider.needs_auth.Pi import Pi

            return Pi
        elif name == "Pollinations" or name == "PollinationsAI":
            from gptc.Provider.Pollinations import Pollinations

            return Pollinations
        elif name == "PollinationsAudio":
            from gptc.Provider.audio.PollinationsAudio import PollinationsAudio

            return PollinationsAudio
        elif name == "PollinationsImage":
            from gptc.Provider.PollinationsImage import PollinationsImage

            return PollinationsImage
        elif name == "Puter" or name == "PuterJS":
            from gptc.Provider.needs_auth.Puter import Puter

            return Puter
        elif name == "Qwen":
            from gptc.Provider.Qwen import Qwen

            return Qwen
        elif name == "QwenCode":
            from gptc.Provider.qwen.QwenCode import QwenCode

            return QwenCode
        elif name == "Reka":
            from gptc.Provider.needs_auth.Reka import Reka

            return Reka
        elif name == "Replicate":
            from gptc.Provider.needs_auth.Replicate import Replicate

            return Replicate
        elif name == "SearXNG":
            from gptc.Provider.search.SearXNG import SearXNG

            return SearXNG
        elif name == "StabilityAI_SD35Large":
            from gptc.Provider.hf_space.StabilityAI_SD35Large import (
                StabilityAI_SD35Large,
            )

            return StabilityAI_SD35Large
        elif name == "TeachAnything":
            from gptc.Provider.TeachAnything import TeachAnything

            return TeachAnything
        elif name == "ThebApi":
            from gptc.Provider.needs_auth.ThebApi import ThebApi

            return ThebApi
        elif name == "Together":
            from gptc.Provider.needs_auth.Together import Together

            return Together
        elif name == "WhiteRabbitNeo":
            from gptc.Provider.needs_auth.WhiteRabbitNeo import WhiteRabbitNeo

            return WhiteRabbitNeo
        elif name == "You":
            from gptc.Provider.needs_auth.You import You

            return You
        elif name == "YouTube":
            from gptc.Provider.search.YouTube import YouTube

            return YouTube
        elif name == "Yqcloud":
            from gptc.Provider.Yqcloud import Yqcloud

            return Yqcloud
        elif name == "gTTS":
            from gptc.Provider.audio.gTTS import gTTS

            return gTTS
        elif name == "xAI":
            from gptc.Provider.needs_auth.xAI import xAI

            return xAI
        else:
            raise ImportError(f"Provider '{name}' not found")


__all__ = __others__ + ProviderLoader.names


def __getattr__(name: str):
    if name == "__providers__":
        # Load all providers if specifically requested
        providers_list = []
        for provider_name in ProviderLoader.names:
            if provider_name in ProviderLoader.ignored:
                continue
            try:
                providers_list.append(ProviderLoader.from_name(provider_name))
            except ImportError:
                pass
        return providers_list
    if name in __others__:
        return globals()[name]
    try:
        return ProviderLoader.from_name(name)
    except ImportError as e:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") from e


def __dir__():
    return __all__


class _ConvertDict(dict):
    def __contains__(self, item):
        return item in ProviderLoader.names

    def __getitem__(self, item):
        try:
            return __getattr__(item)
        except AttributeError:
            raise KeyError(f"Provider '{item}' not found")

    def keys(self):
        return ProviderLoader.names

    def items(self):
        return [(k, self[k]) for k in ProviderLoader.names]

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default


__map__ = _ConvertDict()


class ProviderUtils:
    convert = __map__

    @classmethod
    def get_by_label(cls, label: str) -> ProviderType:
        if not label:
            raise ValueError("Label must be provided")

        # Check explicit map
        try:
            return ProviderLoader.from_name(label)
        except ImportError:
            pass

        # Fallback to search
        for provider_name in ProviderLoader.names:
            if provider_name.lower().startswith(label.lower()):
                try:
                    provider = ProviderLoader.from_name(provider_name)
                    if provider.working:
                        return provider
                except ImportError:
                    pass

        raise ValueError(f"Provider with label '{label}' not found")


import sys  # noqa: E402
import types  # noqa: E402


class LazyProviderModule(types.ModuleType):
    def __getattribute__(self, name):
        if name.startswith("__"):
            return super().__getattribute__(name)

        try:
            return __getattr__(name)
        except AttributeError:
            pass

        return super().__getattribute__(name)


sys.modules[__name__].__class__ = LazyProviderModule
